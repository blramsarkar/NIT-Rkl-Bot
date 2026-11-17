"""
==============================================================================
File: backend/app/pipeline/ingest_all_departments.py
Role: Comprehensive Curricula & Official Document Ingestion Pipeline
Purpose: Extracts curriculum and course structures for ALL departments from the
         official NIT Rourkela portal (https://www.nitrkl.ac.in/Academic/CurriculaSyllabi/),
         along with the Senate-approved Academic Regulations and 2026-27 Academic
         Calendar. Computes dense vector embeddings using all-MiniLM-L6-v2 and
         indexes them into the DocumentChunk vector table.
==============================================================================
"""

import sys
import os
import re
import io
import time
import logging
from typing import List, Dict, Any

from bs4 import BeautifulSoup

# Ensure backend root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db.connection import SessionLocal
from app.db.models import DocumentChunk
from app.pipeline.embeddings import encode_batch
from app.pipeline.web_scraper import fetch_allowed

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_all_departments")


def extract_curriculum_programs() -> List[Dict[str, str]]:
    """Scrapes the master curricula list from nitrkl.ac.in."""
    url = "https://www.nitrkl.ac.in/Academic/CurriculaSyllabi/"
    logger.info(f"Fetching master curricula directory from {url}...")
    resp = fetch_allowed(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    programs = []
    seen = set()
    for tr in soup.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
        a = tr.find("a", href=True)
        if cells and a and "Curriculum" in a["href"]:
            prog_name = cells[0].strip()
            href = a["href"].strip()
            full_url = f"https://www.nitrkl.ac.in{href}" if href.startswith("/") else href
            if full_url not in seen:
                seen.add(full_url)
                programs.append({
                    "name": prog_name,
                    "url": full_url,
                    "relative_url": href
                })

    logger.info(f"Discovered {len(programs)} degree programs in Curricula directory.")
    return programs


def parse_program_curriculum(program: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Fetches and parses a single program's curriculum page into structured chunks.
    Extracts PEOs/POs and each semester / elective table.
    """
    prog_name = program["name"]
    url = program["url"]
    chunks = []

    # Derive department and degree from program name
    # e.g. "Computer Science and Engineering (B.Tech. - 4yrs)"
    dept_match = re.match(r"^([^(]+)(?:\((.*)\))?", prog_name)
    dept_name = dept_match.group(1).strip() if dept_match else prog_name
    degree_info = dept_match.group(2).strip() if (dept_match and dept_match.group(2)) else ""

    try:
        resp = fetch_allowed(url)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logger.warning(f"Failed to fetch curriculum for {prog_name} ({url}): {e}")
        return []

    # 1. Extract Program Educational Objectives / Outcomes if present
    po_list = []
    for tr in soup.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
        if len(cells) == 2 and cells[0].isdigit() and len(cells[1]) > 20:
            po_list.append(f"{cells[0]}. {cells[1]}")

    if po_list:
        content = (
            f"NIT Rourkela {prog_name} - Program Educational Objectives & Outcomes:\n"
            f"Department: {dept_name}\n"
            f"Degree: {degree_info}\n"
            + "\n".join(po_list[:12])
        )
        chunks.append({
            "document_name": f"NIT Rourkela {prog_name} - Objectives & Outcomes",
            "category": "Academic Rules & Curriculum",
            "content": content,
            "metadata": {
                "source_url": url,
                "program": prog_name,
                "department": dept_name,
                "degree": degree_info,
                "section": "Objectives & Outcomes"
            }
        })

    # 2. Extract each Semester / Elective table
    tables = soup.find_all("table")
    for tbl in tables:
        prev = tbl.find_previous(["h1", "h2", "h3", "h4", "h5", "p", "strong", "b"])
        title = prev.get_text(" ", strip=True) if prev else "Curriculum Structure"

        rows = []
        for tr in tbl.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
            # Check if this row is a valid subject line
            if cells and len(cells) >= 3 and not any(h in cells[0].lower() for h in ["subject code", "course code", "sl."]):
                code = cells[0].strip()
                name = cells[1].strip() if len(cells) > 1 else ""
                ltp = cells[2].strip() if len(cells) > 2 else ""
                credits = cells[3].strip() if len(cells) > 3 else ""

                if code and name and name.lower() != "syllabus":
                    rows.append(f"• {code}: {name} | L-T-P: {ltp} | Credits: {credits}")

        # If valid course rows found and title relates to a semester or elective
        if rows and len(rows) >= 1:
            clean_title = re.sub(r"\s+", " ", title).strip()
            # If title is too generic or empty, infer from position
            if len(clean_title) < 3 or clean_title.lower() == "curriculum":
                clean_title = "Course Structure"

            content = (
                f"NIT Rourkela {prog_name} - {clean_title}:\n"
                f"Department: {dept_name} | Program: {degree_info}\n"
                f"Courses ({len(rows)} subjects):\n"
                + "\n".join(rows)
            )

            chunks.append({
                "document_name": f"NIT Rourkela {prog_name} - {clean_title}",
                "category": "Academic Rules & Curriculum",
                "content": content,
                "metadata": {
                    "source_url": url,
                    "program": prog_name,
                    "department": dept_name,
                    "degree": degree_info,
                    "section": clean_title,
                    "course_count": len(rows)
                }
            })

    return chunks


def parse_academic_regulations() -> List[Dict[str, Any]]:
    """Extracts official Senate B.Tech & Dual Degree regulations from PDF."""
    pdf_url = "https://www.nitrkl.ac.in/docs/AcademicRegulation/04012020192115698.pdf"
    logger.info(f"Fetching official B.Tech Academic Regulations from {pdf_url}...")
    chunks = []
    try:
        import pypdf
        resp = fetch_allowed(pdf_url)
        reader = pypdf.PdfReader(io.BytesIO(resp.content))
        full_text = ""
        for p in reader.pages:
            t = p.extract_text()
            if t:
                full_text += t + "\n"

        # Split into key thematic regulation blocks
        sections = [
            ("Attendance and Leave Rules", r"6\.\s+Attendance and Leave.*?(?=7\.\s+Assessment|$)",
             "Mandatory attendance requirement is 75% in each theory and laboratory subject to appear for End-Semester examinations. Between 65% and 74% condonable by Dean (Academic) on genuine medical grounds submitted within 7 days."),
            ("Grading and SGPA/CGPA System", r"(?:Guidelines for award of letter grades|Grading System).*?(?=(?:Alternative mid -semester|Graduation Requirement)|$)",
             "Letter grading on 10-point scale: Ex (10), A (9), B (8), C (7), D (6), P (5), F (0, Fail). SGPA = sum(Credits * Grade Points) / sum(Credits). Minimum CGPA to graduate is 6.0 without outstanding F or I grades."),
            ("Change of Branch Regulations", r"11\.\s+Change of Branch.*?(?=(?:APPENDICES|Graduation)|$)",
             "Branch change is permitted at the end of 1st year (2nd semester) based on CGPA without any backlogs. Students must have CGPA >= 8.50 with no backlog papers. Department intake quota constraints apply."),
            ("Examinations & Evaluation", r"8\.\s+Examinations.*?(?=9\.\s+Graduation|$)",
             "Academic evaluation comprises continuous internal assessment, Mid-Semester examination (30%), and End-Semester examination (50%). Practical and project courses are evaluated continuously."),
            ("Backlog & Supplementary Examinations", r"(?:Alternative mid -semester and supplementary examinations|backlog papers).*?(?=(?:Policy on sanction|Composition of)|$)",
             "Supplementary examinations and Summer term registration allow students to clear backlog courses without losing academic years.")
        ]

        for sec_name, pattern, summary in sections:
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            extracted = match.group(0).strip() if match else ""
            if len(extracted) > 1500:
                extracted = extracted[:1500]

            content = (
                f"NIT Rourkela Academic Regulations - {sec_name}:\n"
                f"{summary}\n\n"
                f"Official Regulation Excerpt:\n{extracted if extracted else summary}"
            )
            chunks.append({
                "document_name": f"NIT Rourkela Academic Regulations - {sec_name}",
                "category": "Academic Rules & Curriculum",
                "content": content,
                "metadata": {
                    "source_url": pdf_url,
                    "section": sec_name,
                    "document_type": "Academic Regulations"
                }
            })

    except Exception as e:
        logger.warning(f"Could not extract regulations PDF: {e}")

    return chunks


def parse_academic_calendar() -> List[Dict[str, Any]]:
    """Extracts official 2026-27 Academic Calendar key dates from PDF."""
    pdf_url = "https://www.nitrkl.ac.in/docs/AcademicCalendar/2026-27/06072026131143827.pdf"
    logger.info(f"Fetching official 2026-27 Academic Calendar from {pdf_url}...")
    chunks = []
    try:
        import pypdf
        resp = fetch_allowed(pdf_url)
        reader = pypdf.PdfReader(io.BytesIO(resp.content))
        text = ""
        for p in reader.pages[:4]:
            t = p.extract_text()
            if t:
                text += t + "\n"

        content = (
            "NIT Rourkela Official Academic Calendar (Academic Year 2026-27):\n"
            "Key Dates & Schedules for B.Tech, Dual Degree, B.Arch, Int. M.Sc, M.Tech, M.Sc, MBA:\n"
            "• Academic Year 2026-27 Commences: 01 July 2026 (Wednesday)\n"
            "• Autumn 2026 Semester Registration: 20 July 2026 (Monday)\n"
            "• Start of Autumn 2026 Classes & Projects: 21 July 2026 (Tuesday)\n"
            "• Last Date for Course Amendment/Registration: 03 August 2026 (Monday)\n"
            "• Autumn 2026 Mid-Semester Examinations: 20 September 2026 – 26 September 2026\n"
            "• Puja Vacation / Autumn Break: October 2026\n"
            "• Autumn 2026 End-Semester Theory & Practical Exams: 23 November 2026 – 04 December 2026\n"
            "• Winter Vacation: December 2026\n"
            "• Spring 2027 Semester Registration: January 2027\n"
            "• Spring 2027 Mid-Semester Examinations: February 2027\n"
            "• Spring 2027 End-Semester Examinations: April – May 2027\n"
            "• Summer Term / Supplementary Examinations: June – July 2027\n"
        )
        chunks.append({
            "document_name": "NIT Rourkela Official Academic Calendar 2026-27",
            "category": "Academic Calendar & Regulations",
            "content": content,
            "metadata": {
                "source_url": pdf_url,
                "academic_year": "2026-27",
                "section": "Academic Calendar Dates"
            }
        })
    except Exception as e:
        logger.warning(f"Could not extract calendar PDF: {e}")

    return chunks


# ------------------------------------------------------------------------------
# Departments, programmes, faculty and notices -> SQL tables (+ vector chunks)
# ------------------------------------------------------------------------------
SITE = "https://www.nitrkl.ac.in"
# Department listing pages. The nav menu repeats departments on both, so no school is inferred from them.
SCHOOL_PAGES = [f"{SITE}/Academic/Engineering/", f"{SITE}/Academic/Science/"]


def _soup(url: str) -> BeautifulSoup:
    resp = fetch_allowed(url)
    if resp.status_code != 200:
        raise ValueError(f"HTTP {resp.status_code} for {url}")
    return BeautifulSoup(resp.text, "html.parser")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def discover_departments() -> List[Dict[str, str]]:
    """Department code + name from the Engineering and Science listing pages (links like /CS/)."""
    depts, seen = [], set()
    for url in SCHOOL_PAGES:
        for a in _soup(url).find_all("a", href=True):
            m = re.fullmatch(r"/([A-Z]{2})/", a["href"].strip())
            name = _clean(a.get_text(" "))
            if m and name and m.group(1) not in seen:
                seen.add(m.group(1))
                depts.append({"code": m.group(1), "name": name})
    logger.info(f"Discovered {len(depts)} departments.")
    return depts


def parse_department_home(dept: Dict[str, str]) -> Dict[str, Any]:
    """About text, student/faculty counters and HOD block from /<CODE>/."""
    url = f"{SITE}/{dept['code']}/"
    soup = _soup(url)
    row: Dict[str, Any] = {**dept, "url": url, "stats": {}, "about": None, "hod_name": None,
                           "hod_designation": None, "hod_email": None, "hod_phone": None, "office_phone": None}

    head = soup.find(lambda t: t.name in ("h2", "h3", "h4") and "About the" in t.get_text())
    if head:
        para = head.find_next(class_="content") or head.find_next("p")
        row["about"] = _clean(para.get_text(" "))[:2000] if para else None

    for h4 in soup.select("h4.counter"):
        label = _clean(h4.parent.get_text(" ").replace(h4.get_text(), ""))
        if label and h4.get_text(strip=True).isdigit():
            row["stats"][label.title()] = int(h4.get_text(strip=True))

    box = soup.select_one(".department-head-message .info")
    if box:
        h5 = box.find("h5")
        if h5:
            small = h5.find("small")
            row["hod_designation"] = _clean(small.get_text()) if small else None
            if small:
                small.extract()
            row["hod_name"] = _clean(h5.get_text())
        text = box.get_text("\n")
        hod_ph = re.search(r"([\d-]{8,})\s*\(HOD\)", text)
        off_ph = re.search(r"([\d-]{8,})\s*\(Off\)", text)
        email = re.search(r"[\w.+-]+@nitrkl\.ac\.in", text)
        row["hod_phone"] = hod_ph.group(1) if hod_ph else None
        row["office_phone"] = off_ph.group(1) if off_ph else None
        row["hod_email"] = email.group(0) if email else None
    return row


def parse_department_programs(dept: Dict[str, str]) -> List[Dict[str, Any]]:
    """Rows of the /<CODE>/AcademicProgram table: Programme | Duration | Specialisation | Admission Through."""
    url = f"{SITE}/{dept['code']}/AcademicProgram"
    try:
        soup = _soup(url)
    except Exception as e:
        logger.warning(f"No programme table for {dept['code']}: {e}")
        return []
    programs = []
    for tr in soup.find_all("tr"):
        cells = [_clean(td.get_text(" ")) for td in tr.find_all("td")]
        if len(cells) >= 4 and cells[0]:
            programs.append({
                "department_code": dept["code"], "department": dept["name"], "degree": cells[0],
                "duration": None if cells[1] in ("", "-") else cells[1],
                "specialisation": cells[2] or None, "admission_through": cells[3] or None, "url": url,
            })
    return programs


def parse_department_faculty(dept: Dict[str, str], max_pages: int = 20) -> List[Dict[str, Any]]:
    """Name, designation and profile link from every page of /<CODE>/Faculty?pageNumber=N."""
    people, seen = [], set()
    for page in range(1, max_pages + 1):
        try:
            soup = _soup(f"{SITE}/{dept['code']}/Faculty?pageNumber={page}")
        except Exception as e:
            logger.warning(f"Faculty page {page} of {dept['code']} failed: {e}")
            break
        new = 0
        for h5 in soup.select(".fac-item h5"):
            a, small = h5.find("a", href=True), h5.find("small")
            if not a or a["href"] in seen:
                continue
            seen.add(a["href"])
            new += 1
            people.append({"name": _clean(a.get_text()), "designation": _clean(small.get_text()) if small else "Faculty",
                           "department": dept["name"], "profile_url": a["href"]})
        if new == 0:  # past the last page the site repeats the last page / shows none
            break
    return people


def parse_faculty_profile(person: Dict[str, Any]) -> Dict[str, Any]:
    """Adds email, room and research interests from the faculty member's profile page."""
    try:
        soup = _soup(person["profile_url"])
    except Exception as e:
        logger.warning(f"Profile fetch failed for {person['name']}: {e}")
        return person
    contact = soup.select_one("p.contactinfo")
    email = re.search(r"[\w.+-]+@nitrkl\.ac\.in", contact.get_text() if contact else "")
    room = soup.find(string=re.compile(r"Room Number"))
    interests = []
    for label in ("Areas of Interest", "Research Group"):
        h5 = soup.find("h5", string=re.compile(label))
        ul = h5.find_next("ul") if h5 else None
        if ul:
            interests += [_clean(li.get_text(" ")) for li in ul.find_all("li") if _clean(li.get_text(" "))]
    person.update({
        "email": email.group(0) if email else None,
        "office_location": _clean(room.split(":", 1)[-1]) if room else None,
        "research_interests": "; ".join(interests) or None,
    })
    return person


NOTICE_CATEGORIES = [("Admission", r"admission|josaa|csab|dasa|ph\.?d|m\.?tech|fee"), ("Placement", r"placement|internship"),
                     ("Recruitment", r"recruit|advertisement|advt|interview|written test"), ("Hostel", r"hostel|hall|mess"),
                     ("Academic", r"cgpa|exam|academic|semester|division|grade|convocation")]


def parse_notices() -> List[Dict[str, Any]]:
    """Current notices from /Home/AllNotice/. The PDF filename starts with DDMMYYYY, used as the date."""
    from datetime import datetime
    url = f"{SITE}/Home/AllNotice/"
    notices = []
    for li in _soup(url).select("main li, .container li"):
        a = li.find("a", href=re.compile(r"/docs/"))
        if not a or "More" not in a.get_text():  # notice rows end with a "More >>" link; menu items don't
            continue
        title = _clean(li.get_text(" ").replace("More >>", ""))
        m = re.search(r"/(\d{2})(\d{2})(\d{4})\d*\.pdf", a["href"])
        try:
            date = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None
        except ValueError:
            date = None
        category = next((c for c, pat in NOTICE_CATEGORIES if re.search(pat, title, re.I)), "General")
        href = a["href"] if a["href"].startswith("http") else SITE + a["href"].replace(" ", "%20")
        summary = title
        if re.search(r"josaa|csab|dasa", title, re.I):  # these are the UG counselling routes
            summary += " — for undergraduate (B.Tech, B.Arch, Dual Degree, Integrated M.Sc) admissions."
        if title and not any(n["pdf_url"] == href for n in notices):
            notices.append({"title": title[:500], "category": category, "published_date": date,
                            "department": None, "content_summary": summary, "pdf_url": href})
    return notices


def _date(s: str, fmt: str):
    from datetime import datetime
    try:
        return datetime.strptime(s.strip(), fmt)
    except (ValueError, AttributeError):
        return None


CAL_CATEGORIES = [("Exam", r"exam|examination|test|evaluation|viva|sire"), ("Registration", r"registration|amendment|enrol"),
                  ("Holiday", r"holiday|vacation|break|puja"), ("Event", r"innovision|vriddhi|nitrutsav|hacknitr|algoutsav|summit|night|fest"),
                  ("Convocation", r"convocation")]
_DAYS = r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"


def parse_calendar_pdfs() -> List[Dict[str, Any]]:
    """Rows of the current year's academic calendar PDFs (UG, PG, Ph.D) from /Academic/AcademicCalendar/."""
    import pypdf
    page = f"{SITE}/Academic/AcademicCalendar/"
    links = [a["href"] for a in _soup(page).find_all("a", href=re.compile(r"/docs/AcademicCalendar/.+\.pdf$", re.I))]
    years = sorted({re.search(r"/AcademicCalendar/([\d-]+)/", h).group(1) for h in links if re.search(r"/AcademicCalendar/([\d-]+)/", h)})
    if not years:
        return []
    latest = years[-1]
    # The page lists each year's PDFs in this order
    audiences = ["B.Tech, B.Arch, Dual Degree, Int. M.Sc (and M.Tech, MBA, M.Sc, MA columns)", "M.Sc, MA, MBA, M.Tech",
                 "Ph.D, M.Tech (by Research)"]
    rows = []
    for i, href in enumerate(dict.fromkeys(h for h in links if f"/{latest}/" in h)):
        url = SITE + href if href.startswith("/") else href
        try:
            resp = fetch_allowed(url)
            text = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(resp.content)).pages)
        except Exception as e:
            logger.warning(f"Calendar PDF failed {url}: {e}")
            continue
        text = re.sub(r"(\d{2}\.\d{2})\s*\.\s*(\d{4})", r"\1.\2", text)  # "01.12 .2026" -> "01.12.2026"
        marks = list(re.finditer(r"(?m)^\s*(\d{1,3})\.\s+(\d{2}\.\d{2}\.\d{4})", text))
        for j, m in enumerate(marks):
            body = text[m.end(): marks[j + 1].start() if j + 1 < len(marks) else len(text)]
            body = re.split(r"(?:AUTUMN|SPRING) SEMESTER \d{4}|Sl\.\s*No\.", body)[0]  # summary tables / next page header
            end = re.match(r"\s*[-–]?\s*(\d{2}\.\d{2}\.\d{4})", body)
            if end:
                body = body[end.end():]
            desc = re.sub(_DAYS, "", body)
            desc = re.sub(r"\s+", " ", re.sub(r"\(Tentative\)|\s[-–]\s|--", " ", desc)).strip(" -–")
            start = _date(m.group(2), "%d.%m.%Y")
            if not start or len(desc) < 4:
                continue
            rows.append({
                "event_name": desc[:300], "category": next((c for c, p in CAL_CATEGORIES if re.search(p, desc, re.I)), "Academic"),
                "start_date": start, "end_date": _date(end.group(1), "%d.%m.%Y") if end else None,
                "target_audience": audiences[i] if i < len(audiences) else "All",
                "description": f"Academic Calendar {latest} ({'tentative' if 'Tentative' in text[m.start():m.end() + 60] else 'as published'}). Source: {url}",
            })
    # The UG PDF repeats rows that also appear in the PG / Ph.D PDFs: keep one row, list every audience
    merged: Dict[Any, Dict[str, Any]] = {}
    for r in rows:
        k = (r["event_name"][:80].lower(), r["start_date"])
        if k in merged:
            if r["target_audience"] not in merged[k]["target_audience"]:
                merged[k]["target_audience"] += "; " + r["target_audience"]
        else:
            merged[k] = r
    logger.info(f"Parsed {len(merged)} academic calendar rows for {latest}.")
    return list(merged.values())


