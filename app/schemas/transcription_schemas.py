from .recording_schemas import Recording
from .helpers import BaseConfig


class Transcription(BaseConfig):
    id: int
    transcription_text: str
    recording: Recording
