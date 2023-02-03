import os
from fastapi import APIRouter, status, Depends, Response
from db.database import get_db
from sqlalchemy.orm import Session
from pydantic import parse_obj_as

from models.room import Room
from models.user import User
from schemas import room_schemas, user_schemas
from auth.jwt_helper import get_current_user
from settings import get_settings
from exceptions.exceptions import RoomNotFound

app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Rooms"])


@router.get(
    "/rooms/{room_name}",
    status_code=status.HTTP_200_OK,
    response_model=room_schemas.Room
)
async def get_room_info(
        room_name: str,
        db: Session = Depends(get_db),
        current_user: user_schemas.User = Depends(get_current_user),
):
    room = Room.get_room_by_name_for_user(db, room_name, current_user)
    if not room:
        raise RoomNotFound(room_name)
    return room


@router.get(
    "/rooms",
    status_code=status.HTTP_200_OK
)
async def get_all_rooms(
        db: Session = Depends(get_db),
        current_user: user_schemas.User = Depends(get_current_user),
        page: int = 1,
        page_size: int = 10
):
    rooms = Room.get_all_rooms_for_user(db, current_user)
    first = (page - 1) * page_size
    last = first + page_size
    rooms_model = parse_obj_as(list[room_schemas.Room], rooms)
    response = room_schemas.RoomPagination(
        rooms_model,
        "/api/v1/rooms",
        first,
        last,
        page,
        page_size
    )
    return response


@router.post(
    "/rooms",
    status_code=status.HTTP_201_CREATED
)
async def create_room(
        request: room_schemas.RoomCreate,
        current_user: user_schemas.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user = User.get_user_by_email(db, current_user.email)
    room = Room(
        name=request.name,
        users=[user]
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return {"info": f"Room '{request.name}' saved"}


@router.delete(
    "/rooms/{room_name}"
)
async def delete_room(
        room_name: str,
        current_user: user_schemas.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    room_to_delete = Room.get_room_by_name_for_user(db, room_name, current_user)
    if not room_to_delete:
        raise RoomNotFound

    for transcription in room_to_delete.transcriptions:
        file_path = app_settings.transcriptions_path + transcription.filename
        try:
            os.remove(file_path)
        except Exception as e:
            print({"Error": e})

    for recording in room_to_delete.recordings:
        file_path = app_settings.recordings_path + recording.filename
        try:
            os.remove(file_path)
        except Exception as e:
            print({"Error": e})

    db.delete(room_to_delete)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/rooms/{room_name}",
    status_code=status.HTTP_202_ACCEPTED
)
async def add_user_to_room(
        room_name: str,
        current_user: user_schemas.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    room_to_edit = Room.get_room_by_name(db, room_name)
    if not room_to_edit:
        raise RoomNotFound

    user_to_add = User.get_user_by_email(db, current_user.email)
    room_to_edit.users.append(user_to_add)
    db.commit()
    db.refresh(room_to_edit)
    return {"info": f"User '{current_user.email}' added to room '{room_name}'"}
