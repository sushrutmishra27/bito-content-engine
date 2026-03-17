import uuid

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContentPiece(Base):
    __tablename__ = "content_pieces"

    channel: Mapped[str] = mapped_column(String(32))  # linkedin, twitter, blog, email
    category: Mapped[str] = mapped_column(String(64), default="")
    body: Mapped[str] = mapped_column(Text)
    selected_hook: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft, approved, scheduled, published, rejected
    suggested_post_time: Mapped[str] = mapped_column(String(64), default="")
    context_brief_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("context_briefs.id"), nullable=True
    )
    week_number: Mapped[int] = mapped_column(Integer)
    published_url: Mapped[str] = mapped_column(String(2048), default="")
