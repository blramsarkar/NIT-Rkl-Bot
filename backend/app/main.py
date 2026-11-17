"""
==============================================================================
File: backend/app/main.py
Role: FastAPI Application Main Server Entry Point
Purpose: REST API for the NIT Rourkela chatbot.
  Public:  POST /chat, POST /chat/stream (SSE), POST /feedback, GET /health,
           GET /config (languages, limits for the widget)
  Admin:   /admin/* (requires X-Admin-Key) — logs, feedback, unanswered queries,
           verified answers (fix bad answers), ingestion and re-ingestion
  Static:  /widget (demo portal + embeddable widget), /admin-ui (admin view)
Security: CORS allowlist, per-IP rate limits, message/history length limits,
  daily LLM budget, PII redaction before logging/LLM calls, no IP logging,
  admin key auth, ingestion restricted to INGEST_DIR, security headers.
==============================================================================
"""

import json
import logging
import os
import sys
import threading
import time
from collections import defaultdict
from typing import Dict, List, Literal, Optional

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import PROJECT_ROOT, settings
from app.db.connection import init_db
from app.pipeline.agent_router import answer_cache, llm_budget, route_and_answer, stream_answer
from app.security import admin_key_valid, client_ip_from, redact_pii
from app.utils import logging as store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nitrkl_bot.main")


def client_ip(request: Request) -> str:
    return client_ip_from(dict(request.headers), request.client.host if request.client else None,
                          settings.TRUST_PROXY_HEADERS)


# ------------------------------------------------------------------------------
# Rate limiter (slowapi if installed; the per-user window below always applies)
# ------------------------------------------------------------------------------
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    limiter = Limiter(key_func=client_ip, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])
except ImportError:  # pragma: no cover
    logger.warning("slowapi not installed: per-minute limiter disabled, per-user window still active.")
    RateLimitExceeded = None

    class _NoLimiter:
        def limit(self, *_a, **_k):
            return lambda f: f
    limiter = _NoLimiter()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
              description="NIT Rourkela chatbot API with tool routing, verified answers and admin review.")
if RateLimitExceeded is not None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if request.url.path.startswith("/admin"):
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Cache-Control", "no-store")
    return response


widget_dir = os.path.join(PROJECT_ROOT, "widget")
admin_ui_dir = os.path.join(PROJECT_ROOT, "admin")
if os.path.isdir(widget_dir):
    app.mount("/widget", StaticFiles(directory=widget_dir, html=True), name="widget")
if os.path.isdir(admin_ui_dir):
    app.mount("/admin-ui", StaticFiles(directory=admin_ui_dir, html=True), name="admin-ui")


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/widget/")


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    # Load the embedding model once, in the background, so the first user doesn't wait.
    from app.pipeline.embeddings import get_embedding_model
    threading.Thread(target=get_embedding_model, daemon=True).start()
    from app.pipeline.scheduler import start_scheduler
    app.state.reingest_task = start_scheduler()
    if not settings.ADMIN_API_KEY:
        logger.info("ADMIN_API_KEY not set: admin endpoints are disabled.")


# ------------------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------------------
Language = Literal["en", "hi", "or"]


class SourceItem(BaseModel):
    type: str
    ref: str
    url: Optional[str] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=settings.MAX_HISTORY_ITEM_CHARS)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=settings.MAX_QUERY_CHARS,
                       json_schema_extra={"example": "Who is the HOD of CSE?"})
    history: List[ChatMessage] = Field(default_factory=list, max_length=settings.MAX_HISTORY_ITEMS)
    language: Language = "en"


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = []
    tools_used: List[str] = []
    latency: float
    log_id: Optional[int] = None
    questions_remaining: Optional[int] = None


class FeedbackRequest(BaseModel):
    log_id: int
    rating: Literal[1, -1]
    comment: Optional[str] = Field(default=None, max_length=500)


class VerifiedAnswerIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    answer: str = Field(..., min_length=1, max_length=4000)
    source_url: Optional[str] = Field(default=None, max_length=500)
    active: bool = True
    resolve_unanswered_id: Optional[int] = None


