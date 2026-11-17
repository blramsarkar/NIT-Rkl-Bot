<!-- ==============================================================================
 * File: README.md
 * Role: System Documentation, Deployment & Academic Evaluation Guide
 * Purpose: Provides a comprehensive installation, architecture, environment setup,
 *          database initialization, widget integration, and academic benchmarking
 *          reference guide for the NIT Rourkela Chatbot System (NIT RKL Bot).
 * ============================================================================== -->

# Production Architecture & Implementation: NIT Rkl Bot

This repository houses the full modular production architecture for the **NIT Rourkela Website Chatbot (NIT RKL Bot)**, moving beyond monolithic prototypes into a clean, decoupled system built with FastAPI, PostgreSQL/pgvector, Native Tool-Calling LLM Agents (Anthropic Claude 3.5 / Groq), and an embeddable vanilla JavaScript chat widget.

---

## 1. File Structure & Purpose Annotations

```
nitrkl_bot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI: /chat, /chat/stream (SSE), /feedback, /health, /admin/*
│   │   ├── config.py            # Settings (.env): LLM keys, DB, CORS, limits, budget, admin key, scraper allowlist
│   │   ├── security.py          # PII redaction, SSRF allowlist, LLM budget, admin auth, untrusted-data wrapper, cache
│   │   ├── db/                  # SQLAlchemy engine/session, models (incl. Feedback, VerifiedAnswer, IngestionRun), seed
│   │   ├── pipeline/
│   │   │   ├── agent_router.py  # Guardrail -> verified answers -> cache -> LLM tool calling -> deterministic router
│   │   │   ├── source_pages.py  # Official nitrkl.ac.in page per topic + "contact this office" fallback (URLs checked 2026-11-15)
│   │   │   ├── structured_tools.py # ORM (parameterised) queries: departments & programmes, faculty, notices, calendar, events, hostels
│   │   │   ├── rag_retrieval.py # Vector + keyword search over document chunks
│   │   │   ├── ingestion.py     # PDF/text ingestion + scheduled web-page re-ingestion
│   │   │   ├── ingest_all_departments.py # Scrapes departments, programmes, faculty, notices, curricula -> SQL + vectors
│   │   │   ├── scheduler.py     # Background re-ingestion loop (REINGEST_INTERVAL_HOURS)
│   │   │   └── web_scraper.py   # Allowlisted scraper + live site search over SiteMap/department/faculty pages
│   │   └── utils/logging.py     # Redacted query logs, feedback, admin data helpers
│   ├── requirements.txt
│   └── .env.example             # Copy to .env (git-ignored)
├── widget/                      # Embeddable widget + demo page styled like nitrkl.ac.in (served at /widget/)
├── admin/                       # Admin view (served at /admin-ui/, needs ADMIN_API_KEY)
├── data/                        # nitrkl_bot.db (SQLite prototype) and ingest/ folder — git-ignored
├── reports/                     # Mid-term report files and the scripts that build them
├── docs/
└── run.py                       # python run.py  -> http://localhost:8000/
```

## 2. Quick Start & Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ with `pgvector` extension enabled (or SQLite for quick local test)

### Step 1: Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# Create local environment configuration
cp .env.example .env
```

### Step 2: Configure Environment Variables (.env)
Edit `.env` file to add your API keys:
```env
GROQ_API_KEY=gsk_xxxxxxxxx            # or ANTHROPIC_API_KEY; empty = deterministic router only
ALLOWED_ORIGINS=http://localhost:8000  # production: https://www.nitrkl.ac.in,https://nitrkl.ac.in
ENVIRONMENT=development
ADMIN_API_KEY=<32+ random characters>  # enables /admin-ui/
```

### Step 3: Run FastAPI Backend Server (Auto-Seeds DB & Serves Widget)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
On initial startup, `init_db()` automatically provisions the SQLite / PostgreSQL tables and seeds them with realistic NIT Rourkela institutional data, generating 384-dimensional dense vector embeddings for RAG retrieval.

- **Interactive Demo Portal (with Live Widget)**: Open `http://localhost:8000/` or `http://localhost:8000/widget/` in your browser.
- **OpenAPI Documentation**: Open `http://localhost:8000/docs`
- **Admin view**: Open `http://localhost:8000/admin-ui/` and sign in with `ADMIN_API_KEY`

### Step 4: Load real data from nitrkl.ac.in (recommended)
```bash
cd backend
python -m app.pipeline.ingest_all_departments           # departments, programmes, faculty (+ profiles), notices, curricula, embeddings
python -m app.pipeline.ingest_all_departments --no-profiles   # faster, skips per-faculty profile pages
python -m tests.check_live_scraper                      # self-check against the live site
```
This replaces the illustrative seed rows for departments, programmes, faculty and notices with what the
official site shows today. A table is only replaced when its scrape returned rows. See
`docs/tech_stack_and_architecture_guide.md` sections 4–5 for every feature and data source.

