from typing import Optional
from datetime import datetime
from .helpers import BaseConfig, CustomPagination


class Recording(BaseConfig):
    id: int
    duration: float
    url: str
    created_at: Optional[datetime]


class RecordingPagination(CustomPagination):
    records: list[Recording] = []
