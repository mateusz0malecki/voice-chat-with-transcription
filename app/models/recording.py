from sqlalchemy import Column, Integer, DateTime, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base


class Recording(Base):
    __tablename__ = "recording"
    id = Column(Integer, primary_key=True, autoincrement=True)
    duration = Column(Float(precision=2), nullable=False, default=0)
    url = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    transcription = relationship("Transcription", back_populates="recording")

    def __repr__(self):
        return f"<id: {self.id}, length: {self.length}>"

    @staticmethod
    def get_all_recordings(db):
        return db.query(Recording).all()

    @staticmethod
    def get_recording_by_id(db, recording_id):
        return db.query(Recording).filter(Recording.id == recording_id).first()
