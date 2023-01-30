from sqlalchemy import Column, Integer, DateTime, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base


room_user_association_table = Table(
    "room_user_association_table",
    Base.metadata,
    Column("room_id", ForeignKey("room.name")),
    Column("user_id", ForeignKey("user.id"))
)


class Room(Base):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    recording = relationship(
        "Recording",
        back_populates="room",
        uselist=False,
        cascade="all, delete-orphan"
    )
    transcription = relationship(
        "Transcription",
        back_populates="room",
        uselist=False,
        cascade="all, delete-orphan"
    )
    users = relationship(
        "User",
        secondary=room_user_association_table,
    )

    @staticmethod
    def get_all_rooms(db, user):
        return db.query(Room).filter(Room.users.contains(user)).all()

    @staticmethod
    def get_room_by_name(db, room_name, user):
        return db.query(Room).filter(Room.name == room_name).filter(Room.users.contains(user)).first()
