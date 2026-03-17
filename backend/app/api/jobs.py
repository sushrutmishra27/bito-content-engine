"""Manual trigger endpoints for scheduled jobs."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.agents.insight_miner import InsightMiner
from app.agents.context_assembler import ContextAssembler
from app.agents.content_generator import ContentGenerator
from app.integrations.rss import RSSIngester

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/ingest-sources")
async def trigger_source_ingestion(db: AsyncSession = Depends(get_db)):
    """Manually trigger source ingestion (RSS, newsletters)."""
    rss = RSSIngester()
    count = await rss.ingest_feeds(db)
    return {"status": "ok", "new_items": count}


@router.post("/extract-insights")
async def trigger_insight_extraction(db: AsyncSession = Depends(get_db)):
    """Manually trigger weekly insight extraction."""
    miner = InsightMiner()
    digest = await miner.run_weekly_extraction(db)
    return {
        "status": "ok",
        "total_sources": digest.total_sources,
        "total_insights": digest.total_insights,
    }


@router.post("/assemble-context")
async def trigger_context_assembly(db: AsyncSession = Depends(get_db)):
    """Manually trigger context brief assembly.

    In production, this pulls from Slack/GitHub/etc.
    For now, accepts optional manual context via request body.
    """
    assembler = ContextAssembler()
    brief = await assembler.assemble_context(db)
    return {"status": "ok", "brief_id": str(brief.id)}


@router.post("/generate-content")
async def trigger_content_generation(db: AsyncSession = Depends(get_db)):
    """Manually trigger content generation for all channels."""
    generator = ContentGenerator()
    pieces = await generator.generate_weekly_content(db)
    return {
        "status": "ok",
        "pieces_generated": len(pieces),
        "channels": list(set(p.channel for p in pieces)),
    }
