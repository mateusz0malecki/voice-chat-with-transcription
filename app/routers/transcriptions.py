import os
from fastapi import APIRouter, status, Depends, Response, HTTPException
from fastapi.responses import FileResponse
from db.database import get_db
from sqlalchemy.orm import Session
from pydantic import parse_obj_as

from models.transcription import Transcription
from schemas import transcription_schemas
from auth.jwt_helper import get_current_user
from exceptions.exceptions import TranscriptionNotFound
from settings import get_settings

app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Transcriptions"])


@router.get(
    "/transcriptions/file/{filename}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
async def get_transcription_file(filename: str):
    dir_ = app_settings.transcriptions_path
    file_path = os.path.join(dir_, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html", filename=filename)
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
        "/api/v1/recordings",
        first,
        last,
        page,
        page_size
    )
    return response


@router.post(
    "/transcriptions/file",
    status_code=status.HTTP_201_CREATED,
)
async def save_stream_transcription(
    request: transcription_schemas.TranscriptionPostText,
    db: Session = Depends(get_db),
):
    transcription_filename = "test.txt"
    transcription = Transcription(
        filename=transcription_filename,
        url=app_settings.domain + app_settings.root_path + "/transcriptions/file/" + transcription_filename,
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)

    if not os.path.exists(app_settings.transcriptions_path):
        os.mkdir(app_settings.transcriptions_path)
    with open(app_settings.transcriptions_path + transcription_filename, 'a') as file:
        file.write(request.text)

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


# @router.post(
#     "/transcriptions",
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(get_current_user)],
# )
# async def create_new_transcription(
#     recording_id: int,
#     db: Session = Depends(get_db),
# ):
#     recording = Recording.get_recording_by_id(db, recording_id)
#     if not recording:
#         raise RecordingNotFound(recording_id)
#
#     recording_filepath = app_settings.recordings_path + recording.filename
#
#     storage_client = get_client()
#
#     if recording.duration < 60 and os.path.getsize(recording_filepath) < 10000000:
#         results = transcript_small_local_file_gcp(recording_filepath)
#     else:
#         storage_client.upload(recording.filename, recording_filepath)
#         blob_uri = storage_client.get_blob_uri(recording.filename)
#         blob_uri = blob_uri.replace('/o/', '/')
#         results = transcript_big_bucket_file_gcp(blob_uri)
#
#     results_text = ""
#     for result in results:
#         results_text += f"- {autocorrect_with_punctuation(str(result.alternatives[0].transcript))}\n"
#
#     transcription_filename = f"{recording.filename.split('.')[0]}.txt"
#     transcription = Transcription(
#         filename=transcription_filename,
#         url=app_settings.domain + app_settings.root_path + "/transcriptions/file/" + transcription_filename,
#         recording_id=recording_id
#     )
#     db.add(transcription)
#     db.commit()
#     db.refresh(transcription)
#
#     if not os.path.exists(app_settings.transcriptions_path):
#         os.mkdir(app_settings.transcriptions_path)
#     with open(app_settings.transcriptions_path + transcription_filename, 'w') as file:
#         file.write(results_text)
#
#     return {"info": f"File saved as '{transcription_filename}'"}
