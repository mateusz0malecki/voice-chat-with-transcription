from fastapi import APIRouter, Depends, status, HTTPException, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from datetime import timedelta
from typing import Any
from secrets import token_urlsafe

from schemas import token_schemas, user_schemas
from db.database import get_db
from auth.jwt_helper import authenticate_user, create_token, ACCESS_TOKEN_EXPIRE_MINUTES
from exceptions.exceptions import CredentialsException
from models.user import User, ResetPassword
from auth.sending_email import send_email_reset_password
from auth.hash import Hash
from settings import get_settings

app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Auth"])


@router.post(
    '/login',
    response_model=token_schemas.Token
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise CredentialsException
    access_token = create_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token}


@router.post(
    "/register",
    response_model=user_schemas.User | Any,
    status_code=status.HTTP_201_CREATED
)
async def register(
        response: Response,
        request: user_schemas.UserCreate,
        db: Session = Depends(get_db),
):
    created_user = User(**request.dict())
    try:
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        return created_user
    except IntegrityError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Email is already used, try again.",
            "error": e
        }


@router.post(
    '/forgot-password',
    status_code=status.HTTP_200_OK
)
async def forgot_password(
        request: user_schemas.ForgotPassword,
        db: Session = Depends(get_db),
):
    user = User.get_user_by_email(db, request.email).first()
    if not user:
        pass
    else:
        token_in_db = ResetPassword.get_unused_by_email(db, user.email)
        if token_in_db:
            reset_code = token_in_db.reset_code
        else:
            reset_code = token_urlsafe(16)
            code_in_db = ResetPassword(
                email=user.email,
                reset_code=reset_code
            )
            db.add(code_in_db)
            db.commit()
            db.refresh(code_in_db)
        await send_email_reset_password(email=[user.email], reset_code=reset_code)
    return {"info": "If we found an account associated with that email, we've sent a password reset message."}


@router.put(
    '/reset-password',
    status_code=status.HTTP_202_ACCEPTED

)
async def reset_password(
        request: user_schemas.ResetPassword,
        db: Session = Depends(get_db)
):
    reset_token = ResetPassword.get_unused_by_reset_code(db, request.reset_password_token)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reset password token has expired, please request a new one."
        )
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passwords do not match."
        )
    user = User.get_user_by_email(db, reset_token.email).first()
    if not user:
        pass
    else:
        user.password = Hash.get_password_hash(request.new_password)
        reset_token.status = True
        db.commit()
        db.refresh(user)
        db.refresh(reset_token)
    return {"info": "Password has been changed."}