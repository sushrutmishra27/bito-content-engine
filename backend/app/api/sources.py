import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.source import Source

router = APIRouter(prefix="/api/sources", tags=["sources"])


class SourceCreate(BaseModel):
    name: str
    source_type: str  # newsletter, rss, twitter, youtube
    config: str = "{}"


class SourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    config: str
    enabled: bool

    model_config = {"from_attributes": True}


@router.post("", response_model=SourceResponse, status_code=201)
async def create_source(data: SourceCreate, db: AsyncSession = Depends(get_db)):
    source = Source(name=data.name, source_type=data.source_type, config=data.config)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.get("", response_model=list[SourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source))
    return result.scalars().all()


@router.patch("/{source_id}", response_model=SourceResponse)
async def toggle_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one()
    source.enabled = not source.enabled
    await db.commit()
    await db.refresh(source)
    return source
