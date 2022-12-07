from .recording_schemas import Recording
from .helpers import BaseConfig, CustomPagination


class TranscriptionMini(BaseConfig):
    id: int
    filename: str
    recording: Recording


class Transcription(BaseConfig):
    id: int
    filename: str
    transcription_text: str
    recording: Recording


class TranscriptionPagination(CustomPagination):
    records: list[TranscriptionMini] = []