class IngestRequest(BaseModel):
    file_name: str = Field(..., description="File name inside INGEST_DIR (data/ingest/)")
    category: str = Field(default="General Regulations", max_length=100)


# ------------------------------------------------------------------------------
# Per-user question window (in-memory, per process)
# ------------------------------------------------------------------------------
USER_QUESTION_HISTORY: Dict[str, List[float]] = defaultdict(list)
_quota_lock = threading.Lock()


def consume_question_quota(ip: str) -> int:
    now = time.time()
    window = settings.USER_RATE_WINDOW_MINUTES * 60
    with _quota_lock:
        recent = [t for t in USER_QUESTION_HISTORY.get(ip, []) if now - t < window]
        if len(recent) >= settings.MAX_QUESTIONS_PER_USER_WINDOW:
            USER_QUESTION_HISTORY[ip] = recent
            raise HTTPException(status_code=429, detail=(
                f"You have reached the limit of {settings.MAX_QUESTIONS_PER_USER_WINDOW} questions. "
                f"Please wait {settings.USER_RATE_WINDOW_MINUTES} minutes before asking more."))
        recent.append(now)
        USER_QUESTION_HISTORY[ip] = recent
        if len(USER_QUESTION_HISTORY) > 10000:  # drop idle entries
            for k in [k for k, v in USER_QUESTION_HISTORY.items() if not v or now - v[-1] > window]:
                USER_QUESTION_HISTORY.pop(k, None)
        return max(0, settings.MAX_QUESTIONS_PER_USER_WINDOW - len(recent))


def _clean_inputs(body: ChatRequest):
    query = redact_pii(body.query.strip())
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    history = [{"role": m.role, "content": redact_pii(m.content)} for m in body.history]
    return query, history


def _log(query: str, result: dict, latency: float) -> Optional[int]:
    return store.log_query_to_db(query=query, bot_response=result.get("answer", ""),
                                 tools_used=result.get("tools_used", []), source_type=result.get("route", "unknown"),
                                 confidence_score=result.get("confidence", 1.0), latency=latency)


# ------------------------------------------------------------------------------
# Public endpoints
# ------------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/config", tags=["System"])
def public_config():
    return {"languages": ["en", "hi", "or"], "max_query_chars": settings.MAX_QUERY_CHARS,
            "max_questions": settings.MAX_QUESTIONS_PER_USER_WINDOW,
            "window_minutes": settings.USER_RATE_WINDOW_MINUTES}


