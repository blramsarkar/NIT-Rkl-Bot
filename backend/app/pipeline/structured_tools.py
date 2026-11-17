"""
==============================================================================
File: backend/app/pipeline/structured_tools.py
Role: Structured SQL Database Tools & LLM Tool Specifications (Groq & Anthropic)
Purpose: Provides parameterized query functions and formal JSON tool declarations
         for Groq (Llama 3 OpenAI-compatible function format) and Anthropic Claude
         to query notices, faculty directory, academic calendar events, campus fests,
         and halls of residence (hostels).
==============================================================================
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db.models import Notice, Faculty, AcademicCalendar, Event, Hostel, Department, Program, PlacementStat

logger = logging.getLogger("nitrkl_bot.pipeline.structured_tools")

STOP_WORDS = {"when", "are", "the", "and", "is", "for", "tell", "me", "about", "what", "which", "in", "of", "to", "at", "a", "an", "do", "how", "can"}


# ==============================================================================
# Base Tool Specifications
# ==============================================================================

STRUCTURED_TOOLS_DEFINITIONS = [
    {
        "name": "get_notices",
        "description": "Searches current NIT Rourkela official notices: admissions, recruitment, fee structure (UG and PG, with PDF links), academic circulars.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filter by category: 'Academic', 'Admission', 'Hostel', 'Placement', 'General'"
                },
                "since_days": {
                    "type": "integer",
                    "description": "Number of past days to include notices for (default 60 days)"
                },
                "keyword": {
                    "type": "string",
                    "description": "Optional search keyword in title or summary"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_academic_calendar",
        "description": "Queries the NIT Rourkela academic calendar for exam dates, registration deadlines, semester schedules, and holidays.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format"
                },
                "event_keyword": {
                    "type": "string",
                    "description": "Keyword for event (e.g., 'mid-sem', 'end-sem', 'registration', 'holiday', 'convocation')"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_events",
        "description": "Returns campus events, seminars, fests (Innovision, Vriddhi, Nitrutsav), workshops, and hackathons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "description": "Type of event: 'Fest', 'Seminar', 'Workshop', 'Conference', 'Cultural', 'Sports'"
                },
                "start_date": {
                    "type": "string",
                    "description": "Filter events starting after YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "Filter events ending before YYYY-MM-DD"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_faculty",
        "description": "Queries faculty directory entries, designations (e.g. Professor, HOD), departments, emails, phone numbers, and offices.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name (e.g., 'Computer Science and Engineering', 'Electrical Engineering', 'Mechanical Engineering')"
                },
                "designation": {
                    "type": "string",
                    "description": "Designation (e.g., 'Professor', 'HOD', 'Associate Professor', 'Director')"
                },
                "name_or_keyword": {
                    "type": "string",
                    "description": "Faculty name or research interest keyword"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_hostels",
        "description": "Queries NIT Rourkela Halls of Residence (Hostels), wardens, curfew timings, room allotment, and facilities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name_or_code": {
                    "type": "string",
                    "description": "Hostel name or code (e.g., 'MSS', 'VS', 'HB', 'CVR', 'KMS', 'DBA')"
                },
                "gender": {
                    "type": "string",
                    "description": "Filter by gender: 'Boys' or 'Girls'"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_departments",
        "description": "Department details from the official website: HOD name/email/phone, student and faculty counts, and the programmes offered (B.Tech, M.Tech, Dual Degree, Integrated M.Sc, M.Sc, Ph.D) with specialisations, duration and admission route (JEE Main, GATE, JAM...). Also answers 'which departments offer M.Tech in X'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name, short name or code (e.g. 'CSE', 'Electrical', 'ME', 'Mathematics'). Omit to list all departments."
                },
                "degree": {
                    "type": "string",
                    "description": "Filter programmes by degree, e.g. 'B.Tech', 'M.Tech', 'Dual Degree', 'M.Sc', 'Ph.D'"
                },
                "specialisation_keyword": {
                    "type": "string",
                    "description": "Find programmes whose specialisation contains this word (e.g. 'artificial intelligence', 'VLSI', 'power')"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_placement_stats",
        "description": "Official placement statistics (Career Development Centre) for 2017-18 to the latest year: students placed and job offers per programme (B.Tech, M.Tech, MBA, M.Sc...), per department, by recruiting sector, and total offers. Defaults to the latest year.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "string", "description": "Academic year like '2024-25'. Omit for the latest year."},
                "department": {"type": "string", "description": "Department name or short name (e.g. 'CSE', 'Mechanical')"},
                "programme": {"type": "string", "description": "Programme, e.g. 'B.Tech', 'M.Tech', 'MBA', 'M.Sc', 'Ph.D'"},
                "by_sector": {"type": "boolean", "description": "True to get job offers by industry sector"}
            },
            "required": []
        }
    },
    {
        "name": "search_docs",
        "description": "Performs RAG semantic vector search across official handbooks, regulations, hostel rules, fee waivers, and FAQs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query regarding rules, attendance criteria, hostel curfews, fee waivers, or degree requirements."
                },
                "source_section": {
                    "type": "string",
                    "description": "Optional category filter: 'Academic Rules', 'Hostel Rules', 'Fees & Scholarships', 'Admissions'"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of relevant text chunks to return (default 3)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "scrape_live_website",
        "description": "Live search of the official nitrkl.ac.in website. Pass either a page URL/path or the user's question in plain words; the tool finds the most relevant official pages and returns the matching text with its URL. Use when the other tools return nothing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "search_path_or_url": {
                    "type": "string",
                    "description": "The question or keywords (e.g. 'anti ragging committee contact'), or a nitrkl.ac.in URL/path."
                }
            },
            "required": ["search_path_or_url"]
        }
    }
]

# Export Anthropic Schema Format
structured_tools_list = STRUCTURED_TOOLS_DEFINITIONS


def _make_groq_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    import copy
    s = copy.deepcopy(schema)
    props = s.get("properties", {})
    req = set(s.get("required", []))
    for k, v in props.items():
        if k not in req and "type" in v:
            t = v["type"]
            if isinstance(t, str):
                v["type"] = [t, "null"]
    return s


# Export Groq / OpenAI Function Schema Format
groq_tools_list = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": _make_groq_schema(tool["input_schema"])
        }
    }
    for tool in STRUCTURED_TOOLS_DEFINITIONS
]


# ==============================================================================
# Parameterized Tool Execution Handlers
# ==============================================================================

def get_notices(category: Optional[str] = None, since_days: Optional[int] = 60, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns official notices from database with filtering and fallback mock records."""
    db: Session = SessionLocal()
    try:
        query = db.query(Notice)
        generic = {"notice", "notices", "latest", "recent", "new", "circular", "nit", "rourkela"}
        all_rows = query.order_by(Notice.published_date.desc()).all()
        # A guessed category ("Academic" for a fee notice filed under Admission) must not hide the match
        candidates = [all_rows]
        if category:
            candidates.insert(0, [n for n in all_rows if category.lower() in (n.category or "").lower()])
        results = []
        for rows in candidates:
            if keyword:  # rank instead of OR-matching single words like "2026"
                rows = _rank_rows(rows, keyword, lambda n: f"{n.title} {n.category} {n.content_summary or ''}", generic)
            if rows:
                results = rows[:6]
                break

        if results:
            return [
                {
                    "title": n.title,
                    "category": n.category,
                    "published_date": str(n.published_date.strftime("%Y-%m-%d")) if n.published_date else "",
                    "department": n.department or "General",
                    "summary": n.content_summary,
                    "url": n.pdf_url or "https://www.nitrkl.ac.in/Notices"
                }
                for n in results
            ]
    except Exception as e:
        logger.warning(f"DB query notice failed: {e}. Defaulting to sample records.")
    finally:
        db.close()

    # No verified record found: return nothing rather than invented sample data,
    # so the router falls back to "I don't know, contact this office".
    return []


