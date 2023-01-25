from typing import Optional
from datetime import datetime
from .helpers import BaseConfig, CustomPagination


class Transcription(BaseConfig):
    id: int
    filename: str
    url: str
    created_at: Optional[datetime]


class TranscriptionPostText(BaseConfig):
    text: str
    room_name: str


class TranscriptionPagination(CustomPagination):
    records: list[Transcription] = []