@app.post("/chat", response_model=ChatResponse, tags=["Conversational AI"])
@app.post("/api/chat", response_model=ChatResponse, include_in_schema=False)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def chat_endpoint(request: Request, body: ChatRequest):
    remaining = consume_question_quota(client_ip(request))
    query, history = _clean_inputs(body)
    start = time.time()
    try:
        result = route_and_answer(query=query, history=history, language=body.language)
    except Exception as e:
        logger.error(f"Routing exception: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
    latency = round(time.time() - start, 3)
    log_id = _log(query, result, latency)
    return ChatResponse(answer=result["answer"], sources=result.get("sources", []),
                        tools_used=result.get("tools_used", []), latency=latency, log_id=log_id,
                        questions_remaining=remaining)


@app.post("/chat/stream", tags=["Conversational AI"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def chat_stream_endpoint(request: Request, body: ChatRequest):
    """Server-Sent Events: `delta` events with text, then one `final` event with sources and log_id."""
    remaining = consume_question_quota(client_ip(request))
    query, history = _clean_inputs(body)

    def events():
        start = time.time()
        try:
            for ev in stream_answer(query=query, history=history, language=body.language):
                if ev["type"] == "final":
                    latency = round(time.time() - start, 3)
                    ev = {"type": "final", "answer": ev.get("answer", ""), "sources": ev.get("sources", []),
                          "tools_used": ev.get("tools_used", []), "latency": latency,
                          "log_id": _log(query, ev, latency), "questions_remaining": remaining}
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"Streaming exception: {e}")
            yield f"data: {json.dumps({'type': 'error', 'detail': 'An error occurred while processing your request.'})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/feedback", tags=["Conversational AI"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def feedback_endpoint(request: Request, body: FeedbackRequest):
    if not store.save_feedback(body.log_id, body.rating, body.comment):
        raise HTTPException(status_code=404, detail="Unknown answer id.")
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# Admin endpoints (X-Admin-Key header; disabled when ADMIN_API_KEY is unset)
# ------------------------------------------------------------------------------
def require_admin(request: Request, x_admin_key: Optional[str] = Header(default=None)):
    if not settings.ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Admin is disabled. Set ADMIN_API_KEY (16+ chars) in .env.")
    if not admin_key_valid(settings.ADMIN_API_KEY, x_admin_key):
        logger.warning(f"Rejected admin request to {request.url.path}")
        raise HTTPException(status_code=401, detail="Invalid admin key.")
    return True


admin = [Depends(require_admin)]


@app.get("/admin/stats", tags=["Administration"], dependencies=admin)
def admin_stats():
    return {**store.get_stats(), "llm_budget": llm_budget.status()}


@app.get("/admin/logs", tags=["Administration"], dependencies=admin)
def admin_logs(limit: int = Query(100, ge=1, le=500), low_confidence: bool = False, negative: bool = False):
    return {"logs": store.get_recent_logs(limit, low_confidence, negative)}


@app.get("/admin/unanswered", tags=["Administration"], dependencies=admin)
def admin_unanswered():
    return {"queries": store.get_unanswered_analytics()}


@app.post("/admin/unanswered/{unanswered_id}/resolve", tags=["Administration"], dependencies=admin)
def admin_resolve_unanswered(unanswered_id: int):
    if not store.resolve_unanswered(unanswered_id):
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "ok"}


@app.get("/admin/verified", tags=["Administration"], dependencies=admin)
def admin_list_verified():
    return {"answers": store.list_verified_answers()}


@app.post("/admin/verified", tags=["Administration"], dependencies=admin)
def admin_create_verified(body: VerifiedAnswerIn):
    new_id = store.upsert_verified_answer(body.question, body.answer, body.source_url, body.active)
    if not new_id:
        raise HTTPException(status_code=500, detail="Could not save")
    if body.resolve_unanswered_id:
        store.resolve_unanswered(body.resolve_unanswered_id)
    answer_cache.clear()
    return {"id": new_id}


@app.put("/admin/verified/{answer_id}", tags=["Administration"], dependencies=admin)
def admin_update_verified(answer_id: int, body: VerifiedAnswerIn):
    if not store.upsert_verified_answer(body.question, body.answer, body.source_url, body.active, answer_id):
        raise HTTPException(status_code=404, detail="Not found")
    answer_cache.clear()
    return {"id": answer_id}


@app.delete("/admin/verified/{answer_id}", tags=["Administration"], dependencies=admin)
def admin_delete_verified(answer_id: int):
    if not store.delete_verified_answer(answer_id):
        raise HTTPException(status_code=404, detail="Not found")
    answer_cache.clear()
    return {"status": "deleted"}


@app.post("/admin/cache/clear", tags=["Administration"], dependencies=admin)
def admin_clear_cache():
    answer_cache.clear()
    return {"status": "cleared"}


@app.get("/admin/ingestion-runs", tags=["Administration"], dependencies=admin)
def admin_ingestion_runs():
    return {"runs": store.list_ingestion_runs()}


@app.post("/admin/reingest", tags=["Administration"], dependencies=admin)
def admin_reingest(background_tasks: BackgroundTasks):
    from app.pipeline.ingestion import run_reingestion
    background_tasks.add_task(run_reingestion, "manual")
    answer_cache.clear()
    return {"status": "started"}


@app.post("/admin/ingest", tags=["Administration"], dependencies=admin)
def admin_ingest_file(body: IngestRequest):
    """Ingest a PDF/TXT/MD file that has been placed in INGEST_DIR. Paths outside it are refused."""
    from app.pipeline.ingestion import ingest_document_file
    base = os.path.realpath(settings.INGEST_DIR)
    target = os.path.realpath(os.path.join(base, body.file_name))
    if os.path.commonpath([base, target]) != base or not os.path.isfile(target):
        raise HTTPException(status_code=400, detail="File must exist inside the ingest folder.")
    result = ingest_document_file(target, body.category)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Ingestion failed"))
    answer_cache.clear()
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