def get_academic_calendar(start_date: Optional[str] = None, end_date: Optional[str] = None, event_keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """Academic calendar + holiday rows, ranked by keyword match, upcoming dates first."""
    db: Session = SessionLocal()
    try:
        query = db.query(AcademicCalendar)
        if start_date:
            query = query.filter(AcademicCalendar.start_date >= start_date)
        if end_date:
            query = query.filter(AcademicCalendar.start_date <= end_date)
        rows = query.order_by(AcademicCalendar.start_date.asc()).all()
        if not rows and (start_date or end_date):  # a guessed date range shouldn't hide the answer
            rows = db.query(AcademicCalendar).order_by(AcademicCalendar.start_date.asc()).all()
        if event_keyword:
            rows = _rank_rows(rows, event_keyword, lambda c: f"{c.event_name} {c.category} {c.target_audience}", CAL_GENERIC)
        if not event_keyword:  # no keyword: what's coming up next
            today = datetime.utcnow() - timedelta(days=1)
            rows = [c for c in rows if c.start_date >= today] or rows
        return [
            {
                "event_name": c.event_name,
                "category": c.category,
                "start_date": c.start_date.strftime("%Y-%m-%d") if c.start_date else "",
                "end_date": c.end_date.strftime("%Y-%m-%d") if c.end_date else None,
                "audience": c.target_audience,
                "description": c.description
            }
            for c in rows[:12]
        ]
    except Exception as e:
        logger.warning(f"DB query calendar failed: {e}")
        return []
    finally:
        db.close()


def get_events(start_date: Optional[str] = None, end_date: Optional[str] = None, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Workshops, conferences, CEPs and student fests, ranked by keyword match, upcoming first."""
    db: Session = SessionLocal()
    try:
        query = db.query(Event)
        if start_date:
            query = query.filter(Event.event_date >= start_date)
        if end_date:
            query = query.filter(Event.event_date <= end_date)
        rows = query.order_by(Event.event_date.asc()).all()
        if not rows and (start_date or end_date):
            rows = db.query(Event).order_by(Event.event_date.asc()).all()
        if event_type:
            rows = _rank_rows(rows, event_type, lambda e: f"{e.title} {e.organizer} {e.description}", CAL_GENERIC)
        today = datetime.utcnow()
        rows = sorted(rows, key=lambda e: e.event_date < today - timedelta(days=1))
        return [
            {
                "title": e.title,
                "organizer": e.organizer,
                "venue": e.venue,
                "event_date": e.event_date.strftime("%Y-%m-%d") if e.event_date else "",
                "description": e.description
            }
            for e in rows[:8]
        ]
    except Exception as e:
        logger.warning(f"DB query events failed: {e}")
        return []
    finally:
        db.close()


# Words that describe the question rather than the date/event being asked about
CAL_GENERIC = {"date", "dates", "schedule", "scheduled", "calendar", "academic", "start", "starts", "begin", "begins",
               "held", "happen", "happening", "will", "next", "upcoming", "this", "year", "event", "events", "nit",
               "rourkela", "day", "days", "time", "fest", "fests", "list", "all"}


def _compact(text: str) -> str:
    """'Mid -Semester Examinations' -> 'midsemesterexaminations' so 'midsem', 'mid-sem', 'mid sem' all match."""
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def _rank_rows(rows, query: str, text_fn, generic=frozenset()):
    """Rank ORM rows by how many query words (stemmed, spacing-insensitive) their text contains.
    Keeps rows matching at least half the words; returns rows unchanged when the query has no useful words."""
    words = [w[:-1] if len(w) > 4 and w.endswith("s") else w
             for w in re.findall(r"[a-z0-9]+", (query or "").lower())
             if w not in STOP_WORDS and w not in generic and len(w) > 2]
    words = list(dict.fromkeys(_compact(w) for w in words))
    if not words:
        return rows
    need = max(1, (len(words) + 1) // 2)
    scored = []
    for r in rows:
        hay = _compact(text_fn(r))
        hits = sum(1 for w in words if w in hay)
        if hits >= need:
            scored.append((hits, r))
    scored.sort(key=lambda x: (-x[0], len(text_fn(x[1]))))  # most words, then the most specific (shortest) row
    return [r for _, r in scored]


# Words that describe the request rather than the person / topic being searched for
FACULTY_GENERIC = {"faculty", "faculties", "professor", "professors", "prof", "teacher", "teachers", "working", "works",
                   "work", "research", "researching", "area", "areas", "department", "dept", "who", "whom", "list",
                   "members", "member", "staff", "contact", "email", "phone", "number", "office", "room", "expert",
                   "experts", "interest", "interests", "field", "nit", "rourkela", "with", "does", "doing", "teaches"}

# Common short names -> department code (codes are the site's URL prefixes, e.g. /CS/).
DEPT_ALIASES = {
    "cse": "CS", "computer science": "CS", "computer": "CS", "ece": "EC", "electronics": "EC",
    "ee": "EE", "eee": "EE", "electrical": "EE", "mech": "ME", "mechanical": "ME", "civil": "CE",
    "chemical": "CH", "ceramic": "CR", "biotech": "BM", "biotechnology": "BM", "biomedical": "BM",
    "food": "FP", "metallurgy": "MM", "metallurgical": "MM", "mme": "MM", "materials": "MM", "mining": "MN",
    "architecture": "PA", "planning": "PA", "humanities": "HS", "hss": "HS", "management": "SM", "mba": "SM",
    "chemistry": "CY", "earth": "ER", "atmospheric": "ER", "life science": "LS", "mathematics": "MA",
    "maths": "MA", "math": "MA", "physics": "PH", "industrial design": "ID", "design": "ID",
}


def match_department(text: Optional[str]) -> Optional[str]:
    """Department code for a name, alias or code mentioned in text (None if no department is named)."""
    if not text:
        return None
    t = text.lower()
    db: Session = SessionLocal()
    try:
        depts = db.query(Department.code, Department.name).all()
    except Exception:
        depts = []
    finally:
        db.close()
    for code, name in sorted(depts, key=lambda d: -len(d[1])):  # longest name first
        if name.lower() in t or re.fullmatch(code.lower(), t.strip()):
            return code
    for alias, code in sorted(DEPT_ALIASES.items(), key=lambda a: -len(a[0])):
        if re.search(rf"\b{re.escape(alias)}\b", t):
            return code
    return None


def _degree_like(degree: str) -> str:
    """'btech' / 'B.Tech' / 'b tech' -> SQL LIKE pattern that matches the site's 'B.Tech.' spelling."""
    letters = re.sub(r"[^a-z]", "", degree.lower())
    known = {"btech": "B%Tech", "mtech": "M%Tech", "msc": "M%Sc", "phd": "Ph%D", "barch": "B%Arch",
             "mba": "MBA", "ma": "MA", "integratedmsc": "Integrated M%Sc", "dualdegree": "Dual"}
    return known.get(letters, degree)


def get_departments(department: Optional[str] = None, degree: Optional[str] = None,
                    specialisation_keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """Departments (HOD, counts, about) with their programmes, filtered by department / degree / specialisation."""
    db: Session = SessionLocal()
    try:
        dq = db.query(Department)
        code = match_department(department) if department else None
        if department and not code:
            dq = dq.filter(Department.name.ilike(f"%{department}%"))
        elif code:
            dq = dq.filter(Department.code == code)
        out = []
        for d in dq.order_by(Department.name.asc()).all():
            pq = db.query(Program).filter(Program.department_code == d.code)
            if degree:
                pq = pq.filter(Program.degree.ilike(f"%{_degree_like(degree)}%"))
                if _degree_like(degree) == "M%Tech":  # "M.Tech" should not also return "M.Tech.(R)" research rows
                    pq = pq.filter(~Program.degree.ilike("%(R)%"))
            if specialisation_keyword:
                pq = pq.filter(Program.specialisation.ilike(f"%{specialisation_keyword}%"))
            programs = [{"degree": p.degree, "specialisation": p.specialisation, "duration": p.duration,
                         "admission_through": p.admission_through} for p in pq.all()]
            if (degree or specialisation_keyword) and not programs:
                continue  # department doesn't offer what was asked
            out.append({
                "department": d.name, "code": d.code, "hod": d.hod_name, "hod_designation": d.hod_designation,
                "hod_email": d.hod_email, "hod_phone": d.hod_phone, "office_phone": d.office_phone,
                "stats": d.stats or {}, "about": (d.about or "")[:600], "url": d.url, "programs": programs,
            })
        if len(out) > 1:  # list answers: keep the payload small enough that no department is cut off
            for d in out:
                d.pop("about"); d.pop("stats")
                d["programs"] = [{"degree": p["degree"], "specialisation": p["specialisation"]} for p in d["programs"]]
                if not (degree or specialisation_keyword):  # "list all departments": names, HODs, links only
                    for k in ("programs", "hod_email", "hod_phone", "office_phone", "hod_designation"):
                        d.pop(k)
        return out
    except Exception as e:
        logger.warning(f"DB query departments failed: {e}")
        return []
    finally:
        db.close()


def get_faculty(department: Optional[str] = None, designation: Optional[str] = None, name_or_keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns faculty directory entries from database with fallback mock records."""
    db: Session = SessionLocal()
    try:
        query = db.query(Faculty)
        if department:
            code = match_department(department)
            dept_name = db.query(Department.name).filter(Department.code == code).scalar() if code else None
            query = query.filter(Faculty.department.ilike(f"%{dept_name or department}%"))

        # Check for HOD queries specifically
        if designation and "hod" in designation.lower():
            query = query.filter(Faculty.is_hod == True)
        elif designation:
            query = query.filter(Faculty.designation.ilike(f"%{designation}%"))

        if name_or_keyword:
            kw = name_or_keyword.strip()
            if re.search(r'\b(hod|head)\b', kw.lower()):
                query = query.filter(Faculty.is_hod == True)
            else:
                words = [w for w in re.findall(r'\b\w+\b', kw.lower())
                         if w not in STOP_WORDS and w not in FACULTY_GENERIC and len(w) > 2]
                if words:
                    conds = []
                    for w in words:
                        conds.append(Faculty.name.ilike(f"%{w}%"))
                        conds.append(Faculty.research_interests.ilike(f"%{w}%"))
                        conds.append(Faculty.department.ilike(f"%{w}%"))
                    query = query.filter(or_(*conds))
                    # Rank on whole-word matches; keep rows matching at least half the words
                    # (so "image processing" needs both-ish, and "anti" doesn't match "Shanti").
                    need = max(1, (len(words) + 1) // 2)
                    scored = []
                    for f in query.all():
                        hay = f"{f.name} {f.research_interests or ''} {f.department}".lower()
                        hits = sum(1 for w in words if re.search(rf"\b{re.escape(w)}", hay))
                        if hits >= need:
                            scored.append((hits, f))
                    scored.sort(key=lambda x: (-x[0], not x[1].is_hod, x[1].name))
                    query = None
                    results = [f for _, f in scored]

        if query is not None:
            results = query.order_by(Faculty.is_hod.desc(), Faculty.name.asc()).all()
        if results:
            return [
                {
                    "name": f.name,
                    "designation": f.designation,
                    "department": f.department,
                    "is_hod": f.is_hod,
                    "email": f.email,
                    "phone": f.phone,
                    "office": f.office_location,
                    "research": f.research_interests,
                    "profile_url": f.profile_url
                }
                for f in results
            ]
    except Exception as e:
        logger.warning(f"DB query faculty failed: {e}. Defaulting to sample records.")
    finally:
        db.close()

    # No verified record found: return nothing rather than invented sample data,
    # so the router falls back to "I don't know, contact this office".
    return []


def get_placement_stats(year: Optional[str] = None, department: Optional[str] = None,
                        programme: Optional[str] = None, by_sector: bool = False) -> Dict[str, Any]:
    """Placement rows for one year (latest by default): programme totals, or one department's rows, or sectors."""
    db: Session = SessionLocal()
    try:
        years = sorted({y for (y,) in db.query(PlacementStat.year).distinct()}, reverse=True)
        if not years:
            return {}
        m = re.search(r"(20\d{2})\s*[-–/]\s*(\d{2,4})", year or "")
        want = f"{m.group(1)}-{m.group(2)[-2:]}" if m else (years[0] if not year else None)
        if want is None:  # "2024" -> the year that starts or ends with it
            y4 = re.search(r"20\d{2}", year or "")
            want = next((y for y in years if y4 and (y.startswith(y4.group(0)) or y.endswith(y4.group(0)[-2:]))), years[0])
        if want not in years:
            want = years[0]
        q = db.query(PlacementStat).filter(PlacementStat.year == want)
        if by_sector:
            q = q.filter(PlacementStat.programme == "Industry / Sector").order_by(PlacementStat.job_offers.desc())
        else:
            q = q.filter(PlacementStat.programme != "Industry / Sector")
            code = match_department(department) if department else None
            dept_name = db.query(Department.name).filter(Department.code == code).scalar() if code else None
            if dept_name or department:
                q = q.filter(PlacementStat.department.ilike(f"%{dept_name or department}%"))
            elif not programme:
                q = q.filter(PlacementStat.department.in_(["All departments", "Total"]))
            if programme:
                q = q.filter(PlacementStat.programme.ilike(f"%{_degree_like(programme)}%"))
                if not (dept_name or department):
                    q = q.filter(PlacementStat.department != "All departments")
        rows = q.all()
        if programme and not rows:  # unknown programme spelling: fall back to that year's totals
            rows = db.query(PlacementStat).filter(PlacementStat.year == want,
                                                  PlacementStat.department.in_(["All departments", "Total"])).all()
        return {
            "year": want, "available_years": years, "source_url": f"https://www.nitrkl.ac.in/CDC/PlacementStatistics/?id={want}",
            "rows": [{"programme": r.programme, "department": r.department, "students": r.students,
                      "job_offers": r.job_offers} for r in rows[:10 if by_sector else 40]],  # sectors: top 10 by offers
        }
    except Exception as e:
        logger.warning(f"DB query placement stats failed: {e}")
        return {}
    finally:
        db.close()


HOSTEL_GENERIC = {"hostel", "hostels", "hall", "halls", "residence", "warden", "wardens", "assistant", "curfew", "mess",
                  "room", "rooms", "facility", "facilities", "girls", "boys", "girl", "boy", "contact", "email", "timing",
                  "timings", "list", "all", "nit", "rourkela", "students", "student"}


def get_hostels(name_or_code: Optional[str] = None, gender: Optional[str] = None) -> List[Dict[str, Any]]:
    """Halls of residence with warden / assistant warden, matched by hall name or code (CVR, MSS, KMS...)."""
    db: Session = SessionLocal()
    try:
        query = db.query(Hostel)
        text = (name_or_code or "").lower()
        if not gender and re.search(r"\bgirls?\b|ladies|women", text):
            gender = "Girls"
        elif not gender and re.search(r"\bboys?\b|gents|men\b", text):
            gender = "Boys"
        if gender:
            query = query.filter(Hostel.gender.ilike(f"%{gender}%"))
        rows = query.order_by(Hostel.name.asc()).all()
        if name_or_code:
            codes = {w.upper() for w in re.findall(r"[A-Za-z]{2,4}", name_or_code)}
            by_code = [h for h in rows if h.code and h.code.upper() in codes]
            rows = by_code or _rank_rows(rows, name_or_code, lambda h: h.name, HOSTEL_GENERIC)
        return [
            {
                "name": h.name,
                "code": h.code,
                "gender": h.gender,
                "warden": h.warden,
                "assistant_warden": h.assistant_warden,
                "contact_email": h.contact_email,
                "curfew_time": h.curfew_time,
                "description": h.description
            }
            for h in rows
        ]
    except Exception as e:
        logger.warning(f"DB query hostels failed: {e}")
        return []
    finally:
        db.close()


# Aliases for convenience
search_notices = get_notices
search_faculty = get_faculty
query_calendar = get_academic_calendar
search_hostels = get_hostels
