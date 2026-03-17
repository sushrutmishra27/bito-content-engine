import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.content_piece import ContentPiece
from app.models.content_hook import ContentHook

router = APIRouter(prefix="/api/content", tags=["content"])


class ContentHookResponse(BaseModel):
    id: uuid.UUID
    hook_text: str
    rank: int
    is_selected: bool

    model_config = {"from_attributes": True}


class ContentPieceResponse(BaseModel):
    id: uuid.UUID
    channel: str
    category: str
    body: str
    selected_hook: str
    status: str
    suggested_post_time: str
    week_number: int
    published_url: str
    created_at: datetime
    hooks: list[ContentHookResponse] = []

    model_config = {"from_attributes": True}


class ContentPieceUpdate(BaseModel):
    body: str | None = None
    selected_hook: str | None = None
    status: str | None = None


@router.get("", response_model=list[ContentPieceResponse])
async def list_content(
    channel: str | None = None,
    status: str | None = None,
    week: int | None = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(ContentPiece).order_by(desc(ContentPiece.created_at))
    if channel:
        query = query.where(ContentPiece.channel == channel)
    if status:
        query = query.where(ContentPiece.status == status)
    if week:
        query = query.where(ContentPiece.week_number == week)
    query = query.limit(limit)
    result = await db.execute(query)
    pieces = result.scalars().all()

    responses = []
    for piece in pieces:
        hooks_result = await db.execute(
            select(ContentHook).where(ContentHook.content_piece_id == piece.id).order_by(ContentHook.rank)
        )
        hooks = hooks_result.scalars().all()
        responses.append(
            ContentPieceResponse(
                **{c.key: getattr(piece, c.key) for c in piece.__table__.columns},
                hooks=[ContentHookResponse.model_validate(h) for h in hooks],
            )
        )
    return responses


@router.get("/{content_id}", response_model=ContentPieceResponse)
async def get_content(content_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentPiece).where(ContentPiece.id == content_id))
    piece = result.scalar_one()
    hooks_result = await db.execute(
        select(ContentHook).where(ContentHook.content_piece_id == piece.id).order_by(ContentHook.rank)
    )
    hooks = hooks_result.scalars().all()
    return ContentPieceResponse(
        **{c.key: getattr(piece, c.key) for c in piece.__table__.columns},
        hooks=[ContentHookResponse.model_validate(h) for h in hooks],
    )


@router.patch("/{content_id}", response_model=ContentPieceResponse)
async def update_content(
    content_id: uuid.UUID, data: ContentPieceUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ContentPiece).where(ContentPiece.id == content_id))
    piece = result.scalar_one()
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(piece, field, value)
    await db.commit()
    await db.refresh(piece)

    hooks_result = await db.execute(
        select(ContentHook).where(ContentHook.content_piece_id == piece.id).order_by(ContentHook.rank)
    )
    hooks = hooks_result.scalars().all()
    return ContentPieceResponse(
        **{c.key: getattr(piece, c.key) for c in piece.__table__.columns},
        hooks=[ContentHookResponse.model_validate(h) for h in hooks],
    )


@router.post("/{content_id}/hooks/{hook_id}/select", status_code=200)
async def select_hook(
    content_id: uuid.UUID, hook_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    # Deselect all hooks for this content piece
    hooks_result = await db.execute(
        select(ContentHook).where(ContentHook.content_piece_id == content_id)
    )
    for hook in hooks_result.scalars().all():
        hook.is_selected = hook.id == hook_id
        if hook.is_selected:
            # Update the content piece's selected_hook
            piece_result = await db.execute(
                select(ContentPiece).where(ContentPiece.id == content_id)
            )
            piece = piece_result.scalar_one()
            piece.selected_hook = hook.hook_text
    await db.commit()
    return {"status": "ok"}
