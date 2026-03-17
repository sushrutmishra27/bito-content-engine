"""APScheduler configuration for scheduled jobs."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.jobs.ingest_sources import run_source_ingestion
from app.jobs.weekly_insights import run_weekly_insights
from app.jobs.weekly_content import run_weekly_content

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler():
    """Configure all scheduled jobs."""

    # Ingest RSS feeds and newsletters every 6 hours
    scheduler.add_job(
        run_source_ingestion,
        CronTrigger(hour="*/6"),
        id="ingest_sources",
        name="Ingest RSS & newsletter sources",
        replace_existing=True,
    )

    # Run weekly insight extraction on Sunday at 8pm
    scheduler.add_job(
        run_weekly_insights,
        CronTrigger(day_of_week="sun", hour=20),
        id="weekly_insights",
        name="Weekly insight extraction",
        replace_existing=True,
    )

    # Generate weekly content on Monday at 8am
    scheduler.add_job(
        run_weekly_content,
        CronTrigger(day_of_week="mon", hour=8),
        id="weekly_content",
        name="Weekly content generation",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with 3 jobs configured")
