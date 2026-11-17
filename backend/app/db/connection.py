"""
==============================================================================
File: backend/app/db/connection.py
Role: Database Connection Manager & Session Pool
Purpose: Establishes SQLAlchemy database engine, configures connection pooling,
         manages session lifecycle for FastAPI dependencies (`get_db`), and
         initializes database schema and pgvector extensions.
==============================================================================
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

logger = logging.getLogger("nitrkl_bot.db")

# Determine engine parameters based on database type
database_url = settings.DATABASE_URL
connect_args = {}

if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args, echo=settings.DEBUG)
else:
    # PostgreSQL connection pool settings for production
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG
    )

# Session factory for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session context per request.
    Closes session automatically upon endpoint completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initializes database tables and creates vector extension if using PostgreSQL.
    Seeds sample schema if empty.
    """
    from app.db.models import Base

    try:
        # If PostgreSQL, enable pgvector extension if available
        if not database_url.startswith("sqlite"):
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                logger.info("Successfully ensured pgvector extension is enabled.")
        
        # Create all tables defined in models.py
        Base.metadata.create_all(bind=engine)
        # create_all never adds columns to existing tables; add the ones introduced later.
        from sqlalchemy import inspect
        if "profile_url" not in {c["name"] for c in inspect(engine).get_columns("faculty")}:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE faculty ADD COLUMN profile_url VARCHAR(500)"))
        logger.info("Database tables initialized successfully.")

        # Seed initial institutional data if empty
        from app.db.seed import seed_database_if_empty
        seed_database_if_empty()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
