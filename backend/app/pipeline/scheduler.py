"""
==============================================================================
File: backend/app/pipeline/scheduler.py
Role: Scheduled re-ingestion
Purpose: Background asyncio task that refreshes official pages (notices,
         calendar, admissions, fees, placements, hostels) every
         REINGEST_INTERVAL_HOURS so dates and notices stay current.
         No extra dependency; runs inside the API process. With several
         workers, run it in one process only (or use cron + `python -m
         app.pipeline.scheduler --once`).
==============================================================================
"""

import asyncio
import logging

from app.config import settings

logger = logging.getLogger("nitrkl_bot.pipeline.scheduler")


async def reingestion_loop() -> None:
    from app.pipeline.ingestion import run_reingestion

    interval = settings.REINGEST_INTERVAL_HOURS * 3600
    await asyncio.sleep(max(0, settings.REINGEST_INITIAL_DELAY_SECONDS))
    while True:
        try:
            await asyncio.to_thread(run_reingestion, "schedule")
        except Exception as e:  # never let the loop die
            logger.error(f"Scheduled re-ingestion failed: {e}")
        await asyncio.sleep(interval)


def start_scheduler() -> "asyncio.Task | None":
    if settings.REINGEST_INTERVAL_HOURS <= 0:
        logger.info("Scheduled re-ingestion disabled (REINGEST_INTERVAL_HOURS=0).")
        return None
    logger.info(f"Scheduled re-ingestion every {settings.REINGEST_INTERVAL_HOURS}h.")
    return asyncio.create_task(reingestion_loop())


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if "--once" in sys.argv:
        from app.db.connection import init_db
        from app.pipeline.ingestion import run_reingestion
        init_db()
        print(run_reingestion("manual"))
