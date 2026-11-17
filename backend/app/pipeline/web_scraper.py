"""
==============================================================================
File: backend/app/pipeline/web_scraper.py
Role: Allowlisted web scraper (live fallback tool + scheduled ingestion)
Purpose: Fetches text from official nitrkl.ac.in pages only.
Security:
  - SSRF guard: scheme/host/port allowlist, no IP literals, every redirect hop
    re-checked, response size capped.
  - Prompt-injection hygiene: hidden elements (display:none, aria-hidden,
    hidden attr, HTML comments, scripts/styles) and invisible Unicode removed.
==============================================================================
"""

import logging
import re
import time
from typing import Any, Dict, List, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Comment

from app.config import settings
from app.security import is_url_allowed, sanitize_untrusted_text

logger = logging.getLogger("nitrkl_bot.pipeline.web_scraper")

try:
    import certifi
    SSL_VERIFY = certifi.where()
except Exception:
    SSL_VERIFY = True

USER_AGENT = "NITRKLBot/2.1 (+https://www.nitrkl.ac.in; institutional assistant)"
MAX_REDIRECTS = 3


def _normalise(search_path_or_url: str) -> str:
    s = (search_path_or_url or "").strip()
    if s.startswith(("http://", "https://")):
        return s
    return f"{settings.NITRKL_BASE_URL.rstrip('/')}/{s.lstrip('/')}"


def fetch_allowed(url: str) -> httpx.Response:
    """GET a URL, following redirects manually so every hop is allowlist-checked."""
    domains = settings.get_scrape_domains()
    current = url
    with httpx.Client(timeout=8.0, follow_redirects=False, headers={"User-Agent": USER_AGENT}, verify=SSL_VERIFY) as client:
        for _ in range(MAX_REDIRECTS + 1):
            if not is_url_allowed(current, domains):
                raise PermissionError(f"URL not on scraper allowlist: {current}")
            with client.stream("GET", current) as resp:
                if resp.is_redirect:
                    current = urljoin(current, resp.headers.get("location", ""))
                    continue
                body = b""
                for chunk in resp.iter_bytes():
                    body += chunk
                    if len(body) > settings.SCRAPE_MAX_BYTES:
                        raise ValueError("Response too large")
                clean_headers = {k: v for k, v in resp.headers.items() if k.lower() not in ("content-encoding", "content-length")}
                return httpx.Response(resp.status_code, headers=clean_headers, content=body,
                                      request=resp.request)
    raise ValueError("Too many redirects")


def extract_visible_text(html: str, max_lines: int = 200) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for el in soup(["script", "style", "noscript", "template", "iframe", "nav", "footer", "header", "form"]):
        el.decompose()
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    hidden = []
    for el in soup.find_all(True):
        style = (el.get("style") or "").replace(" ", "").lower()
        if (
            el.has_attr("hidden")
            or el.get("aria-hidden") == "true"
            or "display:none" in style
            or "visibility:hidden" in style
            or "font-size:0" in style
        ):
            hidden.append(el)
    for el in hidden:
        if el.parent is not None:  # skip children of an already-removed element
            el.extract()
    lines = []
    for node in soup.find_all(["h1", "h2", "h3", "h4", "h5", "p", "li", "tr", "a"]):
        if node.name == "tr":  # one line per table row, so short cells ("128") stay next to their label
            text = " | ".join(re.sub(r"\s+", " ", c.get_text(" ", strip=True)) for c in node.find_all(["th", "td"]))
            keep = len(text) > 3
        else:
            if node.find_parent("tr"):
                continue
            text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
            keep = len(text) > 20
        if keep and text not in lines:
            lines.append(text)
        if len(lines) >= max_lines:
            break
    return sanitize_untrusted_text("\n".join(lines))


# ------------------------------------------------------------------------------
# Site search: the site's own /Search returns HTTP 503, so we keep our own index
# of official pages (SiteMap + topic pages + every department's pages) and rank
# them against the question, then read the best pages and keep matching lines.
# ------------------------------------------------------------------------------
INDEX_TTL_SECONDS = 24 * 3600
_index: Dict[str, Any] = {"built_at": 0.0, "pages": []}

