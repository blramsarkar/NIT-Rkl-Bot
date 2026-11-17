# v2.2 changes

| Item | Where |
|---|---|
| Real data from nitrkl.ac.in: 20 departments (HOD, phones, email, student/faculty counts, about), programmes (B.Tech, M.Tech, Dual Degree, M.Sc, Integrated M.Sc, Ph.D...), faculty with email/room/research areas/profile link, current notices | `ingest_all_departments.run_structured_ingestion`, new `departments` / `programs` tables, `faculty.profile_url` |
| `get_departments` tool (LLM + deterministic router): HOD, counts, programmes by degree / specialisation | `structured_tools.py`, `agent_router.py` |
| Department aliases (CSE, ECE, mech, maths...) resolved for faculty and department queries | `structured_tools.match_department` |
| Vector store: department overview + faculty-list chunks; more official pages re-ingested (scholarships, halls, CDC, how to apply, FAQs, anti-ragging, holidays, campus) | `department_chunks`, `source_pages.REINGEST_PAGES` |
| Live scraper accepts a plain question, not just a page name: searches an index of SiteMap + topic + department + faculty profile pages (site's own /Search is down), recovers from 404 paths | `web_scraper.search_site`, `site_index`, `scrape_nitrkl_live` |
| Deterministic router searches the live website before replying "no verified information" | `route_and_answer_deterministic` |
| Syllabus questions answered from the ingested curricula instead of a canned message; removed a 404 curricula link and unverified phone/email | `agent_router.py` |
| Fixed 4 topic URLs that returned 404 (scholarships, halls, placement, events) | `source_pages.py` |
| Widget, admin and demo page restyled to the nitrkl.ac.in look (#c35839, Nunito, site layout) | `widget/`, `admin/index.html` |
| Academic calendar from the official 2026-27 PDFs + holiday list; events from /Home/AllEvents/ + fests from the calendar; 11 halls with real wardens / assistant wardens | `parse_calendar_pdfs`, `parse_holidays`, `parse_events`, `parse_hostels` |
| Calendar / events / hostels / notices lookups rank by whole-word match instead of OR-ing substrings ("sem" no longer matches every row) | `structured_tools._rank_rows` |
| Removed illustrative seed policy chunks (invented phone numbers) and the invented curfew default | `ingest_all_departments`, `models.Hostel` |
| LLM guards: no guessed date filters, user words used for ranking, department record attached, live search when tools are empty, no placeholder contacts, official PDF as an answer | `agent_router.py` |
| Answers are brief bullet points (no tables, no nested bullets, one "Source:" line); list questions list every item | `agent_router` prompts + deterministic router |
| Placement statistics 2017-18 → latest (per programme, department, sector, total offers) in a new `placement_stats` table + `get_placement_stats` tool + vector chunks | `parse_placement_stats`, `structured_tools.get_placement_stats` |
| Live scraper follows hub pages one level deeper (e.g. /CDC/Statistics/ → ?id=2024-25) and reads table rows whole, so numbers aren't dropped | `web_scraper.search_site`, `extract_visible_text` |
| Second Groq model (`FALLBACK_LLM_MODEL`) used when the main model hits its daily limit | `agent_router._llm_providers` |
| Self-check against the live site | `backend/tests/check_live_scraper.py` |
| Docs: feature reference, data tables, refresh commands | `docs/tech_stack_and_architecture_guide.md` §4–5, README |

# v2.1 changes

## Already in v2.0 (kept, not redone)
- Quick-suggestion chips, source badges, deterministic no-LLM fallback router
- Per-IP rate limiting (slowapi + 15 questions / 10 min window)
- Parameterised ORM queries in `structured_tools.py` (no SQL built from LLM output)
- Widget HTML-escaped text before formatting; widget never held API keys
- Pre-ingested data with live scraping only as a tool fallback
- Embedding model loaded once (singleton) — now also warmed at startup

## Added / fixed
| Item | Where |
|---|---|
| Official nitrkl.ac.in link on every source badge | `pipeline/source_pages.py`, `agent_router.sources_for_tool` |
| "I don't have verified information — contact <office>: <url>" fallback | `source_pages.fallback_message` |
| Removed invented `mock_*` records returned when a lookup found nothing | `structured_tools.py` |
| Hindi / Odia (UI, chips, LLM reply language, fallback text) | widget, `agent_router` |
| Thumbs up/down + optional comment, linked to the logged answer | `POST /feedback`, `Feedback` table, widget |
| Admin-verified answers checked before the LLM (fees, deadlines, corrections) | `VerifiedAnswer` table, `/admin/verified` |
| Scheduled re-ingestion of official pages (content-hash, replace on change) | `pipeline/scheduler.py`, `ingestion.run_reingestion` |
| Admin view: stats, logs, thumbs-down, unanswered, verified answers, ingestion runs | `/admin-ui/`, `/admin/*` (X-Admin-Key) |
| Streaming answers (SSE) with fallback to `/chat` | `POST /chat/stream`, widget |
| Answer cache for frequent questions (TTL + LRU) | `security.TTLCache` |
| Prompt-injection: untrusted-data envelope + system-prompt rules + hidden-text stripping | `security.wrap_untrusted`, `web_scraper` |
| SSRF: domain allowlist, no IP literals/odd ports, redirect re-check, size cap | `security.is_url_allowed`, `web_scraper.fetch_allowed` |
| CORS from settings; `*` refused in production | `config.get_allowed_origins_list` |
| Max message length (500), history cap (6), daily LLM call budget | `config`, `main.ChatRequest`, `security.LLMBudget` |
| PII redaction before logging and before LLM calls; IPs not logged; privacy notice | `security.redact_pii`, widget |
| XSS: widget and admin build DOM with textContent; links only for allowlisted domains | widget, `admin/admin.js` |
| Admin endpoints were open; `/admin/ingest` read any server path | now key-protected; ingest limited to `data/ingest/` |
| `/admin/unanswered` returned made-up sample rows when empty | removed |
| Anthropic follow-up call lacked `tools` (API error); model id now configurable | `agent_router` |
| Fallback embeddings used `hash()` (changes every restart) | stable md5 hash in `embeddings.py` |

## Housekeeping
- Removed the root `app` symlink (pointed to `backend/app`); one `backend/app/` remains
- Added `.gitignore` (`.env`, `__pycache__/`, `*.db`, `data/`, `.DS_Store`, `__MACOSX/`)
- One database at `data/nitrkl_bot.db` (was duplicated in root and `backend/`); path no longer depends on the start directory
- Report files and scripts moved to `reports/`; hard-coded `/Users/balaram/...` paths made relative
- Note: `reports/build_midterm_pdf.py` already had a syntax error (unescaped `\{` in a LaTeX string) before these changes; not touched
