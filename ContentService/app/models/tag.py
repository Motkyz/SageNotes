from uuid import UUID, uuid7

from sqlalchemy import String, UUID as SA_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db import Base


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    title: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String(9), nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(SA_UUID, nullable=True)
    # user_id: Mapped[UUID] = mapped_column(SA_UUID, nullable=False) TODO на время разработки, потом надо вернуть !!

    notes = relationship(
        "Note",
        secondary="note_tags",
        back_populates="tags",
        lazy = "selectin"
    )