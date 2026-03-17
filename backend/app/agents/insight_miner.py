"""Engine #2: Insight Miner — extracts insights from collected content using Claude API."""

import json
import logging
from datetime import datetime, timezone

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.inspiration import Inspiration
from app.models.raw_content import RawContent
from app.models.insight import Insight
from app.models.weekly_digest import WeeklyDigest
from app.agents.prompts.insight_extraction import (
    INSIGHT_EXTRACTION_SYSTEM,
    INSIGHT_EXTRACTION_USER,
)

logger = logging.getLogger(__name__)


class InsightMiner:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def extract_insights_from_content(
        self, title: str, source_type: str, url: str, content: str
    ) -> list[dict]:
        """Extract insights from a single piece of content using Claude."""
        prompt = INSIGHT_EXTRACTION_USER.format(
            title=title,
            source_type=source_type,
            url=url,
            content=content[:30000],  # Trim to avoid token limits
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=INSIGHT_EXTRACTION_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            text = response.content[0].text
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse insight extraction response: {e}")
            return []

    async def run_weekly_extraction(self, db: AsyncSession) -> WeeklyDigest:
        """Run the weekly insight extraction job."""
        now = datetime.now(timezone.utc)
        week_number = now.isocalendar()[1]
        year = now.year

        # Create or get weekly digest
        result = await db.execute(
            select(WeeklyDigest).where(
                WeeklyDigest.week_number == week_number,
                WeeklyDigest.year == year,
            )
        )
        digest = result.scalar_one_or_none()
        if not digest:
            digest = WeeklyDigest(week_number=week_number, year=year)
            db.add(digest)
            await db.flush()

        # Get all inspirations from this week that haven't been processed
        existing_insight_source_ids = set()
        existing_result = await db.execute(
            select(Insight.source_inspiration_id).where(
                Insight.week_number == week_number
            )
        )
        for row in existing_result:
            if row[0]:
                existing_insight_source_ids.add(row[0])

        # Process inspirations
        inspirations_result = await db.execute(
            select(Inspiration).where(
                Inspiration.id.notin_(existing_insight_source_ids) if existing_insight_source_ids else True
            )
        )
        inspirations = inspirations_result.scalars().all()

        total_insights = 0
        total_sources = 0

        for insp in inspirations:
            insights_data = await self.extract_insights_from_content(
                title=insp.title,
                source_type=insp.source_type,
                url=insp.url,
                content=insp.content_markdown,
            )
            total_sources += 1

            for insight_data in insights_data:
                insight = Insight(
                    source_inspiration_id=insp.id,
                    source_type="capture",
                    insight_text=insight_data.get("insight_text", ""),
                    tags=insight_data.get("tags", []),
                    relevance_score=insight_data.get("relevance_score", 3),
                    suggested_angles=insight_data.get("suggested_angles", []),
                    week_number=week_number,
                    digest_id=digest.id,
                )
                db.add(insight)
                total_insights += 1

        # Process raw content (newsletters, RSS, etc.)
        raw_result = await db.execute(select(RawContent))
        raw_contents = raw_result.scalars().all()

        for raw in raw_contents:
            insights_data = await self.extract_insights_from_content(
                title=raw.title,
                source_type="newsletter",
                url=raw.url,
                content=raw.content_markdown,
            )
            total_sources += 1

            for insight_data in insights_data:
                insight = Insight(
                    source_raw_content_id=raw.id,
                    source_type="newsletter",
                    insight_text=insight_data.get("insight_text", ""),
                    tags=insight_data.get("tags", []),
                    relevance_score=insight_data.get("relevance_score", 3),
                    suggested_angles=insight_data.get("suggested_angles", []),
                    week_number=week_number,
                    digest_id=digest.id,
                )
                db.add(insight)
                total_insights += 1

        # Update digest stats
        digest.total_sources = total_sources
        digest.total_insights = total_insights
        digest.summary = f"Processed {total_sources} sources, extracted {total_insights} insights."

        await db.commit()
        logger.info(f"Weekly extraction complete: {total_sources} sources, {total_insights} insights")
        return digest
