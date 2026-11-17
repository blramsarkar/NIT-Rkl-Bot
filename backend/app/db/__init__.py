"""
==============================================================================
File: backend/app/db/__init__.py
Role: Database Package Initialization
Purpose: Exposes SQLAlchemy engine, session generator, and ORM database models.
==============================================================================
"""

from app.db.connection import engine, SessionLocal, get_db, init_db
from app.db.models import Base, Notice, Event, AcademicCalendar, Faculty, Hostel, UnansweredQuery, QueryLog, DocumentChunk, Feedback, VerifiedAnswer, IngestionRun, Department, Program, PlacementStat

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "Base",
    "Notice",
    "Event",
    "AcademicCalendar",
    "Faculty",
    "Hostel",
    "UnansweredQuery",
    "QueryLog",
    "DocumentChunk",
    "Feedback",
    "VerifiedAnswer",
    "IngestionRun",
    "Department",
    "Program",
    "PlacementStat",
]
