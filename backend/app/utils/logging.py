"""
==============================================================================
File: backend/app/utils/logging.py
Role: Analytics logger, feedback store and admin data helpers
Purpose: Records queries (PII-redacted, no IP addresses), tools used, confidence
         and latency to QueryLog; tracks unanswered queries; stores thumbs
         up/down feedback; and serves the admin view (logs, feedback,
         unanswered, verified answers, ingestion runs).
==============================================================================
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.connection import SessionLocal
from app.db.models import QueryLog, UnansweredQuery, Feedback, VerifiedAnswer, IngestionRun
from app.security import redact_pii

logger = logging.getLogger("nitrkl_bot.utils.logging")


def log_query_to_db(query: str, bot_response: str = "", tools_used: List[str] = None,
                    source_type: str = "Hybrid", confidence_score: float = 1.0,
                    latency: float = 0.0) -> Optional[int]:
    """Store one interaction. Returns the QueryLog id (used to attach feedback)."""
    query = redact_pii(query)
    db: Session = SessionLocal()
    try:
        entry = QueryLog(user_query=query, bot_response=bot_response, tools_used=tools_used or [],
                         source_type=source_type, confidence_score=confidence_score, latency_seconds=latency)
        db.add(entry)
        if confidence_score < 0.6:
            existing = db.query(UnansweredQuery).filter(UnansweredQuery.user_query == query).first()
            if existing:
                existing.frequency_count += 1
                existing.last_asked_at = datetime.utcnow()
                existing.resolved = False
            else:
                db.add(UnansweredQuery(user_query=query, frequency_count=1))
        db.commit()
        return entry.id
    except Exception as e:
        logger.error(f"Failed to log query to DB: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def save_feedback(query_log_id: int, rating: int, comment: Optional[str]) -> bool:
    db: Session = SessionLocal()
    try:
        if not db.query(QueryLog.id).filter(QueryLog.id == query_log_id).first():
            return False
        existing = db.query(Feedback).filter(Feedback.query_log_id == query_log_id).first()
        if existing:  # one vote per answer; allow changing it
            existing.rating, existing.comment = rating, redact_pii(comment) or existing.comment
        else:
            db.add(Feedback(query_log_id=query_log_id, rating=rating, comment=redact_pii(comment) or None))
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# ------------------------------------------------------------------------------
# Admin view helpers
# ------------------------------------------------------------------------------
def get_unanswered_analytics(limit: int = 50) -> List[Dict[str, Any]]:
    db: Session = SessionLocal()
    try:
        rows = (db.query(UnansweredQuery).filter(UnansweredQuery.resolved == False)  # noqa: E712
                .order_by(UnansweredQuery.frequency_count.desc()).limit(limit).all())
        return [{"id": u.id, "query": u.user_query, "frequency_count": u.frequency_count,
                 "last_asked_at": str(u.last_asked_at)} for u in rows]
    except Exception as e:
        logger.error(f"Failed to fetch unanswered analytics: {e}")
        return []
    finally:
        db.close()


def resolve_unanswered(unanswered_id: int) -> bool:
    db: Session = SessionLocal()
    try:
        row = db.get(UnansweredQuery, unanswered_id)
        if not row:
            return False
        row.resolved = True
        db.commit()
        return True
    finally:
        db.close()


def get_recent_logs(limit: int = 100, only_low_confidence: bool = False,
                    only_negative: bool = False) -> List[Dict[str, Any]]:
    db: Session = SessionLocal()
    try:
        q = db.query(QueryLog, Feedback).outerjoin(Feedback, Feedback.query_log_id == QueryLog.id)
        if only_low_confidence:
            q = q.filter(QueryLog.confidence_score < 0.6)
        if only_negative:
            q = q.filter(Feedback.rating < 0)
        rows = q.order_by(QueryLog.timestamp.desc()).limit(limit).all()
        return [{
            "id": log.id, "timestamp": str(log.timestamp), "query": log.user_query,
            "response": log.bot_response, "tools_used": log.tools_used or [],
            "route": log.source_type, "confidence": log.confidence_score, "latency": log.latency_seconds,
            "feedback": fb.rating if fb else None, "feedback_comment": fb.comment if fb else None,
        } for log, fb in rows]
    finally:
        db.close()


def get_stats() -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        total = db.query(QueryLog).count()
        up = db.query(Feedback).filter(Feedback.rating > 0).count()
        down = db.query(Feedback).filter(Feedback.rating < 0).count()
        low = db.query(QueryLog).filter(QueryLog.confidence_score < 0.6).count()
        last_run = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).first()
        return {
            "total_queries": total, "thumbs_up": up, "thumbs_down": down, "unanswered": low,
            "verified_answers": db.query(VerifiedAnswer).filter(VerifiedAnswer.active == True).count(),  # noqa: E712
            "last_ingestion": None if not last_run else {
                "started_at": str(last_run.started_at), "trigger": last_run.trigger,
                "updated": last_run.pages_ok, "unchanged": last_run.pages_unchanged, "failed": last_run.pages_failed,
            },
        }
    finally:
        db.close()


def list_verified_answers() -> List[Dict[str, Any]]:
    db: Session = SessionLocal()
    try:
        rows = db.query(VerifiedAnswer).order_by(VerifiedAnswer.updated_at.desc()).all()
        return [{"id": r.id, "question": r.question, "answer": r.answer, "source_url": r.source_url,
                 "active": r.active, "updated_at": str(r.updated_at)} for r in rows]
    finally:
        db.close()


def upsert_verified_answer(question: str, answer: str, source_url: Optional[str],
                           active: bool = True, answer_id: Optional[int] = None) -> Optional[int]:
    from app.pipeline.embeddings import encode_text
    db: Session = SessionLocal()
    try:
        row = db.get(VerifiedAnswer, answer_id) if answer_id else None
        if answer_id and not row:
            return None
        if not row:
            row = VerifiedAnswer()
            db.add(row)
        row.question, row.answer, row.source_url, row.active = question, answer, source_url, active
        row.embedding = encode_text(question)
        db.commit()
        return row.id
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save verified answer: {e}")
        return None
    finally:
        db.close()


def delete_verified_answer(answer_id: int) -> bool:
    db: Session = SessionLocal()
    try:
        row = db.get(VerifiedAnswer, answer_id)
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True
    finally:
        db.close()


def list_ingestion_runs(limit: int = 20) -> List[Dict[str, Any]]:
    db: Session = SessionLocal()
    try:
        rows = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit).all()
        return [{"id": r.id, "started_at": str(r.started_at), "finished_at": str(r.finished_at),
                 "trigger": r.trigger, "updated": r.pages_ok, "unchanged": r.pages_unchanged,
                 "failed": r.pages_failed, "details": r.details} for r in rows]
    finally:
        db.close()
