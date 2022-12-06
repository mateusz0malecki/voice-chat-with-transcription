from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import transcriptions, auth, recordings, users
from settings import get_settings

app_settings = get_settings()


def create_app():
    # Settings
    settings = get_settings()

    # FastAPI
    app = FastAPI(
        docs_url=f"{settings.root_path}/docs",
        version="1.0.0",
        openapi_url=f"{settings.root_path}"
    )
    app.include_router(transcriptions.router)
    app.include_router(auth.router)
    app.include_router(recordings.router)
    app.include_router(users.router)

    # CORS middleware
    origins = [
        "*"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
