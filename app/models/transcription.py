from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base
from .recording import Recording


class Transcription(Base):
    __tablename__ = "transcription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transcription_text = Column(Text)
    recording_id = Column(ForeignKey("recording.id", ondelete="CASCADE"))
    recording = relationship("Recording", back_populates="transcription")

    def __repr__(self):
        return f"<id: {self.id}, recording-id: {self.recording_id}>"

    @staticmethod
    def get_all_transcriptions(db):
        return db.query(Transcription).all()

    @staticmethod
    def get_transcription_by_id(db, _id):
        return db.query(Transcription).filter(Transcription.id == _id).first()
