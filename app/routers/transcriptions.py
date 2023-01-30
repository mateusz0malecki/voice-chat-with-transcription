import os
from fastapi import APIRouter, status, Depends, Response, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from db.database import get_db
from sqlalchemy.orm import Session
from pydantic import parse_obj_as
from datetime import datetime

from models.transcription import Transcription
from models.room import Room
from schemas import transcription_schemas
from auth.jwt_helper import get_current_user
from exceptions.exceptions import TranscriptionNotFound, RoomNotFound
from settings import get_settings
from utils.autocorrect_nlp import save_autocorrected_text

app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Transcriptions"])


@router.get(
    "/transcriptions/file/{filename}",
    status_code=status.HTTP_200_OK,
    response_model=transcription_schemas.TranscriptionText,
    dependencies=[Depends(get_current_user)]
)
async def get_transcription_file(
        filename: str,
        db: Session = Depends(get_db)
):
    dir_ = app_settings.transcriptions_path
    file_path = os.path.join(dir_, filename)
    transcription = Transcription.get_transcription_by_filename(db, filename)
    if transcription and os.path.exists(file_path):
        with open(file_path, "r") as file:
            file_text = file.read()
        return {
            "room_name": transcription.room_name,
            "text": file_text
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found."
    )


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
    transcriptions_model = parse_obj_as(list[transcription_schemas.Transcription], transcriptions)
    response = transcription_schemas.TranscriptionPagination(
        transcriptions_model,
        "/api/v1/transcriptions",
        first,
        last,
        page,
        page_size
    )
    return response


@router.post(
    "/transcriptions",
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_201_CREATED
)
async def save_stream_transcription(
    background_tasks: BackgroundTasks,
    request: transcription_schemas.TranscriptionText,
    db: Session = Depends(get_db)
):
    room = Room.get_room_by_name(db, request.room_name)
    if not room:
        raise RoomNotFound(request.room_name)

    data_dir = "data/"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    transcription_filename = f"{datetime.now().strftime('%d-%m-%Y')}-{request.room_name}.txt"
    transcription = Transcription(
        filename=transcription_filename,
        room_name=request.room_name,
        url=app_settings.domain + app_settings.root_path + "/transcriptions/file/" + transcription_filename,
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)

    dir_ = app_settings.transcriptions_path
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    background_tasks.add_task(
        save_autocorrected_text,
        text=request.text,
        transcription_filename=transcription_filename,
        directory=dir_
    )
    return {"info": f"File saved.'"}


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

    file_path = app_settings.transcriptions_path + transcription_to_delete.filename
    try:
        os.remove(file_path)
    except Exception as e:
        print({"Error": e})

    db.delete(transcription_to_delete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
