import datetime
from uuid import UUID, uuid7

from sqlalchemy import String, DateTime, Text, func, UUID as SA_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db import Base


class Note(Base):
    __tablename__ = 'notes'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)

    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[UUID | None] = mapped_column(SA_UUID, nullable=True)
    # user_id: Mapped[UUID] = mapped_column(SA_UUID, nullable=False) TODO на время разработки, потом надо вернуть !!

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    tags = relationship(
        "Tag",
        secondary="note_tags",
        back_populates="notes",
        lazy="selectin"
    )

    files = relationship(
        "File",
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
