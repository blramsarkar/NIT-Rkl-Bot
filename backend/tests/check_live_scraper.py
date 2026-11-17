"""
Self-check for the live scraper, department data and router (hits www.nitrkl.ac.in).
Run from backend/ after `python -m app.pipeline.ingest_all_departments`:
    python -m tests.check_live_scraper
"""

from app.pipeline.agent_router import route_and_answer_deterministic
from app.pipeline.structured_tools import get_departments, get_faculty, match_department
from app.pipeline.web_scraper import scrape_nitrkl_live

checks = []


def check(name, cond, detail=""):
    cond = bool(cond)
    checks.append(cond)
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -> {detail}"))


# Live scraper: question, keyword, path, wrong path, blocked domain
for q in ["how to apply for admission", "scholarships", "anti ragging"]:
    r = scrape_nitrkl_live(q)
    check(f"search '{q}'", r["status"] == "success" and "nitrkl.ac.in" in (r["source_url"] or ""), r)
r = scrape_nitrkl_live("/Academic/AcademicCalendar/")
check("fetch by path", r["status"] == "success", r)
r = scrape_nitrkl_live("/Placement")  # 404 on the site -> should recover via search
check("wrong path recovers", r["status"] == "success" and "/CDC/" in (r["source_url"] or ""), r)
r = scrape_nitrkl_live("https://example.com/")
check("external URL blocked", r["status"] == "blocked", r)

# Department matching and data
for text, code in [("cse", "CS"), ("hod of mechanical", "ME"), ("ECE labs", "EC"), ("maths", "MA"), ("tell me something", None)]:
    check(f"match_department('{text}')", match_department(text) == code, match_department(text))
cs = get_departments("CSE")
check("CSE has HOD", bool(cs and cs[0]["hod"]), cs[:1])
degrees = {p["degree"] for p in (cs[0]["programs"] if cs else [])}
check("CSE offers B.Tech and M.Tech", any("B.Tech" in d for d in degrees) and any("M.Tech" in d for d in degrees), degrees)
mtech = get_departments(degree="M.Tech")
check("several departments offer M.Tech", len(mtech) >= 5, len(mtech))
check("M.Tech filter excludes M.Tech.(R)", all("(R)" not in p["degree"] for d in mtech for p in d["programs"]))

# Faculty: by name, by research topic, HOD flag
f = get_faculty(name_or_keyword="Banshidhar Majhi")
check("faculty by name", any("Majhi" in x["name"] for x in f), f[:1])
f = get_faculty(name_or_keyword="image processing")
check("faculty by research topic", len(f) > 0 and all(x["research"] for x in f[:3]), f[:1])
f = get_faculty(department="CSE", designation="HOD")
check("HOD of CSE flagged", len(f) == 1 and f[0]["email"], f)

# Placement statistics: table data, and live scraper following the year list into the stats page
from app.pipeline.structured_tools import get_placement_stats
from app.pipeline.web_scraper import search_site
ps = get_placement_stats()
check("placement stats: latest year totals", ps.get("rows") and any(r["department"] == "Total" for r in ps["rows"]), ps)
ps = get_placement_stats(year="2023-24", department="CSE")
check("placement stats: CSE 2023-24", ps.get("year") == "2023-24" and ps.get("rows"), ps)
r = search_site("placement stats")
check("live scraper follows hub to stats page", "PlacementStatistics" in (r.get("source_url") or "") and "|" in r["content"], r)
r = route_and_answer_deterministic("placement stats")
check("router: placement stats from data", "get_placement_stats" in r["tools_used"], r["tools_used"])

# Router (no LLM): programmes, and live-site fallback
r = route_and_answer_deterministic("Which departments offer M.Tech?")
check("router: programmes via get_departments", "get_departments" in r["tools_used"], r["tools_used"])
r = route_and_answer_deterministic("anti ragging committee members")
check("router: live website fallback", "scrape_live_website" in r["tools_used"] or "search_docs" in r["tools_used"], r)

print(f"\n{sum(checks)}/{len(checks)} checks passed")
raise SystemExit(0 if all(checks) else 1)
