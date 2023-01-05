from typing import Optional
from datetime import datetime
from .recording_schemas import Recording
from .helpers import BaseConfig, CustomPagination


class Transcription(BaseConfig):
    id: int
    filename: str
    url: str
    created_at: Optional[datetime]
    recording: Recording


class TranscriptionPagination(CustomPagination):
    records: list[Transcription] = []
