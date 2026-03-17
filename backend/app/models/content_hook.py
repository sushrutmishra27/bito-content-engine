import uuid

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContentHook(Base):
    __tablename__ = "content_hooks"

    content_piece_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_pieces.id"))
    hook_text: Mapped[str] = mapped_column(Text)
    rank: Mapped[int] = mapped_column(Integer)
    is_selected: Mapped[bool] = mapped_column(default=False)