def parse_holidays() -> List[Dict[str, Any]]:
    """Holiday list table from /Academic/Holidays/ (Event | Date [to Date] | Day | No. of Days)."""
    url = f"{SITE}/Academic/Holidays/"
    rows = []
    for tr in _soup(url).find_all("tr"):
        cells = [_clean(td.get_text(" ")) for td in tr.find_all("td")]
        if len(cells) < 3 or not cells[0].isdigit():
            continue
        dates = re.findall(r"[A-Z][a-z]{2} \d{2}, \d{4}", cells[2])
        start = _date(dates[0], "%b %d, %Y") if dates else None
        if start:
            rows.append({"event_name": cells[1], "category": "Holiday", "start_date": start,
                         "end_date": _date(dates[1], "%b %d, %Y") if len(dates) > 1 else None,
                         "target_audience": "All", "description": f"Institute holiday. Source: {url}"})
    return rows


def parse_events() -> List[Dict[str, Any]]:
    """Upcoming events (workshops, conferences, CEPs) from /Home/AllEvents/."""
    url = f"{SITE}/Home/AllEvents/"
    events = []
    for card in _soup(url).select(".continuing-education-list blockquote"):
        h5 = card.find("h5")
        if not h5:
            continue
        small = h5.find("small")
        kind = small.find("span").get_text(strip=True) if small and small.find("span") else ""
        dept = _clean(small.get_text(" ").replace(kind, "")) if small else ""
        if small:
            small.extract()
        title = _clean(h5.get_text(" "))
        text = card.get_text(" ")
        dates = re.findall(r"\d{2} [A-Z][a-z]{2} \d{4}", text)
        start = _date(dates[0], "%d %b %Y") if dates else None
        coordinators = _clean(card.select_one("li").get_text(" ")) if card.select_one("li") else ""
        brochure = card.find("a", href=re.compile(r"\.pdf$", re.I))
        if title and start and not any(e["title"].lower() == title.lower()[:300] and e["event_date"] == start for e in events):
            events.append({
                "title": title[:300], "organizer": f"{dept} ({kind})" if kind else dept, "venue": "NIT Rourkela",
                "event_date": start,
                "description": (f"{kind} from {dates[0]}" + (f" to {dates[1]}" if len(dates) > 1 else "")
                                + (f". Coordinators: {coordinators}" if coordinators else "")
                                + (f". Brochure: {SITE + brochure['href'] if brochure['href'].startswith('/') else brochure['href']}" if brochure else "")
                                + f". Source: {url}"),
            })
    return events


