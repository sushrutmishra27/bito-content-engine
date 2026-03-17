from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class WeeklyDigest(Base):
    __tablename__ = "weekly_digests"

    week_number: Mapped[int] = mapped_column(Integer, unique=True)
    year: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text, default="")
    total_sources: Mapped[int] = mapped_column(Integer, default=0)
    total_insights: Mapped[int] = mapped_column(Integer, default=0)
