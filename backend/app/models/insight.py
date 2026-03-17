import uuid

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Insight(Base):
    __tablename__ = "insights"

    source_inspiration_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("inspirations.id"), nullable=True
    )
    source_raw_content_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("raw_content.id"), nullable=True
    )
    source_type: Mapped[str] = mapped_column(String(32))  # capture, newsletter, rss, twitter, youtube
    insight_text: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    relevance_score: Mapped[int] = mapped_column(Integer, default=3)
    suggested_angles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    week_number: Mapped[int] = mapped_column(Integer)
    digest_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("weekly_digests.id"), nullable=True
    )
