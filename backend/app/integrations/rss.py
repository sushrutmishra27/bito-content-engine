"""RSS/Atom feed ingestion."""

import logging
from datetime import datetime, timezone

import feedparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.models.raw_content import RawContent

logger = logging.getLogger(__name__)


class RSSIngester:
    async def ingest_feeds(self, db: AsyncSession) -> int:
        """Fetch and store content from all enabled RSS sources."""
        result = await db.execute(
            select(Source).where(Source.source_type == "rss", Source.enabled == True)
        )
        sources = result.scalars().all()

        total_new = 0
        for source in sources:
            import json
            config = json.loads(source.config)
            feed_url = config.get("url", "")
            if not feed_url:
                continue

            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:
                # Check if already ingested by URL
                existing = await db.execute(
                    select(RawContent).where(
                        RawContent.source_id == source.id,
                        RawContent.url == entry.get("link", ""),
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                content = entry.get("summary", "") or entry.get("description", "")
                raw = RawContent(
                    source_id=source.id,
                    title=entry.get("title", "Untitled"),
                    url=entry.get("link", ""),
                    content_markdown=content,
                    author=entry.get("author", ""),
                    published_at=datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    if hasattr(entry, "published_parsed") and entry.published_parsed
                    else None,
                )
                db.add(raw)
                total_new += 1

        await db.commit()
        logger.info(f"RSS ingestion complete: {total_new} new items from {len(sources)} feeds")
        return total_new
