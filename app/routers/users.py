from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from pydantic import parse_obj_as

from schemas import user_schemas
from models.user import User
from db.database import get_db
from exceptions.exceptions import UserNotFound
from auth.jwt_helper import get_current_user
from settings import get_settings


app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Users"])


@router.get(
    "/me",
    response_model=user_schemas.UserDetail,
    status_code=status.HTTP_200_OK
)
async def read_user(
        db: Session = Depends(get_db),
        current_user: user_schemas.User = Depends(get_current_user),
):
    user = User.get_user_by_id(db, str(current_user.id))
    if not user:
        raise UserNotFound(str(current_user.id))
    return user


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
async def read_all_users(
        db: Session = Depends(get_db),
        page: int = 1,
        page_size: int = 10
):
    users = User.get_all_users(db)
    first = (page - 1) * page_size
    last = first + page_size
    users_model = parse_obj_as(list[user_schemas.User], users)
    response = user_schemas.UserPagination(
        users_model,
        "/api/v1/users",
        first,
        last,
        page,
        page_size
    )
    return response