### Step 5: Standalone Seeder (Optional)
If you need to force-reseed the database at any time (e.g. after changing models or in production):
```bash
python -m app.db.seed --force
```

---

## 3. Web Site Embedding Instructions

To embed the floating chat widget on any official NIT Rourkela web page (`nitrkl.ac.in`), include the following lines before the closing `</body>` tag:

```html
<!-- NIT RKL Bot Widget Stylesheet -->
<link rel="stylesheet" href="https://bot.nitrkl.ac.in/widget/nitrkl-bot-widget.css" />

<!-- Configure API Endpoint -->
<script>
  window.NITRKL_BOT_API_URL = "https://bot.nitrkl.ac.in/chat";
</script>

<!-- NIT RKL Bot Widget Script -->
<script src="https://bot.nitrkl.ac.in/widget/nitrkl-bot-widget.js"></script>
```

---

## 4. Security & Operations

| Area | What the code does |
|---|---|
| Prompt injection | Tool output is wrapped as `UNTRUSTED RETRIEVED DATA`; the system prompt forbids following instructions inside it; scraper drops hidden elements and invisible Unicode |
| Secrets | `.env` is git-ignored; the widget only calls the backend and holds no keys |
| Abuse & cost | Per-IP per-minute limit (slowapi), per-user question window, 500-char message cap, 6-item history cap, `DAILY_LLM_CALL_BUDGET` (falls back to the no-LLM router when exhausted) |
| CORS | `ALLOWED_ORIGINS` allowlist; `*` is refused when `ENVIRONMENT=production` |
| SQL injection | All queries go through the SQLAlchemy ORM with bound parameters; LLM output never becomes SQL |
| XSS | Widget and admin view build DOM nodes with `textContent`; links are clickable only for allowlisted domains |
| SSRF | Scraper fetches only `SCRAPE_ALLOWED_DOMAINS` over http(s), rejects IP literals and odd ports, re-checks every redirect, caps response size |
| Privacy | Roll numbers, phone numbers, Aadhaar-like numbers and emails are redacted before logging or LLM calls; IPs are not logged; widget shows a notice |
| Wrong answers | Admin **verified answers** are matched before the LLM; invented "sample" fallback records were removed; no-match answers say "I don't have verified information" and name the office |
| Admin | `/admin/*` require `X-Admin-Key`; disabled when `ADMIN_API_KEY` is empty; `/admin/ingest` only reads files inside `data/ingest/` |

**Before going live:**
1. Run `python -m app.pipeline.ingest_all_departments` (departments, programmes, faculty, notices come from the live site). The academic calendar, events and hostels tables are still illustrative seed data in `backend/app/db/seed.py` — replace them with verified data.
2. Topic URLs in `backend/app/pipeline/source_pages.py` were checked against the live site on 2026-11-15; re-check after any site redesign.
3. Move to PostgreSQL (`DATABASE_URL`). Rate limits, the LLM budget and the cache are in-memory per process; with several workers use Redis or run one worker, and run the re-ingestion scheduler in one process only (or via cron: `python -m app.pipeline.scheduler --once` from `backend/`).
4. Set `TRUST_PROXY_HEADERS=true` only when behind your own nginx, otherwise every user shares the proxy's IP limit.

## 5. Topics Needing Clarity (For Web Admin / Professor)

To finalize official deployment on NIT Rourkela servers, please confirm:
1. **Database Access**: Will the production system connect to a read-only PostgreSQL replica or execute via REST APIs?
2. **LLM Provider & Budget**: Selection between Anthropic Claude 3.5 Sonnet (higher accuracy) vs Groq Llama-3.1-8b (higher speed, low cost).
3. **Document Ingestion Scope**: List of official PDF regulations to index in the RAG store (e.g., UG Rules, PG Handbooks, Hostel Rules).
4. **Hosting Domain**: Confirm SSL domain mapping (e.g., `https://bot.nitrkl.ac.in`).

---

## 6. Academic Paper & Publishability Framework

### Title Strategy
> *"A Hybrid Agentic Tool-Routing Architecture for Real-Time Institutional Information Retrieval"*

### Target Venues
- **Conferences**: IEEE TALE, IEEE ICAART, ACM SAC, Springer CCIS
- **Journals**: IEEE Access, Computers & Education: Artificial Intelligence

### Key Empirical Benchmarks to Report
1. **RAG Triad Metrics**: Context Relevance, Groundedness, and Answer Faithfulness using TruLens/Ragas across 300+ real student queries.
2. **Routing Accuracy**: Tool Selection Precision & Recall of Claude 3.5 vs Llama-3.1.
3. **User Evaluation**: System Usability Scale (SUS) survey metrics administered to 50+ students.