SEARCH_STOP = {
    "the", "and", "for", "what", "which", "who", "whom", "when", "where", "how", "are", "is", "was", "were", "can",
    "could", "does", "did", "tell", "about", "give", "show", "list", "please", "with", "from", "this", "that", "there",
    "any", "all", "get", "find", "nit", "nitr", "rourkela", "rkl", "institute", "national", "technology", "details",
    "information", "info", "you", "your", "know", "want", "need", "have", "has", "will", "should", "much", "many",
}
# Words people ask with -> words the site uses in titles/URLs
SYNONYMS = {"hostel": "hall", "hostels": "hall", "placement": "cdc", "placements": "cdc", "job": "career",
            "jobs": "career", "fees": "fee", "scholarship": "scholarships", "hod": "head", "syllabus": "curricula",
            "curriculum": "curricula", "exam": "examination", "stats": "statistics", "stat": "statistics", "timetable": "time table", "phone": "contact",
            "library": "library", "doctor": "health", "hospital": "health", "ragging": "antiragging"}


def _terms(query: str) -> List[str]:
    words = [w for w in re.findall(r"[a-z0-9.+-]+", (query or "").lower()) if len(w) > 1 and w not in SEARCH_STOP]
    out = []
    for w in words:
        w = w.strip(".+-")
        if len(w) > 1 and w not in out:
            out.append(w)
        if w in SYNONYMS and SYNONYMS[w] not in out:
            out.append(SYNONYMS[w])
    return out


def _has_word(word: str, text: str) -> bool:
    """Word-start match: 'placement' matches 'placements' but not 'displacement'."""
    return re.search(rf"(?<![a-z0-9]){re.escape(word)}", text) is not None


def site_index(force: bool = False) -> List[Tuple[str, str]]:
    """(title, url) pairs of official pages; rebuilt at most once a day."""
    if not force and _index["pages"] and time.time() - _index["built_at"] < INDEX_TTL_SECONDS:
        return _index["pages"]
    from app.pipeline import source_pages as sp

    base = settings.NITRKL_BASE_URL.rstrip("/")
    domains = settings.get_scrape_domains()
    pages: Dict[str, str] = {}
    sitemap_ok = False

    def add(title: str, url: str) -> None:
        url = urljoin(base + "/", (url or "").strip())
        if url.lower().endswith(".pdf") or not is_url_allowed(url, domains):
            return
        pages[url] = (pages.get(url, "") + " " + re.sub(r"\s+", " ", title or "")).strip()

    try:
        resp = fetch_allowed(f"{base}/Home/SiteMap/")
        if resp.status_code == 200:
            sitemap_ok = True
            for a in BeautifulSoup(resp.text, "html.parser").find_all("a", href=True):
                if not a["href"].startswith(("javascript", "#", "mailto")):
                    add(a.get_text(" ", strip=True), a["href"])
    except Exception as e:
        logger.warning(f"SiteMap fetch failed, using known pages only: {e}")

    for t in sp.TOPICS.values():  # topic keywords make "hostel", "fee" etc. findable
        add(f"{t['label']} {t['keywords'].replace('|', ' ')}", t["url"])
    try:
        from app.db.connection import SessionLocal
        from app.db.models import Department, Faculty
        db = SessionLocal()
        try:
            for f in db.query(Faculty).filter(Faculty.profile_url.isnot(None)).all():
                add(f"{f.name} {f.designation} {f.department} {f.research_interests or ''}", f.profile_url)
            for d in db.query(Department).all():
                for sub, label in (("", "department home hod head faculty count students"),
                                   ("About", "about vision mission"),
                                   ("AcademicProgram", "academic programmes programs btech mtech msc phd admission specialisation"),
                                   ("Faculty", "faculty professors list"), ("Laboratory", "laboratory labs facilities")):
                    add(f"{d.name} {d.code} {label}", f"/{d.code}/{sub}")
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Department pages not added to site index: {e}")

    result = [(title, url) for url, title in pages.items()]
    # Without the SiteMap the index is thin, so retry it after an hour instead of a day.
    _index.update(built_at=time.time() - (0 if sitemap_ok else INDEX_TTL_SECONDS - 3600), pages=result)
    return result


