from typing import Optional
from datetime import datetime
from .helpers import BaseConfig, CustomPagination


class Transcription(BaseConfig):
    id: int
    filename: str
    url: str
    room_name: str
    created_at: Optional[datetime]


class TranscriptionText(BaseConfig):
    text: str
    room_name: str


class TranscriptionPagination(CustomPagination):
    records: list[Transcription] = []
