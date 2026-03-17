from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Inspiration(Base):
    __tablename__ = "inspirations"

    url: Mapped[str] = mapped_column(String(2048))
    title: Mapped[str] = mapped_column(String(512))
    content_markdown: Mapped[str] = mapped_column(Text)
    note: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(64))
    source_type: Mapped[str] = mapped_column(String(32), default="manual_capture")
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
