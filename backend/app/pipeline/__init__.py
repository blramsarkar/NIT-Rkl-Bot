"""
==============================================================================
File: backend/app/pipeline/__init__.py
Role: Agent Pipeline Package Initialization
Purpose: Exposes agent router, RAG retrieval engine, structured tools, live scraper,
         and background ingestion pipeline.
==============================================================================
"""

from app.pipeline.agent_router import route_and_answer
from app.pipeline.structured_tools import structured_tools_list, search_notices, search_faculty, query_calendar
from app.pipeline.rag_retrieval import perform_vector_search
from app.pipeline.web_scraper import scrape_nitrkl_live
from app.pipeline.ingestion import ingest_document_file

__all__ = [
    "route_and_answer",
    "structured_tools_list",
    "search_notices",
    "search_faculty",
    "query_calendar",
    "perform_vector_search",
    "scrape_nitrkl_live",
    "ingest_document_file",
]
