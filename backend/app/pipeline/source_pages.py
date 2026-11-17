"""
==============================================================================
File: backend/app/pipeline/source_pages.py
Role: Official source pages & "contact this office" fallback directory
Purpose: Single place that maps each topic to (a) the official nitrkl.ac.in page
         cited as the answer's source link, (b) the office to contact when the bot
         has no verified answer, and (c) the pages re-ingested on a schedule.

URLs checked against the live site on 2026-11-15 (all HTTP 200; ContactUs timed out
that day but is linked from the site menu). Re-check if the site is restructured.
==============================================================================
"""

import re
from typing import Dict, List, Optional

BASE = "https://www.nitrkl.ac.in"

# topic -> official page + office to contact
TOPICS: Dict[str, Dict[str, str]] = {
    "admissions": {
        "label": "Admissions",
        "url": f"{BASE}/Academic/Admission/",
        "office": "Admission Cell, Academic Section",
        "keywords": r"admission|admissions|josaa|csab|ccmt|jam|gate|apply|eligibility|seat|cutoff|reporting|प्रवेश|ଆଡମିଶନ|ନାମଲେଖା",
    },
    "fees": {
        "label": "Fees & Scholarships",
        "url": f"{BASE}/Student/Scholarships_Financial_Assistance/",
        "office": "Accounts Section / Academic Section (Fees & Scholarships)",
        "keywords": r"fee|fees|tuition|waiver|scholarship|stipend|htra|refund|payment|शुल्क|फीस|छात्रवृत्ति|ଫି|ଛାତ୍ରବୃତ୍ତି",
    },
    "calendar": {
        "label": "Academic Calendar",
        "url": f"{BASE}/Academic/AcademicCalendar/",
        "office": "Academic Section (Office of the Dean, Academic)",
        "keywords": r"calendar|exam|exams|mid-?sem|end-?sem|registration|holiday|holidays|vacation|semester|schedule|deadline|convocation|परीक्षा|ପରୀକ୍ଷା",
    },
    "notices": {
        "label": "Notices",
        "url": f"{BASE}/Home/AllNotice/",
        "office": "Office of the Registrar",
        "keywords": r"notice|notices|circular|announcement|news|सूचना|ବିଜ୍ଞପ୍ତି",
    },
    "departments": {
        "label": "Departments & Faculty",
        "url": f"{BASE}/Academic/Engineering/",
        "office": "the respective Department Office",
        "keywords": r"department|faculty|professor|prof|hod|head|teacher|director|विभाग|ବିଭାଗ",
    },
    "curriculum": {
        "label": "Curricula & Syllabi",
        "url": f"{BASE}/Academic/CurriculaSyllabi/",
        "office": "Academic Section (Office of the Dean, Academic)",
        "keywords": r"curriculum|syllabus|syllabi|course structure|subject code|l-t-p|credit|credits|पाठ्यक्रम|ପାଠ୍ୟକ୍ରମ",
    },
    "hostels": {
        "label": "Halls of Residence",
        "url": f"{BASE}/Hall/",
        "office": "Office of the Chief Warden",
        "keywords": r"hostel|hostels|hall|warden|curfew|mess|room|allotment|छात्रावास|हॉस्टल|ହଷ୍ଟେଲ",
    },
    "placements": {
        "label": "Training & Placement",
        "url": f"{BASE}/CDC/",
        "office": "Training & Placement Centre",
        "keywords": r"placement|placements|internship|recruit|company|companies|package|ctc|tpo|प्लेसमेंट|ପ୍ଲେସମେଣ୍ଟ",
    },
    "events": {
        "label": "Events",
        "url": f"{BASE}/Home/AllEvents/",
        "office": "Student Activity Centre",
        "keywords": r"event|events|fest|innovision|nitrutsav|vriddhi|hackathon|workshop|conference|club",
    },
    "rules": {
        "label": "Academic Regulations",
        "url": f"{BASE}/Academic/AcademicRegulations/",
        "office": "Academic Section (Office of the Dean, Academic)",
        "keywords": r"rule|rules|regulation|regulations|attendance|cgpa|sgpa|grade|branch change|ordinance|नियम|ନିୟମ",
    },
    "contacts": {
        "label": "Contact Us",
        "url": f"{BASE}/Institute/ContactUs/",
        "office": "Institute Reception / Telephone Exchange",
        "keywords": r"contact|phone|telephone|email|address|reach|location|संपर्क|ଯୋଗାଯୋଗ",
    },
}

