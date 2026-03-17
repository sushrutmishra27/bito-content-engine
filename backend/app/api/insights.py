import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.insight import Insight
from app.models.weekly_digest import WeeklyDigest

router = APIRouter(prefix="/api/insights", tags=["insights"])


class InsightResponse(BaseModel):
    id: uuid.UUID
    source_type: str
    insight_text: str
    tags: list[str]
    relevance_score: int
    suggested_angles: list[str]
    week_number: int

    model_config = {"from_attributes": True}


class WeeklyDigestResponse(BaseModel):
    id: uuid.UUID
    week_number: int
    year: int
    summary: str
    total_sources: int
    total_insights: int
    insights: list[InsightResponse] = []

    model_config = {"from_attributes": True}


@router.get("", response_model=list[InsightResponse])
async def list_insights(
    week: int | None = None,
    min_relevance: int = Query(default=1, ge=1, le=5),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Insight)
        .where(Insight.relevance_score >= min_relevance)
        .order_by(desc(Insight.relevance_score))
    )
    if week:
        query = query.where(Insight.week_number == week)
    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/digests", response_model=list[WeeklyDigestResponse])
async def list_digests(
    limit: int = Query(default=10, le=52),
    db: AsyncSession = Depends(get_db),
):
    query = select(WeeklyDigest).order_by(desc(WeeklyDigest.week_number)).limit(limit)
    result = await db.execute(query)
    digests = result.scalars().all()

    responses = []
    for digest in digests:
        insights_result = await db.execute(
            select(Insight).where(Insight.digest_id == digest.id).order_by(desc(Insight.relevance_score))
        )
        insights = insights_result.scalars().all()
        responses.append(
            WeeklyDigestResponse(
                id=digest.id,
                week_number=digest.week_number,
                year=digest.year,
                summary=digest.summary,
                total_sources=digest.total_sources,
                total_insights=digest.total_insights,
                insights=[InsightResponse.model_validate(i) for i in insights],
            )
        )
    return responses
