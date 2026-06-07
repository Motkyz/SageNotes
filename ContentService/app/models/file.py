import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    note_id: Mapped[UUID] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)

    extension: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Дата создания именно файла, а не записи
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    note = relationship(
        "Note",
        back_populates="files"
    )