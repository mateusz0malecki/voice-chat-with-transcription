from fastapi import HTTPException, status


class UserNotFound(HTTPException):
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found."
        )


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"}
        )


class RecordingNotFound(HTTPException):
    def __init__(self, recording_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording with id '{recording_id}' not found."
        )


class TranscriptionNotFound(HTTPException):
    def __init__(self, transcription_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transcription with id '{transcription_id}' not found."
        )


class RoomNotFound(HTTPException):
    def __init__(self, room_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with name '{room_name}' not found."
        )
