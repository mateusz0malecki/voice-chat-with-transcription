from typing import Optional
from datetime import datetime
from .helpers import BaseConfig, CustomPagination


class Recording(BaseConfig):
    id: int
    filename: str
    duration: float
    url: str
    room_name: str
    created_at: Optional[datetime]


class RecordingPagination(CustomPagination):
    records: list[Recording] = []
