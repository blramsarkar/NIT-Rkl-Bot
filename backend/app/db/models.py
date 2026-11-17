"""
==============================================================================
File: backend/app/db/models.py
Role: Database Schema & SQLAlchemy ORM Models
Purpose: Defines database tables for structured institutional data (Notices,
         Faculty, Events, Academic Calendar) as well as vector document chunks,
         query analytics logs, and unanswered user queries.
==============================================================================
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Notice(Base):
    """Stores official NIT Rourkela circulars, notices, and announcements."""
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    category = Column(String(100), default="General", index=True)  # Academic, Admission, Hostel, Placement, General
    published_date = Column(DateTime, default=datetime.utcnow, index=True)
    department = Column(String(150), nullable=True)
    content_summary = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Faculty(Base):
    """Stores NIT Rourkela faculty profiles, HOD information, and contact details."""
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    designation = Column(String(150), nullable=False)  # Professor, Associate Professor, Assistant Professor, HOD
    department = Column(String(150), nullable=False, index=True)
    is_hod = Column(Boolean, default=False, index=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    office_location = Column(String(200), nullable=True)
    research_interests = Column(Text, nullable=True)
    profile_url = Column(String(500), nullable=True)


class Department(Base):
    """One row per academic department, scraped from its nitrkl.ac.in/<CODE>/ home page."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), nullable=False, unique=True, index=True)  # CS, EE, ME ...
    name = Column(String(200), nullable=False, index=True)
    hod_name = Column(String(200), nullable=True)
    hod_designation = Column(String(150), nullable=True)
    hod_email = Column(String(200), nullable=True)
    hod_phone = Column(String(100), nullable=True)
    office_phone = Column(String(100), nullable=True)
    about = Column(Text, nullable=True)
    stats = Column(JSON, nullable=True)  # {"UNDERGRADUATE STUDENTS": 828, "FACULTIES": 25, ...}
    url = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Program(Base):
    """Degree programmes per department (B.Tech, M.Tech, Dual Degree, M.Sc, Ph.D ...)."""
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    department_code = Column(String(10), nullable=False, index=True)
    department = Column(String(200), nullable=False)
    degree = Column(String(100), nullable=False, index=True)  # "B.Tech.", "M.Tech.", "Ph.D." ...
    specialisation = Column(String(300), nullable=True)
    duration = Column(String(50), nullable=True)
    admission_through = Column(String(200), nullable=True)
    url = Column(String(500), nullable=True)


class AcademicCalendar(Base):
    """Stores key academic calendar dates, exam schedules, registration deadlines, and holidays."""
    __tablename__ = "academic_calendar"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(300), nullable=False, index=True)
    category = Column(String(100), default="Academic")  # Exam, Registration, Holiday, Event
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=True)
    target_audience = Column(String(100), default="All")  # B.Tech, M.Tech, Ph.D, All
    description = Column(Text, nullable=True)


class Event(Base):
    """Stores campus events, fests (Innovision, Vriddhi, Nitrutsav), workshops, and seminars."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    organizer = Column(String(200), nullable=True)  # Club, Department, Student Activity Centre
    venue = Column(String(200), nullable=True)
    event_date = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=True)


class Hostel(Base):
    """Stores Hall of Residence (Hostel) details, wardens, capacities, and curfews."""
    __tablename__ = "hostels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)  # MSS, VS, SD, KMS, CVR, DBA
    gender = Column(String(50), nullable=False)  # Boys, Girls
    warden = Column(String(200), nullable=True)
    assistant_warden = Column(String(200), nullable=True)
    contact_email = Column(String(200), nullable=True)
    curfew_time = Column(String(100), nullable=True)  # not published on the site; left empty unless verified
    description = Column(Text, nullable=True)


class PlacementStat(Base):
    """Placement statistics per year / programme / department (or recruiting sector), from /CDC/PlacementStatistics/."""
    __tablename__ = "placement_stats"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String(10), nullable=False, index=True)  # "2024-25"
    programme = Column(String(100), nullable=False, index=True)  # "B.Tech.", "M.Tech.", "Industry / Sector", "All"
    department = Column(String(200), nullable=False)  # department, sector, "All departments" or "Total"
    students = Column(Integer, nullable=True)
    job_offers = Column(Integer, nullable=True)
    url = Column(String(500), nullable=True)


class DocumentChunk(Base):
    """
    Stores unstructured policy chunks (handbooks, regulations, hostel rules)
    along with 384-dimensional dense vector embeddings for RAG retrieval.
    """
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(300), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # Admission, Hostel Rules, BTech Rules, MTech Rules
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # 384-dim dense float vector stored as JSON array
    chunk_metadata = Column(JSON, nullable=True)  # page number, section header, source url
    created_at = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    """Logs all user queries for analytical tracking, tool call breakdown, and latency metrics."""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=True)
    tools_used = Column(JSON, default=[])  # List of tools invoked by router
    source_type = Column(String(50), default="Hybrid")  # Structured SQL, RAG, Web Scraper, General
    confidence_score = Column(Float, default=1.0)
    latency_seconds = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class UnansweredQuery(Base):
    """Stores low-confidence or unanswerable queries for web admins to audit and improve KB."""
    __tablename__ = "unanswered_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False, unique=True)
    frequency_count = Column(Integer, default=1)
    last_asked_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)


class Feedback(Base):
    """Thumbs up/down on a specific bot answer (linked to its QueryLog row)."""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, index=True, nullable=False)
    rating = Column(Integer, nullable=False)  # +1 helpful, -1 wrong / unhelpful
    comment = Column(Text, nullable=True)     # PII-redacted
    reviewed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class VerifiedAnswer(Base):
    """
    Admin-approved answers. Checked before any LLM call, so fees, deadlines and
    admission rules come from verified text rather than model memory, and a bad
    answer can be fixed by an admin without code changes.
    """
    __tablename__ = "verified_answers"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    embedding = Column(JSON, nullable=True)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IngestionRun(Base):
    """History of scheduled / manual re-ingestion runs, for the admin view."""
    __tablename__ = "ingestion_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    finished_at = Column(DateTime, nullable=True)
    trigger = Column(String(20), default="schedule")  # schedule | manual
    pages_ok = Column(Integer, default=0)
    pages_unchanged = Column(Integer, default=0)
    pages_failed = Column(Integer, default=0)
    details = Column(JSON, nullable=True)