GENERAL_CONTACT = {
    "label": "NIT Rourkela",
    "url": BASE,
    "office": "the Institute Reception (see the Contact Us page)",
}

# Pages refreshed by the scheduled re-ingestion job (must be on SCRAPE_ALLOWED_DOMAINS).
REINGEST_PAGES: List[Dict[str, str]] = [
    {"url": TOPICS["curriculum"]["url"], "category": "Academic Rules & Curriculum"},
    {"url": TOPICS["rules"]["url"], "category": "Academic Rules"},
    {"url": TOPICS["calendar"]["url"], "category": "Academic Calendar"},
    {"url": TOPICS["admissions"]["url"], "category": "Admissions"},
    {"url": TOPICS["notices"]["url"], "category": "Notices"},
    {"url": TOPICS["fees"]["url"], "category": "Fees & Scholarships"},
    {"url": TOPICS["hostels"]["url"], "category": "Hostel Rules"},
    {"url": TOPICS["placements"]["url"], "category": "Placements"},
    {"url": f"{BASE}/Student/How2Apply/", "category": "Admissions"},
    {"url": f"{BASE}/Academic/UGProgramme/", "category": "Admissions"},
    {"url": f"{BASE}/Student/FAQs/", "category": "Admissions"},
    {"url": f"{BASE}/Student/AntiRagging/", "category": "Student Welfare"},
    {"url": f"{BASE}/Academic/Holidays/", "category": "Academic Calendar"},
    {"url": f"{BASE}/Institute/CampusFacility/", "category": "Campus Facilities"},
]

# Document-chunk category -> topic (for citing a page for RAG hits without their own URL)
CATEGORY_TOPIC = {
    "academic rules": "rules",
    "academic rules & curriculum": "curriculum",
    "curriculum & syllabus": "curriculum",
    "hostel rules": "hostels",
    "fees & scholarships": "fees",
    "admissions": "admissions",
    "postgraduate regulations": "rules",
    "notices": "notices",
    "academic calendar": "calendar",
    "academic calendar & regulations": "calendar",
    "placements": "placements",
    "departments": "departments",
    "student welfare": "contacts",
    "campus facilities": "contacts",
}


def detect_topic(query: str) -> Optional[str]:
    q = query.lower()
    best, best_hits = None, 0
    for key, t in TOPICS.items():
        hits = len(re.findall(rf"(?:\b|^)(?:{t['keywords']})", q))
        if hits > best_hits:
            best, best_hits = key, hits
    return best


def topic_page(topic: Optional[str]) -> Dict[str, str]:
    return TOPICS.get(topic or "", GENERAL_CONTACT)


def page_for_category(category: Optional[str]) -> str:
    topic = CATEGORY_TOPIC.get((category or "").strip().lower())
    return topic_page(topic)["url"]


def office_for_query(query: str) -> Dict[str, str]:
    """Office + page to refer the user to when no verified answer exists."""
    return topic_page(detect_topic(query))


FALLBACK_MARKER = "I don't have verified information on this"

FALLBACK_TEXT = {
    "en": FALLBACK_MARKER + ". Please contact {office}: {url}",
    "hi": "इस विषय पर मेरे पास सत्यापित जानकारी नहीं है। कृपया {office} से संपर्क करें: {url}",
    "or": "ଏହି ବିଷୟରେ ମୋ ପାଖରେ ଯାଞ୍ଚ ହୋଇଥିବା ତଥ୍ୟ ନାହିଁ। ଦୟାକରି {office} ସହ ଯୋଗାଯୋଗ କରନ୍ତୁ: {url}",
}

# Phrases (any language) that mean "no verified answer" -> logged as unanswered
UNANSWERED_PHRASES = [
    FALLBACK_MARKER.lower(),
    "सत्यापित जानकारी नहीं",
    "ଯାଞ୍ଚ ହୋଇଥିବା ତଥ୍ୟ ନାହିଁ",
    "not currently available",
    "could not locate",
    "unable to answer",
]


def fallback_message(query: str, language: str = "en") -> str:
    office = office_for_query(query)
    template = FALLBACK_TEXT.get(language, FALLBACK_TEXT["en"])
    return template.format(office=office["office"], url=office["url"])


def is_unanswered(answer: str) -> bool:
    a = (answer or "").lower()
    return any(p in a for p in UNANSWERED_PHRASES)
