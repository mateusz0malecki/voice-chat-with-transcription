from fastapi import APIRouter, status, Depends, UploadFile, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import parse_obj_as

import os
import shutil
from librosa import get_duration
from datetime import datetime
from secrets import token_urlsafe

from db.database import get_db
from models.recording import Recording
from utils.convert import convert_to_wav_and_save_file
from schemas import recording_schemas
from auth.jwt_helper import get_current_user
from settings import get_settings
from exceptions.exceptions import RecordingNotFound

app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Recordings"])


@router.post(
    "/recordings",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)]
)
async def upload_new_recording(
        file: UploadFile,
        db: Session = Depends(get_db),
):
    temp_dir = "data/temp/"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    filename = f"{datetime.now().strftime('%d-%m-%Y')}-{token_urlsafe(8)}" + file.filename[-4:]

    with open(temp_dir + filename, "wb") as my_file:
        content = await file.read()
        my_file.write(content)
        my_file.close()

    if file.filename.endswith(".wav"):
        dir_ = app_settings.recordings_path
        if not os.path.exists(dir_):
            os.mkdir(dir_)
        shutil.copyfile(temp_dir + filename, dir_ + filename)
        new_filename = filename
        duration = get_duration(filename=temp_dir+filename)
    else:
        new_filename, duration = convert_to_wav_and_save_file(temp_dir, filename)
    os.remove(temp_dir + filename)

    new_recording = Recording(
        filename=new_filename,
        duration=duration,
        url=app_settings.domain + app_settings.root_path + "/recording-file/" + new_filename
    )
    db.add(new_recording)
    db.commit()
    db.refresh(new_recording)
    return {"info": f"File saved as '{new_filename}'"}


@router.get(
    "/recording-file/{filename}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
async def get_recording_file(filename: str):
    dir_ = app_settings.recordings_path
    file_path = os.path.join(dir_, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found."
    )


@router.get(
    "/recordings/{recording_id}",
    status_code=status.HTTP_200_OK,
    response_model=recording_schemas.Recording,
    dependencies=[Depends(get_current_user)]
)
async def get_recording_info(
        recording_id: int,
        db: Session = Depends(get_db),
):
    recording = Recording.get_recording_by_id(db, recording_id)
    if not recording:
        raise RecordingNotFound(recording_id)
    return recording


@router.get(
    "/recordings",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
async def get_all_recordings(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10
):
    recordings = Recording.get_all_recordings(db)
    first = (page - 1) * page_size
    last = first + page_size
    recordings_model = parse_obj_as(list[recording_schemas.Recording], recordings)
    response = recording_schemas.RecordingPagination(
        recordings_model,
        "/api/v1/recordings",
        first,
        last,
        page,
        page_size
    )
    return response


@router.delete(
    "/recordings/{recording_id}",
    dependencies=[Depends(get_current_user)]
)
async def delete_recording(
        recording_id: int,
        db: Session = Depends(get_db),
):
    recording_to_delete = Recording.get_recording_by_id(db, recording_id)
    if not recording_to_delete:
        raise RecordingNotFound(recording_id)

    file_path = app_settings.recordings_path + recording_to_delete.filename
    try:
        os.remove(file_path)
    except Exception as e:
        print({"Error": e})

    if recording_to_delete.transcription:
        transcription_file_path = app_settings.recordings_path + recording_to_delete.filename.split('.')[0] + '.txt'
        try:
            os.remove(transcription_file_path)
        except Exception as e:
            print({"Error": e})

    db.delete(recording_to_delete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
