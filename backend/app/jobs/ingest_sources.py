"""Scheduled job: ingest content from RSS feeds and email newsletters."""

import logging

from app.db.session import async_session
from app.integrations.rss import RSSIngester

logger = logging.getLogger(__name__)


async def run_source_ingestion():
    """Run ingestion from all configured sources."""
    async with async_session() as db:
        rss = RSSIngester()
        rss_count = await rss.ingest_feeds(db)
        logger.info(f"Source ingestion complete: {rss_count} new RSS items")
