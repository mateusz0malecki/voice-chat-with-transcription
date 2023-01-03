import logging
import os

from celery import Task

from .celery import app
from db.database import db_session
from settings import get_settings
from models.transcription import Transcription, Recording
from utils.storage_client import get_client
from utils.transcript_gcp import transcript_big_bucket_file_gcp, transcript_small_local_file_gcp
from utils.autocorrect_nlp import autocorrect_with_punctuation

logging.getLogger(__name__)
app_settings = get_settings()

storage_client = get_client()


class SQLAlchemyTask(Task):
    """
    An abstract Celery Task that ensures that the connection the
    database is closed on task completion
    """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()


@app.task(name="transcript", base=SQLAlchemyTask)
def transcript(recording_id: int):
    recording = Recording.get_recording_by_id(db_session, recording_id)
    recording_filepath = app_settings.recordings_path + recording.filename

    if recording.duration < 60 and os.path.getsize(recording_filepath) < 10000000:
        results = transcript_small_local_file_gcp(recording_filepath)
    else:
        storage_client.upload(recording.filename, recording_filepath)
        blob_uri = storage_client.get_blob_uri(recording.filename)
        blob_uri = blob_uri.replace('/o/', '/')
        results = transcript_big_bucket_file_gcp(blob_uri)

    results_text = ""
    for result in results:
        results_text += f"- {autocorrect_with_punctuation(str(result.alternatives[0].transcript))}\n"

    transcription_filename = f"{recording.filename.split('.')[0]}.txt"
    transcription = Transcription(
        filename=transcription_filename,
        url=app_settings.domain + app_settings.root_path + "/transcriptions/file/" + transcription_filename,
        recording_id=recording_id
    )
    db_session.add(transcription)
    db_session.commit()
    db_session.refresh(transcription)

    if not os.path.exists(app_settings.transcriptions_path):
        os.mkdir(app_settings.transcriptions_path)
    with open(app_settings.transcriptions_path + transcription_filename, 'w') as file:
        file.write(results_text)
