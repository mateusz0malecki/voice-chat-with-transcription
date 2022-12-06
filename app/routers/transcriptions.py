from fastapi import APIRouter, status, Depends, HTTPException
from db.database import get_db
from sqlalchemy.orm import Session

from models.user import User
from models.transcription import Transcription
from models.recording import Recording
from auth.jwt_helper import get_current_user
from settings import get_settings

app_settings = get_settings()
router = APIRouter(prefix=f"{app_settings.root_path}", tags=["Samples"])
