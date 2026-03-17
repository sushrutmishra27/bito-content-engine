"""Scheduled job: weekly insight extraction."""

import logging

from app.db.session import async_session
from app.agents.insight_miner import InsightMiner

logger = logging.getLogger(__name__)


async def run_weekly_insights():
    """Run weekly insight extraction from all collected content."""
    async with async_session() as db:
        miner = InsightMiner()
        digest = await miner.run_weekly_extraction(db)
        logger.info(
            f"Weekly insights: {digest.total_insights} insights from {digest.total_sources} sources"
        )
