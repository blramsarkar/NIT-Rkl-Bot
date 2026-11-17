"""
==============================================================================
File: backend/app/pipeline/ingestion.py
Role: Knowledge Base Ingestion & Chunking Pipeline
Purpose: Handles ingestion of official PDF documents (Hostel Rules, B.Tech Regulations,
         Academic Calendar PDFs, Fee Structures) and web content. Performs text extraction,
         recursive semantic chunking, dense vector embedding computation, and database indexing.
==============================================================================
"""

import os
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db.models import DocumentChunk
from app.pipeline.embeddings import encode_batch

logger = logging.getLogger("nitrkl_bot.pipeline.ingestion")


def recursive_chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Splits plain text into overlapping chunks for semantic retrieval."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        start += (chunk_size - chunk_overlap)
    return chunks


def ingest_text_content(content: str, document_name: str, category: str = "General Regulations") -> Dict[str, Any]:
    """Chunks raw text, generates dense vector embeddings, and stores records in database."""
    chunks = recursive_chunk_text(content)
    if not chunks:
        return {"status": "error", "message": "No valid text content found to ingest."}

    logger.info(f"Generating embeddings for {len(chunks)} chunks of '{document_name}'...")
    embeddings = encode_batch(chunks)

    db: Session = SessionLocal()
    inserted_count = 0
    try:
        for idx, chunk_content in enumerate(chunks):
            chunk_record = DocumentChunk(
                document_name=document_name,
                category=category,
                chunk_index=idx,
                content=chunk_content,
                embedding=embeddings[idx] if idx < len(embeddings) else None,
                chunk_metadata={"source": document_name, "total_chunks": len(chunks)}
            )
            db.add(chunk_record)
            inserted_count += 1
        db.commit()
        logger.info(f"Successfully indexed {inserted_count} embedded chunks for '{document_name}'.")
        return {
            "status": "success",
            "document_name": document_name,
            "category": category,
            "chunks_created": inserted_count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save chunks to DB: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def ingest_pdf_file(file_path: str, category: str = "General Regulations") -> Dict[str, Any]:
    """Extracts text from a local PDF file and indexes chunked records into the database."""
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"File path does not exist: {file_path}"}

    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        file_name = os.path.basename(file_path)
        return ingest_text_content(full_text, file_name, category)
    except Exception as e:
        logger.error(f"Failed to ingest PDF {file_path}: {e}")
        return {"status": "error", "message": str(e)}


def ingest_document_file(file_path: str, category: str) -> Dict[str, Any]:
    """Main entry point for document ingestion."""
    if file_path.lower().endswith(".pdf"):
        return ingest_pdf_file(file_path, category)
    elif file_path.lower().endswith((".txt", ".md")):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return ingest_text_content(text, os.path.basename(file_path), category)
    else:
        return {"status": "error", "message": "Supported formats: .pdf, .txt, .md"}


# ------------------------------------------------------------------------------
# Web page ingestion (used by the scheduled re-ingestion job)
# ------------------------------------------------------------------------------
def ingest_web_page(url: str, category: str) -> Dict[str, Any]:
    """
    Fetch an allowlisted official page and replace its chunks in the vector store.
    Skips the rewrite when the page text is unchanged (content hash).
    """
    import hashlib
    from app.pipeline.web_scraper import fetch_allowed, extract_visible_text

    try:
        resp = fetch_allowed(url)
    except Exception as e:
        return {"url": url, "status": "error", "message": str(e)[:200]}
    if resp.status_code != 200:
        return {"url": url, "status": "error", "message": f"HTTP {resp.status_code}"}

    text = extract_visible_text(resp.text, max_lines=400)
    if len(text) < 100:
        return {"url": url, "status": "error", "message": "Too little readable text; kept previous version"}

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    db: Session = SessionLocal()
    try:
        existing = db.query(DocumentChunk).filter(DocumentChunk.document_name == url).all()
        if existing and (existing[0].chunk_metadata or {}).get("content_hash") == digest:
            return {"url": url, "status": "unchanged", "chunks": len(existing)}

        chunks = recursive_chunk_text(text, chunk_size=220, chunk_overlap=30)
        embeddings = encode_batch(chunks)
        for row in existing:
            db.delete(row)
        for idx, chunk in enumerate(chunks):
            db.add(DocumentChunk(
                document_name=url,
                category=category,
                chunk_index=idx,
                content=chunk,
                embedding=embeddings[idx] if idx < len(embeddings) else None,
                chunk_metadata={"source_url": url, "content_hash": digest,
                                "total_chunks": len(chunks), "origin": "scheduled_ingestion"},
            ))
        db.commit()
        return {"url": url, "status": "updated", "chunks": len(chunks)}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to store chunks for {url}: {e}")
        return {"url": url, "status": "error", "message": str(e)[:200]}
    finally:
        db.close()


def run_reingestion(trigger: str = "schedule") -> Dict[str, Any]:
    """Re-ingest every page in REINGEST_PAGES and record the run."""
    from datetime import datetime
    from app.db.models import IngestionRun
    from app.pipeline.source_pages import REINGEST_PAGES

    started = datetime.utcnow()
    results = [ingest_web_page(p["url"], p["category"]) for p in REINGEST_PAGES]
    summary = {
        "pages_ok": sum(r["status"] == "updated" for r in results),
        "pages_unchanged": sum(r["status"] == "unchanged" for r in results),
        "pages_failed": sum(r["status"] == "error" for r in results),
    }
    db: Session = SessionLocal()
    try:
        db.add(IngestionRun(started_at=started, finished_at=datetime.utcnow(), trigger=trigger,
                            details=results, **summary))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Could not record ingestion run: {e}")
    finally:
        db.close()
    logger.info(f"Re-ingestion ({trigger}) finished: {summary}")
    return {**summary, "results": results}