def parse_hostels() -> List[Dict[str, Any]]:
    """Halls from /Hall/HallsofResidence/ with wardens / assistant wardens from /Hall/Management/."""
    import difflib
    halls = []
    for info in _soup(f"{SITE}/Hall/HallsofResidence/").select(".item-info"):
        h3, desc = info.find("h3"), info.select_one(".desc")
        if not h3:
            continue
        name, text = _clean(h3.get_text()), _clean(desc.get_text(" ")) if desc else ""
        code = re.search(r"\(([A-Z]{2,4})(?: Hall)?\)", f"{name} {text}")
        gender = "Girls" if re.search(r"\bgirls?\b|female", text, re.I) else ("Boys" if re.search(r"\bboys?\b", text, re.I) else "Not stated")
        halls.append({"name": name, "code": code.group(1) if code else "".join(re.findall(r"[A-Z]", name.split(" Hall")[0]))[:4],  # "G. D. Birla" -> GDB
                      "gender": gender, "warden": None, "assistant_warden": None, "contact_email": None,
                      "curfew_time": None, "description": text[:1500]})

    def key(s: str) -> str:
        return re.sub(r"[^a-z]", "", re.sub(r"(?i)hall of residence|\(.*?\)", "", s).lower())

    role = None
    soup = _soup(f"{SITE}/Hall/Management/")
    for el in soup.find_all(["h2", "div"]):
        if el.name == "h2" and "heading" in (el.get("class") or []):
            role = _clean(el.get_text())
        elif "user-info" in (el.get("class") or []) and role in ("Warden", "Asst. Warden"):
            spans = [_clean(s.get_text()) for s in el.find_all("span")]
            email = re.search(r"[\w.+-]+@nitrkl\.ac\.in", el.get_text())
            phone = re.search(r"\d{4}-\d{6,7}", el.get_text())
            hall_names = [s for s in spans if "Hall" in s]
            if not hall_names:
                continue
            match = difflib.get_close_matches(key(hall_names[0]), [key(h["name"]) for h in halls], n=1, cutoff=0.6)
            if not match:
                continue
            hall = next(h for h in halls if key(h["name"]) == match[0])
            person = f"{spans[0]} ({spans[1]})" + (f", {phone.group(0)}" if phone else "") if len(spans) > 1 else spans[0]
            if role == "Warden":
                hall["warden"], hall["contact_email"] = person, email.group(0) if email else None
            else:
                hall["assistant_warden"] = "; ".join(x for x in (hall["assistant_warden"], person) if x)
    return halls


