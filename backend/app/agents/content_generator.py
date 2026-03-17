"""Engine #3b: Content Generator — generates multi-channel content using Claude API."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.insight import Insight
from app.models.context_brief import ContextBrief
from app.models.content_piece import ContentPiece
from app.models.content_hook import ContentHook
from app.models.content_performance import ContentPerformance
from app.agents.prompts.content_generation import (
    CONTENT_GENERATION_SYSTEM,
    LINKEDIN_GENERATION_USER,
    TWITTER_GENERATION_USER,
    BLOG_GENERATION_USER,
    EMAIL_GENERATION_USER,
)

logger = logging.getLogger(__name__)

WRITING_PROFILES_DIR = Path(__file__).parent.parent.parent / "writing_profiles"

CHANNEL_CONFIG = {
    "linkedin": {"prompt": LINKEDIN_GENERATION_USER, "count": 12},
    "twitter": {"prompt": TWITTER_GENERATION_USER, "count": 7},
    "blog": {"prompt": BLOG_GENERATION_USER, "count": 2},
    "email": {"prompt": EMAIL_GENERATION_USER, "count": 1},
}


class ContentGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def _load_writing_style(self) -> str:
        """Load writing style guides from files."""
        style_parts = []
        for filename in ["bito_voice.md", "sushrut_style.md"]:
            filepath = WRITING_PROFILES_DIR / filename
            if filepath.exists():
                style_parts.append(filepath.read_text())
        return "\n\n".join(style_parts) if style_parts else "No writing style guide configured."

    async def _get_top_performers(self, db: AsyncSession) -> str:
        """Get top performing content for style reference."""
        result = await db.execute(
            select(ContentPiece, ContentPerformance)
            .join(ContentPerformance, ContentPerformance.content_piece_id == ContentPiece.id)
            .order_by(desc(ContentPerformance.engagement_rate))
            .limit(5)
        )
        rows = result.all()
        if not rows:
            return "No past performance data available yet."

        parts = []
        for piece, perf in rows:
            parts.append(
                f"- [{piece.channel}] Hook: {piece.selected_hook}\n"
                f"  Engagement: {perf.engagement_rate:.1%} | "
                f"Impressions: {perf.impressions} | Likes: {perf.likes}"
            )
        return "\n".join(parts)

    async def generate_weekly_content(
        self, db: AsyncSession, channels: list[str] | None = None
    ) -> list[ContentPiece]:
        """Generate content for all specified channels."""
        now = datetime.now(timezone.utc)
        week_number = now.isocalendar()[1]
        year = now.year

        # Get latest context brief
        brief_result = await db.execute(
            select(ContextBrief)
            .where(ContextBrief.week_number == week_number, ContextBrief.year == year)
            .order_by(desc(ContextBrief.created_at))
            .limit(1)
        )
        brief = brief_result.scalar_one_or_none()
        context_brief_text = brief.full_brief if brief else "No context brief available."

        # Get this week's insights
        insights_result = await db.execute(
            select(Insight)
            .where(Insight.week_number == week_number)
            .order_by(desc(Insight.relevance_score))
            .limit(20)
        )
        insights = insights_result.scalars().all()
        insights_text = "\n".join(
            f"- [{i.relevance_score}/5] {i.insight_text} (angles: {', '.join(i.suggested_angles)})"
            for i in insights
        ) or "No insights available this week."

        # Get top performers and writing style
        top_performers = await self._get_top_performers(db)
        writing_style = self._load_writing_style()

        system_prompt = CONTENT_GENERATION_SYSTEM.format(writing_style_guide=writing_style)

        target_channels = channels or list(CHANNEL_CONFIG.keys())
        all_pieces = []

        for channel in target_channels:
            if channel not in CHANNEL_CONFIG:
                continue

            config = CHANNEL_CONFIG[channel]
            user_prompt = config["prompt"].format(
                count=config["count"],
                context_brief=context_brief_text,
                insights=insights_text,
                top_performers=top_performers,
            )

            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=8000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            try:
                text = response.content[0].text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                content_items = json.loads(text.strip())
            except (json.JSONDecodeError, IndexError) as e:
                logger.error(f"Failed to parse {channel} content: {e}")
                continue

            for item in content_items:
                piece = ContentPiece(
                    channel=channel,
                    category=item.get("category", ""),
                    body=item.get("body", ""),
                    selected_hook=item.get("hooks", [""])[0],  # Default to first hook
                    status="draft",
                    suggested_post_time=item.get("suggested_post_time", ""),
                    context_brief_id=brief.id if brief else None,
                    week_number=week_number,
                )
                db.add(piece)
                await db.flush()

                # Create hook options
                for rank, hook_text in enumerate(item.get("hooks", [])[:8], start=1):
                    hook = ContentHook(
                        content_piece_id=piece.id,
                        hook_text=hook_text,
                        rank=rank,
                        is_selected=(rank == 1),
                    )
                    db.add(hook)

                all_pieces.append(piece)

        await db.commit()
        logger.info(f"Generated {len(all_pieces)} content pieces across {target_channels}")
        return all_pieces
