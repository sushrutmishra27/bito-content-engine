import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RawContent(Base):
    __tablename__ = "raw_content"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(2048), default="")
    content_markdown: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(256), default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
