import os
from fastapi import APIRouter, status, Depends, Response
from db.database import get_db
from sqlalchemy.orm import Session
from pydantic import parse_obj_as

from models.transcription import Transcription, Recording
from schemas import transcription_schemas
from auth.jwt_helper import get_current_user
from exceptions.exceptions import TranscriptionNotFound, RecordingNotFound
from settings import get_settings
from celery_worker.tasks import transcript

app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Transcriptions"])


@router.get(
    "/transcriptions/{transcription_id}",
    status_code=status.HTTP_200_OK,
    response_model=transcription_schemas.Transcription,
    dependencies=[Depends(get_current_user)]
)
async def get_transcription_info(
        transcription_id: int,
        db: Session = Depends(get_db),
):
    transcription = Transcription.get_transcription_by_id(db, transcription_id)
    if not transcription:
        raise TranscriptionNotFound(transcription_id)
    return transcription


@router.get(
    "/transcriptions",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
async def get_all_transcriptions(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10
):
    transcriptions = Transcription.get_all_transcriptions(db)
    first = (page - 1) * page_size
    last = first + page_size
    transcriptions_model = parse_obj_as(list[transcription_schemas.TranscriptionMini], transcriptions)
    response = transcription_schemas.TranscriptionPagination(
        transcriptions_model,
        "/api/v1/recordings",
        first,
        last,
        page,
        page_size
    )
    return response


@router.post(
    "/transcriptions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def create_new_transcription(
    recording_id: int,
    db: Session = Depends(get_db),
):
    recording = Recording.get_recording_by_id(db, recording_id)
    if not recording:
        raise RecordingNotFound(recording_id)

    transcript.delay(recording_id=recording_id)

    transcription_filename = f"{recording.filename.split('.')[0]}.txt"
    return {"info": f"File will be saved shortly as '{transcription_filename}'"}


@router.delete(
    "/transcriptions/{transcription_id}",
    dependencies=[Depends(get_current_user)]
)
async def delete_transcription(
        transcription_id: int,
        db: Session = Depends(get_db),
):
    transcription_to_delete = Transcription.get_transcription_by_id(db, transcription_id)
    if not transcription_to_delete:
        raise TranscriptionNotFound(transcription_id)

    file_path = app_settings.recordings_path + transcription_to_delete.filename
    try:
        os.remove(file_path)
    except Exception as e:
        print({"Error": e})

    db.delete(transcription_to_delete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
