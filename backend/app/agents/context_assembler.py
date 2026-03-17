"""Engine #3a: Context Assembler — compiles weekly internal context brief."""

import json
import logging
from datetime import datetime, timezone

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.context_brief import ContextBrief
from app.agents.prompts.context_summary import (
    CONTEXT_ASSEMBLY_SYSTEM,
    CONTEXT_ASSEMBLY_USER,
)

logger = logging.getLogger(__name__)


class ContextAssembler:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def assemble_context(
        self,
        db: AsyncSession,
        slack_data: str = "",
        github_data: str = "",
        meeting_data: str = "",
        support_data: str = "",
        analytics_data: str = "",
    ) -> ContextBrief:
        """Compile weekly context from all internal sources."""
        now = datetime.now(timezone.utc)
        week_number = now.isocalendar()[1]
        year = now.year

        prompt = CONTEXT_ASSEMBLY_USER.format(
            week_number=week_number,
            year=year,
            slack_data=slack_data or "No Slack data available this week.",
            github_data=github_data or "No GitHub data available this week.",
            meeting_data=meeting_data or "No meeting transcripts available this week.",
            support_data=support_data or "No support ticket data available this week.",
            analytics_data=analytics_data or "No analytics data available this week.",
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=CONTEXT_ASSEMBLY_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            data = json.loads(text.strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse context assembly response: {e}")
            data = {
                "what_shipped": "",
                "customer_wins": "",
                "industry_trends": "",
                "internal_insights": "",
                "full_brief": "",
            }

        brief = ContextBrief(
            week_number=week_number,
            year=year,
            what_shipped=data.get("what_shipped", ""),
            customer_wins=data.get("customer_wins", ""),
            industry_trends=data.get("industry_trends", ""),
            internal_insights=data.get("internal_insights", ""),
            full_brief=data.get("full_brief", ""),
        )
        db.add(brief)
        await db.commit()
        await db.refresh(brief)

        logger.info(f"Context brief assembled for week {week_number}")
        return brief
