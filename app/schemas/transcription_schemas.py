from typing import Optional
from datetime import datetime
from .recording_schemas import Recording
from .helpers import BaseConfig, CustomPagination


class Transcription(BaseConfig):
    id: int
    filename: str
    url: str
    created_at: Optional[datetime]
    recording: Optional[Recording]


class TranscriptionPostText(BaseConfig):
    text: str


class TranscriptionPagination(CustomPagination):
    records: list[Transcription] = []
