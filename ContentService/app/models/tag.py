from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    color = Column(Integer, nullable=False)

    notes = relationship(
        "Note",
        secondary="note_tags",
        back_populates="tags"
    )