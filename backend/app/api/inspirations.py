import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.inspiration import Inspiration

router = APIRouter(prefix="/api/inspirations", tags=["inspirations"])


class InspirationCreate(BaseModel):
    url: str
    title: str
    content_markdown: str
    note: str = ""
    category: str = "content-idea"


class InspirationResponse(BaseModel):
    id: uuid.UUID
    url: str
    title: str
    content_markdown: str
    note: str
    category: str
    source_type: str
    captured_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("", response_model=InspirationResponse, status_code=201)
async def create_inspiration(data: InspirationCreate, db: AsyncSession = Depends(get_db)):
    inspiration = Inspiration(
        url=data.url,
        title=data.title,
        content_markdown=data.content_markdown,
        note=data.note,
        category=data.category,
        source_type="manual_capture",
        captured_at=datetime.now(timezone.utc),
    )
    db.add(inspiration)
    await db.commit()
    await db.refresh(inspiration)
    return inspiration


@router.get("", response_model=list[InspirationResponse])
async def list_inspirations(
    category: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Inspiration).order_by(desc(Inspiration.captured_at))
    if category:
        query = query.where(Inspiration.category == category)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{inspiration_id}", response_model=InspirationResponse)
async def get_inspiration(inspiration_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Inspiration).where(Inspiration.id == inspiration_id))
    inspiration = result.scalar_one()
    return inspiration


@router.delete("/{inspiration_id}", status_code=204)
async def delete_inspiration(inspiration_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Inspiration).where(Inspiration.id == inspiration_id))
    inspiration = result.scalar_one()
    await db.delete(inspiration)
    await db.commit()
