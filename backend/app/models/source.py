from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(256))
    source_type: Mapped[str] = mapped_column(String(32))  # newsletter, rss, twitter, youtube
    config: Mapped[str] = mapped_column(Text, default="{}")  # JSON config (URL, credentials, etc.)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
