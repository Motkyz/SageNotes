from sqlalchemy import Column, Integer, ForeignKey, String

from app.db import Base


class NoteFiles(Base):
    __tablename__ = 'note_files'

    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), primary_key=True)
    file_link = Column(String, nullable=False)