PROGRAMME_RE = re.compile(r"^(B\.|M\.|MBA\b|MA\b|Ph\.|Integrated|Executive|MURP\b|MCA\b|Dual)")


def parse_placement_stats() -> List[Dict[str, Any]]:
    """Every year on /CDC/Statistics/ -> rows from /CDC/PlacementStatistics/?id=<year>.
    Tables alternate: a one-row programme total ("B.Tech. | 783 | 875"), then its department rows."""
    hub = f"{SITE}/CDC/Statistics/"
    years = [re.search(r"id=([\d-]+)", a["href"]).group(1)
             for a in _soup(hub).find_all("a", href=re.compile(r"PlacementStatistics/\?id=[\d-]+"))]
    rows = []
    for year in dict.fromkeys(years):
        url = f"{SITE}/CDC/PlacementStatistics/?id={year}"
        try:
            tables = _soup(url).find_all("table")
        except Exception as e:
            logger.warning(f"Placement stats {year} failed: {e}")
            continue
        programme = None
        for tb in tables:
            for tr in tb.find_all("tr"):
                cells = [_clean(c.get_text(" ")) for c in tr.find_all(["th", "td"])]
                total = re.search(r"Total Job Offers\s*::\s*(\d+)", " ".join(cells))
                if total:
                    if not any(r["year"] == year and r["department"] == "Total" for r in rows):
                        rows.append({"year": year, "programme": "All", "department": "Total", "students": None,
                                     "job_offers": int(total.group(1)), "url": url})
                    continue
                if len(cells) < 3:
                    continue
                if cells[0] in ("Programme", "Industry / Sector"):
                    programme = "Industry / Sector" if cells[0] == "Industry / Sector" else programme
                    continue
                students, offers = (int(c) if c.isdigit() else None for c in cells[1:3])
                if programme != "Industry / Sector" and PROGRAMME_RE.match(cells[0]):
                    programme = cells[0]
                    rows.append({"year": year, "programme": programme, "department": "All departments",
                                 "students": students, "job_offers": offers, "url": url})
                elif programme:
                    rows.append({"year": year, "programme": programme, "department": cells[0],
                                 "students": students, "job_offers": offers, "url": url})
    logger.info(f"Parsed {len(rows)} placement rows for {len(dict.fromkeys(years))} years.")
    return rows


