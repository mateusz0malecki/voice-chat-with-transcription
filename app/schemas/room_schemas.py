from typing import Optional
from datetime import datetime
from .helpers import BaseConfig, CustomPagination
from .recording_schemas import Recording
from .transcription_schemas import Transcription
from .user_schemas import User


class Room(BaseConfig):
    name: str
    created_at: Optional[datetime]
    recording: Optional[Recording]
    transcription: Optional[Transcription]
    users: Optional[list[User]] = []


class RoomCreate(BaseConfig):
    name: str


class RoomPagination(CustomPagination):
    records: list[Room] = []
