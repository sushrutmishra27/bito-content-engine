"""Scheduled job: weekly content generation."""

import logging

from app.db.session import async_session
from app.agents.content_generator import ContentGenerator

logger = logging.getLogger(__name__)


async def run_weekly_content():
    """Generate weekly content across all channels."""
    async with async_session() as db:
        generator = ContentGenerator()
        pieces = await generator.generate_weekly_content(db)
        logger.info(f"Weekly content generation: {len(pieces)} pieces created")
