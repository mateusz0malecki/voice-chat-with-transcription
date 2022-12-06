from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import timedelta, datetime

from schemas import token_schemas
from db.database import get_db
from models.user import User
from auth.hash import Hash
from exceptions.exceptions import CredentialsException
from settings import get_settings


router = APIRouter(tags=["Auth"])
app_settings = get_settings()

SECRET_KEY = app_settings.secret_key
ALGORITHM = app_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(app_settings.access_token_expire_minutes)

auth_scheme = OAuth2PasswordBearer(tokenUrl='login')


def authenticate_user(
        email: str,
        password: str,
        db: Session = Depends(get_db)
):
    user = User.get_user_by_email(db, email)
    if not user:
        return False
    if not Hash.verify_password(password, user.password):
        return False
    return user


def create_token(data: dict, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
        token: str = Depends(auth_scheme),
        db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise CredentialsException
        token_data = token_schemas.TokenData(email=email)
    except JWTError:
        raise CredentialsException
    user = User.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise CredentialsException
    return user
