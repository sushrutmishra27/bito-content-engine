import uuid

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContentPerformance(Base):
    __tablename__ = "content_performance"

    content_piece_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_pieces.id"), unique=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(default=0.0)
