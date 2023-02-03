from sqlalchemy import Column, Integer, DateTime, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base
from .room import Room


class Recording(Base):
    __tablename__ = "recording"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(256), nullable=False)
    duration = Column(Float(precision=2), nullable=False, default=0)
    url = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    room_name = Column(String, ForeignKey("room.name", ondelete='CASCADE'))
    room = relationship("Room", back_populates="recordings")

    def __repr__(self):
        return f"<id: {self.id}, length: {self.length}>"

    @staticmethod
    def get_all_recordings_for_user(db, user):
        return db.query(Recording).join(Room).filter(Room.users.contains(user)).all()

    @staticmethod
    def get_recording_by_id_for_user(db, recording_id, user):
        return db.query(Recording).filter(Recording.id == recording_id)\
            .join(Room).filter(Room.users.contains(user)).first()

    @staticmethod
    def get_recording_by_filename_for_user(db, filename, user):
        return db.query(Recording).filter(Recording.filename == filename)\
            .join(Room).filter(Room.users.contains(user)).first()
