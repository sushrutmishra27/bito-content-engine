"""Slack integration — fetches messages from configured channels."""

import logging
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)


class SlackIngester:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://slack.com/api"
        self.headers = {"Authorization": f"Bearer {token}"}

    async def get_channel_messages(
        self, channel_id: str, days_back: int = 7
    ) -> str:
        """Fetch messages from a Slack channel for the past N days."""
        oldest = datetime.now(timezone.utc) - timedelta(days=days_back)
        oldest_ts = str(oldest.timestamp())

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/conversations.history",
                headers=self.headers,
                params={
                    "channel": channel_id,
                    "oldest": oldest_ts,
                    "limit": 200,
                },
            )
            data = resp.json()

        if not data.get("ok"):
            logger.error(f"Slack API error: {data.get('error')}")
            return ""

        messages = data.get("messages", [])
        # Format messages as readable text
        formatted = []
        for msg in messages:
            text = msg.get("text", "")
            if text and not msg.get("subtype"):  # Skip system messages
                formatted.append(f"- {text}")

        return "\n".join(formatted)

    async def get_weekly_summary(self, channel_ids: list[str]) -> str:
        """Get a combined summary from multiple channels."""
        parts = []
        for channel_id in channel_ids:
            messages = await self.get_channel_messages(channel_id)
            if messages:
                parts.append(f"### Channel {channel_id}\n{messages}")
        return "\n\n".join(parts)
