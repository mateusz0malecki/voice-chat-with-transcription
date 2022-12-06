from datetime import datetime
from typing import Optional, Any
from pydantic import EmailStr

from auth.hash import Hash
from .helpers import CustomPagination, BaseConfig


class UserBase(BaseConfig):
    email: EmailStr


class ForgotPassword(BaseConfig):
    email: EmailStr


class ResetPassword(BaseConfig):
    reset_password_token: str
    new_password: str
    confirm_password: str


class User(UserBase):
    name: str
    id: int


class UserDetail(User):
    updated_at: Optional[datetime]
    created_at: Optional[datetime]


class UserCreate(UserBase):
    name: str
    password: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.password = Hash.get_password_hash(self.password)


class UserPagination(CustomPagination):
    records: list[User] = []
