from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base
from .room import Room


class Transcription(Base):
    __tablename__ = "transcription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(256), nullable=False)
    url = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    room_name = Column(String, ForeignKey("room.name", ondelete='CASCADE'))
    room = relationship("Room", back_populates="transcription")

    def __repr__(self):
        return f"<id: {self.id}, recording-id: {self.recording_id}>"

    @staticmethod
    def get_all_transcriptions(db):
        return db.query(Transcription).all()

    @staticmethod
    def get_transcription_by_id(db, transcription_id):
        return db.query(Transcription).filter(Transcription.id == transcription_id).first()

    @staticmethod
    def get_transcription_by_filename(db, filename):
        return db.query(Transcription).filter(Transcription.filename == filename).first()
