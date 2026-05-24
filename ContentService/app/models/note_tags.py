from sqlalchemy import Column, Integer, ForeignKey

from app.db import Base


class NoteTags(Base):
    __tablename__ = 'note_tags'
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)