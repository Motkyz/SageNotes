import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db import Base


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)

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
    )

    files = relationship(
        "NoteFiles",
        back_populates="note"
    )