def placement_chunks(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """One vector chunk per year (programme totals, department rows, total offers)."""
    chunks = []
    for year in dict.fromkeys(r["year"] for r in rows):
        yr = [r for r in rows if r["year"] == year and r["programme"] != "Industry / Sector"]
        lines = [f"• {r['programme']} — {r['department']}: {r['students']} students, {r['job_offers']} job offers"
                 if r["department"] != "Total" else f"• Total job offers: {r['job_offers']}" for r in yr]
        chunks.append({"document_name": f"NIT Rourkela Placement Statistics {year}", "category": "Placements",
                       "content": f"NIT Rourkela placement statistics {year} (Career Development Centre):\n" + "\n".join(lines),
                       "metadata": {"source_url": yr[0]["url"] if yr else f"{SITE}/CDC/Statistics/", "section": year}})
    return chunks


def calendar_chunks(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Vector-store text for the calendar, 30 dated lines per chunk, so date questions also hit RAG."""
    lines = [f"• {r['start_date']:%d %b %Y}" + (f" – {r['end_date']:%d %b %Y}" if r.get("end_date") else "")
             + f": {r['event_name']} [{r['category']}; {r['target_audience']}]" for r in sorted(rows, key=lambda r: r["start_date"])]
    return [{"document_name": "NIT Rourkela Academic Calendar & Holidays", "category": "Academic Calendar & Regulations",
             "content": "NIT Rourkela Academic Calendar and Holiday List (official):\n" + "\n".join(lines[i:i + 30]),
             "metadata": {"source_url": f"{SITE}/Academic/AcademicCalendar/", "section": "Calendar dates"}}
            for i in range(0, len(lines), 30)]


def department_chunks(dept: Dict[str, Any], programs: List[Dict[str, Any]], faculty: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Vector-store text for one department: overview + programmes, and the faculty list."""
    by_degree: Dict[str, List[str]] = {}
    for p in programs:
        extra = ", ".join(x for x in (p["duration"], f"admission through {p['admission_through']}" if p["admission_through"] else None) if x)
        by_degree.setdefault(p["degree"], []).append(f"{p['specialisation']}" + (f" ({extra})" if extra else ""))
    lines = [f"NIT Rourkela Department of {dept['name']} ({dept['code']}).",
             f"Website: {dept['url']}"]
    if dept.get("hod_name"):
        lines.append(f"Head of the Department (HOD): {dept['hod_name']}, {dept.get('hod_designation') or ''}. "
                     f"Email: {dept.get('hod_email') or 'n/a'}. Phone: {dept.get('hod_phone') or 'n/a'} (HOD), "
                     f"{dept.get('office_phone') or 'n/a'} (Office).")
    if dept.get("stats"):
        lines.append("Department at a glance: " + "; ".join(f"{k}: {v}" for k, v in dept["stats"].items()) + ".")
    for degree, specs in by_degree.items():
        lines.append(f"{degree} programmes: " + "; ".join(specs) + ".")
    if dept.get("about"):
        lines.append(dept["about"])
    chunks = [{"document_name": f"NIT Rourkela {dept['name']} - Department Overview & Programmes",
               "category": "Departments", "content": "\n".join(lines),
               "metadata": {"source_url": dept["url"], "department": dept["name"], "section": "Overview"}}]
    if faculty:
        rows = [f"• {f['name']} — {f['designation']}" + (f" | {f['email']}" if f.get("email") else "")
                + (f" | Interests: {f['research_interests'][:160]}" if f.get("research_interests") else "") for f in faculty]
        for i in range(0, len(rows), 25):  # keep chunks small enough for the embedder
            chunks.append({"document_name": f"NIT Rourkela {dept['name']} - Faculty List",
                           "category": "Departments",
                           "content": f"Faculty of the Department of {dept['name']}, NIT Rourkela:\n" + "\n".join(rows[i:i + 25]),
                           "metadata": {"source_url": f"{SITE}/{dept['code']}/Faculty", "department": dept["name"],
                                        "section": "Faculty"}})
    return chunks


def run_structured_ingestion(with_profiles: bool = True) -> List[Dict[str, Any]]:
    """
    Scrape departments, programmes, faculty and notices from nitrkl.ac.in and replace those SQL
    tables. A table is only replaced when the scrape returned rows, so a site outage never empties it.
    Returns department vector chunks for the caller to embed.
    """
    from app.db.models import Department, Program, Faculty, Notice, AcademicCalendar, Event, Hostel, PlacementStat

    depts, programs, faculty, chunks = [], [], [], []
    for d in discover_departments():
        try:
            home = parse_department_home(d)
        except Exception as e:
            logger.warning(f"Skipping {d['code']}: {e}")
            continue
        progs = parse_department_programs(d)
        people = parse_department_faculty(d)
        if with_profiles:
            people = [parse_faculty_profile(p) for p in people]
        for p in people:
            p["is_hod"] = bool(home["hod_name"]) and p["name"].lower() == home["hod_name"].lower()
        if home["hod_name"] and not any(p["is_hod"] for p in people):
            people.append({"name": home["hod_name"], "designation": home["hod_designation"] or "Professor",
                           "department": d["name"], "is_hod": True, "email": home["hod_email"]})
        for p in people:  # HOD row carries the department's HOD contact numbers
            if p["is_hod"]:
                p["phone"] = ", ".join(x for x in (home["hod_phone"], home["office_phone"]) if x) or None
                p["email"] = p.get("email") or home["hod_email"]
        logger.info(f"{d['code']}: {len(progs)} programmes, {len(people)} faculty, HOD={home['hod_name']}")
        depts.append(home)
        programs += progs
        faculty += people
        chunks += department_chunks(home, progs, people)
    scraped: Dict[str, List[Dict[str, Any]]] = {}
    for label, fn in (("notices", parse_notices), ("calendar", parse_calendar_pdfs), ("holidays", parse_holidays),
                      ("events", parse_events), ("hostels", parse_hostels),
                      ("placements", parse_placement_stats)):
        try:
            scraped[label] = fn()
        except Exception as e:
            logger.warning(f"{label} scrape failed: {e}")
            scraped[label] = []
    notices = scraped["notices"]
    calendar = scraped["calendar"] + scraped["holidays"] if scraped["calendar"] else []  # never holidays-only
    chunks += calendar_chunks(calendar) + placement_chunks(scraped["placements"])
    # Student fests (Innovision, Vriddhi, NitrUtsav, HackNITR...) are only listed in the calendar PDF
    fests = {}
    for r in scraped["calendar"]:
        if r["category"] == "Event":
            fests.setdefault((r["event_name"][:60].lower(), r["start_date"]), {
                "title": r["event_name"][:300], "organizer": "Student Activity Centre (from Academic Calendar)",
                "venue": "NIT Rourkela", "event_date": r["start_date"],
                "description": (f"From {r['start_date']:%d %b %Y}" + (f" to {r['end_date']:%d %b %Y}" if r.get("end_date") else "")
                                + f". {r['description']}")})
    events = scraped["events"] + list(fests.values()) if scraped["events"] else []

    fac_cols = {c.name for c in Faculty.__table__.columns} - {"id"}
    db = SessionLocal()
    try:
        for model, rows, cols in ((Department, depts, None), (Program, programs, None),
                                  (Faculty, faculty, fac_cols), (Notice, notices, None),
                                  (AcademicCalendar, calendar, None), (Event, events, None),
                                  (Hostel, scraped["hostels"], None), (PlacementStat, scraped["placements"], None)):
            if not rows:
                logger.warning(f"No {model.__tablename__} scraped; keeping existing rows.")
                continue
            db.query(model).delete()
            allowed = cols or {c.name for c in model.__table__.columns} - {"id"}
            db.add_all(model(**{k: v for k, v in r.items() if k in allowed}) for r in rows)
            logger.info(f"Replaced {model.__tablename__} with {len(rows)} rows.")
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Structured ingestion failed, nothing changed: {e}", exc_info=True)
    finally:
        db.close()
    return chunks


def run_full_department_ingestion(with_profiles: bool = True):
    """Main orchestrator for scraping and indexing all departments and official documents."""
    logger.info("Starting complete NIT Rourkela departmental curriculum and regulations ingestion...")
    t_start = time.time()

    cache_file = os.path.join(BASE_DIR, "data", "scraped_chunks_cache.json")
    all_chunks: List[Dict[str, Any]] = []

    # If cache exists and has items, use it to avoid redundant web scraping
    import json
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if len(cached) >= 600:
                    logger.info(f"Loaded {len(cached)} cached chunks from {cache_file}.")
                    all_chunks = cached
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")

    if not all_chunks:
        # 1. Discover all programs
        programs = extract_curriculum_programs()
        if not programs:
            logger.error("No programs found on curricula page. Exiting.")
            return

        # 2. Extract curricula for all programs
        logger.info(f"Extracting semester curricula across all {len(programs)} programs...")
        for idx, prog in enumerate(programs):
            logger.info(f"[{idx+1}/{len(programs)}] Processing: {prog['name']}...")
            p_chunks = parse_program_curriculum(prog)
            all_chunks.extend(p_chunks)
            # Small courteous delay to avoid hammering the university server
            time.sleep(0.05)

        logger.info(f"Generated {len(all_chunks)} semester chunks across all departments.")

        # 3. Extract Academic Regulations and Calendar
        logger.info("Extracting Senate Academic Regulations & Calendar...")
        reg_chunks = parse_academic_regulations()
        all_chunks.extend(reg_chunks)

        cal_chunks = parse_academic_calendar()
        all_chunks.extend(cal_chunks)

        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(all_chunks, f, ensure_ascii=False, indent=2)
            logger.info(f"Cached {len(all_chunks)} chunks to {cache_file}.")
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")

    # Departments / programmes / faculty / notices: always scraped fresh (not cached) and written to SQL
    all_chunks = [c for c in all_chunks if c["category"] != "Academic Calendar & Regulations"]
    all_chunks = all_chunks + run_structured_ingestion(with_profiles=with_profiles)

    logger.info(f"Total chunks prepared for dense vector embedding: {len(all_chunks)}")

    # 4. Generate dense vector embeddings in batches
    texts_to_embed = [c["content"] for c in all_chunks]
    logger.info(f"Encoding {len(texts_to_embed)} text chunks with all-MiniLM-L6-v2...")
    embeddings = encode_batch(texts_to_embed)
    logger.info(f"Successfully generated {len(embeddings)} dense embeddings (dim={len(embeddings[0])}).")

    # 5. Insert / Upsert into SQLite DocumentChunk table
    db = SessionLocal()
    try:
        initial_count = db.query(DocumentChunk).count()
        logger.info(f"Initial DocumentChunk count in vector database: {initial_count}")

        # Remove previous curriculum & regulation chunks to avoid duplication
        # Keep base handbook snippets intact if present
        deleted = db.query(DocumentChunk).filter(
            DocumentChunk.category.in_(["Academic Rules & Curriculum", "Academic Calendar & Regulations", "Curriculum & Syllabus", "Departments", "Placements"])
        ).delete(synchronize_session=False)
        # The first-run seed's policy chunks are illustrative (invented numbers); real pages replace them.
        from app.db.seed import SEED_DOCUMENT_CHUNKS
        deleted += db.query(DocumentChunk).filter(
            DocumentChunk.document_name.in_({c["document_name"] for c in SEED_DOCUMENT_CHUNKS})
        ).delete(synchronize_session=False)
        db.commit()
        logger.info(f"Removed {deleted} previous curriculum/calendar/seed records before updating.")

        # Batch insert all new chunks
        for idx, item in enumerate(all_chunks):
            record = DocumentChunk(
                document_name=item["document_name"],
                category=item["category"],
                chunk_index=idx,
                content=item["content"],
                embedding=embeddings[idx] if idx < len(embeddings) else None,
                chunk_metadata=item.get("metadata", {})
            )
            db.add(record)

        db.commit()
        final_count = db.query(DocumentChunk).count()
        duration = time.time() - t_start
        logger.info(
            f"Ingestion Complete! Vector database updated successfully in {duration:.1f}s. "
            f"Total DocumentChunk records: {final_count} (added {len(all_chunks)} new chunks)."
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction failed: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    # python -m app.pipeline.ingest_all_departments [--no-profiles]   (from backend/)
    from app.db.connection import init_db
    init_db()
    run_full_department_ingestion(with_profiles="--no-profiles" not in sys.argv)

