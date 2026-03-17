from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContextBrief(Base):
    __tablename__ = "context_briefs"

    week_number: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    what_shipped: Mapped[str] = mapped_column(Text, default="")
    customer_wins: Mapped[str] = mapped_column(Text, default="")
    industry_trends: Mapped[str] = mapped_column(Text, default="")
    internal_insights: Mapped[str] = mapped_column(Text, default="")
    full_brief: Mapped[str] = mapped_column(Text, default="")