def search_site(query: str, max_pages: int = 3, max_lines: int = 12) -> Dict[str, Any]:
    """
    Answer a free-text question from the live website: rank indexed pages by the question's
    words, fetch the best few, and return the lines that mention those words.
    """
    terms = _terms(query)
    not_found = {"source_url": None, "status": "not_found", "query": query,
                 "content": "No matching content was found on the official NIT Rourkela website."}
    if not terms:
        return not_found

    ranked = []
    for title, url in site_index():
        t, u = title.lower(), url.lower()
        score = sum(2 for w in terms if _has_word(w, t)) + sum(1 for w in terms if w in u)
        if score:
            ranked.append((score, url))
    ranked.sort(key=lambda x: -x[0])
    candidates = [u for _, u in ranked[:max_pages]]

    found = []  # (score, page_rank, line, url)
    queue = [(rank, url, None) for rank, url in enumerate(candidates)]  # (rank, url, url_score for followed links)
    visited, followed = set(), 0
    while queue:
        rank, url, url_score = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = fetch_allowed(url)
            if resp.status_code != 200 or "html" not in resp.headers.get("content-type", "html"):
                continue
        except Exception as e:
            logger.info(f"search_site: skip {url}: {e}")
            continue
        lines = extract_visible_text(resp.text, max_lines=400).split("\n")
        matched = 0
        for line in lines:
            low = line.lower()
            hits = sum(1 for w in terms if _has_word(w, low)) / len(terms)
            if url_score is not None:  # a followed detail page: its rows are relevant even without the words
                hits = max(hits, url_score)
            if hits:
                matched += 1
                found.append((hits, rank, line, url))
        # Hub page (e.g. /CDC/Statistics/ only lists years): follow its best-matching links one level deeper
        if matched < 3 and url_score is None and followed < 2:
            links = []
            for a in BeautifulSoup(resp.text, "html.parser").find_all("a", href=True):
                child = urljoin(url, a["href"])
                low = (child + " " + a.get_text(" ", strip=True)).lower()
                score = sum(1 for w in terms if w in low) / len(terms)
                if score >= 0.5 and child not in visited and child.rstrip("/") != url.rstrip("/") \
                        and is_url_allowed(child, settings.get_scrape_domains()) and not child.lower().endswith(".pdf"):
                    links.append((score, child))
            links.sort(key=lambda x: -x[0])  # stable: page order (newest first) breaks ties
            for score, child in links[:1]:
                queue.insert(0, (rank + 0.5, child, score))
                followed += 1
    if not found:
        return {**not_found, "pages_checked": candidates}

    found.sort(key=lambda x: (-x[0], x[1]))
    best_url = found[0][3]
    lines = [f[2] for f in found if f[3] == best_url][:max_lines]
    lines += [f[2] for f in found if f[3] != best_url][:max(0, max_lines - len(lines)) // 2]
    return {"source_url": best_url, "status": "success", "query": query, "pages_checked": candidates,
            "match_score": round(found[0][0], 2), "content": "\n".join(lines)}


def _looks_like_page(s: str) -> bool:
    return s.startswith(("http://", "https://", "/")) or bool(re.fullmatch(r"[\w\-./~]+/[\w\-./~]*", s))


def scrape_nitrkl_live(search_path_or_url: str, max_lines: int = 15) -> Dict[str, Any]:
    """
    Live fallback tool used by the LLM router. Accepts a URL, a site path, or a plain
    question/keywords (searched across the official site). Only allowlisted domains are fetched.
    """
    s = (search_path_or_url or "").strip()
    if not _looks_like_page(s):
        return search_site(s, max_lines=max_lines)
    target_url = _normalise(s)
    if not is_url_allowed(target_url, settings.get_scrape_domains()):
        logger.warning(f"Blocked scrape of non-allowlisted URL: {target_url!r}")
        return {"source_url": None, "status": "blocked",
                "content": "That address is not an official NIT Rourkela page, so it was not fetched."}

    logger.info(f"Live fallback scrape: {target_url}")
    try:
        resp = fetch_allowed(target_url)
        text = extract_visible_text(resp.text, max_lines=max_lines) if resp.status_code == 200 else ""
        if not text:  # wrong/moved path or empty page: search the site with the path's words instead
            words = " ".join(re.findall(r"[A-Za-z]{3,}", urlparse(target_url).path))
            result = search_site(words, max_lines=max_lines) if words else {"status": "not_found"}
            if result.get("status") == "success":
                return result
            return {"source_url": target_url, "status": "failed",
                    "content": f"The page returned HTTP {resp.status_code} and no matching page was found."}
        return {"source_url": target_url, "status": "success", "content": text}
    except PermissionError as e:
        logger.warning(str(e))
        return {"source_url": None, "status": "blocked",
                "content": "The page redirected outside the official site, so it was not fetched."}
    except Exception as e:
        logger.error(f"Live scraping failed for {target_url}: {e}")
        return {"source_url": target_url, "status": "error",
                "content": "The official page could not be reached right now."}
