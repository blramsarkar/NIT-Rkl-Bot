# Graph Report - nitrkl_bot_1.0  (2026-11-15)

## Corpus Check
- 34 files · ~68,286 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 1, .example 1, .tex 1)

## Summary
- 476 nodes · 1176 edges · 17 communities (14 shown, 3 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- structured_tools.py
- agent_router.py
- main.py
- ingest_all_departments.py
- os
- web_scraper.py
- source_pages.py
- nitrkl-bot-widget.js
- 1. Technology Stack Breakdown (What Each Tech Stack Component Is Used For)
- Added / fixed
- scheduler.py
- 2. Quick Start & Local Setup
- admin.js
- ponytail-graphify

## God Nodes (most connected - your core abstractions)
1. `run_structured_ingestion()` - 27 edges
2. `route_and_answer_deterministic()` - 22 edges
3. `fetch_allowed()` - 19 edges
4. `v2.2 changes` - 19 edges
5. `search_site()` - 16 edges
6. `get_departments()` - 15 edges
7. `scrape_nitrkl_live()` - 15 edges
8. `_soup()` - 14 edges
9. `Added / fixed` - 14 edges
10. `Department` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Step 3: Run FastAPI Backend Server (Auto-Seeds DB & Serves Widget)` --references--> `init_db()`  [INFERRED]
  README.md → backend/app/db/connection.py
- `**BeautifulSoup4 & HTTPX (`beautifulsoup4`, `httpx`)**` --references--> `fetch_allowed()`  [INFERRED]
  docs/tech_stack_and_architecture_guide.md → backend/app/pipeline/web_scraper.py
- `4.3 Live website search (`pipeline/web_scraper.py`)` --references--> `site_index()`  [INFERRED]
  docs/tech_stack_and_architecture_guide.md → backend/app/pipeline/web_scraper.py
- `**SQLAlchemy ORM (`sqlalchemy`, `psycopg2-binary`)**` --references--> `get_db()`  [INFERRED]
  docs/tech_stack_and_architecture_guide.md → backend/app/db/connection.py
- `v2.2 changes` --references--> `Hostel`  [INFERRED]
  CHANGES.md → backend/app/db/models.py

## Import Cycles
- 2-file cycle: `backend/app/pipeline/__init__.py -> backend/app/pipeline/agent_router.py -> backend/app/pipeline/__init__.py`

## Communities (17 total, 3 thin omitted)

### Community 0 - "structured_tools.py"
Cohesion: 0.06
Nodes (30): init_db(), AcademicCalendar, Department, DocumentChunk, Event, Faculty, Feedback, Hostel (+22 more)

### Community 1 - "agent_router.py"
Cohesion: 0.06
Nodes (40): _anthropic_synth(), _anthropic_tool_phase(), dedupe_sources(), _department_context(), execute_tool_call(), find_verified_answer(), _finish(), _groq_synth() (+32 more)

### Community 2 - "main.py"
Cohesion: 0.06
Nodes (37): admin_clear_cache(), admin_create_verified(), admin_delete_verified(), admin_ingest_file(), admin_ingestion_runs(), admin_list_verified(), admin_logs(), admin_reingest() (+29 more)

### Community 3 - "ingest_all_departments.py"
Cohesion: 0.09
Nodes (26): calendar_chunks(), _clean(), _date(), department_chunks(), discover_departments(), extract_curriculum_programs(), parse_academic_calendar(), parse_academic_regulations() (+18 more)

### Community 4 - "os"
Cohesion: 0.10
Nodes (3): create_report(), get_base64(), get_b64()

### Community 5 - "web_scraper.py"
Cohesion: 0.12
Nodes (11): extract_visible_text(), _has_word(), _looks_like_page(), _normalise(), scrape_nitrkl_live(), search_site(), site_index(), add() (+3 more)

### Community 6 - "source_pages.py"
Cohesion: 0.10
Nodes (20): detect_topic(), fallback_message(), is_unanswered(), office_for_query(), page_for_category(), topic_page(), 2. Comprehensive File System Directory Mapping, 3. End-to-End System Workings (Step-by-Step Execution Flow) (+12 more)

### Community 7 - "nitrkl-bot-widget.js"
Cohesion: 0.23
Nodes (21): addBotMessage(), addTyping(), addUserMessage(), appendInline(), applyLanguage(), el(), handleSend(), initWidget() (+13 more)

### Community 8 - "1. Technology Stack Breakdown (What Each Tech Stack Component Is Used For)"
Cohesion: 0.09
Nodes (20): get_db(), 1.1 Backend Core Frameworks, 1.2 Database & Data Storage Layer, 1.3 Machine Learning & Data Processing Utilities, 1.4 Security, Rate Limiting & Configuration, 1.5 Frontend Widget Layer, 1. Technology Stack Breakdown (What Each Tech Stack Component Is Used For), **Anthropic Claude API (`anthropic`)** (+12 more)

### Community 9 - "Added / fixed"
Cohesion: 0.12
Nodes (6): Settings, LLMBudget, Added / fixed, Already in v2.0 (kept, not redone), Housekeeping, v2.1 changes

### Community 10 - "scheduler.py"
Cohesion: 0.17
Nodes (8): ingest_document_file(), ingest_pdf_file(), ingest_text_content(), ingest_web_page(), recursive_chunk_text(), run_reingestion(), reingestion_loop(), start_scheduler()

### Community 11 - "2. Quick Start & Local Setup"
Cohesion: 0.12
Nodes (16): 1. File Structure & Purpose Annotations, 2. Quick Start & Local Setup, 3. Web Site Embedding Instructions, 4. Security & Operations, 5. Topics Needing Clarity (For Web Admin / Professor), 6. Academic Paper & Publishability Framework, Key Empirical Benchmarks to Report, Prerequisites (+8 more)

### Community 12 - "admin.js"
Cohesion: 0.47
Nodes (11): api(), loadLogs(), loadOverview(), loadRuns(), loadUnanswered(), loadVerified(), prefillVerified(), saveVerified() (+3 more)

### Community 13 - "ponytail-graphify"
Cohesion: 0.40
Nodes (4): ponytail-graphify, Prerequisites, Rules, Steps

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `init_db()` connect `structured_tools.py` to `scheduler.py`, `2. Quick Start & Local Setup`, `main.py`, `ingest_all_departments.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `run_structured_ingestion()` (e.g. with `AcademicCalendar` and `Department`) actually correct?**
  _`run_structured_ingestion()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Should `structured_tools.py` be split into smaller, more focused modules?**
  _Cohesion score 0.062037037037037036 - nodes in this community are weakly interconnected._
- **Why does `fetch_allowed()` connect `ingest_all_departments.py` to `structured_tools.py`, `web_scraper.py`, `1. Technology Stack Breakdown (What Each Tech Stack Component Is Used For)`, `Added / fixed`, `scheduler.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `fetch_allowed()` (e.g. with `Added / fixed` and `**BeautifulSoup4 & HTTPX (`beautifulsoup4`, `httpx`)**`) actually correct?**
  _`fetch_allowed()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `agent_router.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06254272043745727 - nodes in this community are weakly interconnected._
- **Why does `Step 3: Run FastAPI Backend Server (Auto-Seeds DB & Serves Widget)` connect `2. Quick Start & Local Setup` to `structured_tools.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._