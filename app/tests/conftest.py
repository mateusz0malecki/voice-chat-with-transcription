import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db.database import Base, get_db
from models.user import User
from auth.jwt_helper import get_current_user


async def avoid_token():
    return User(
        id=1,
        name="name",
        email="email@email.com",
        password="password",
        updated_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    if not database_exists(SQLALCHEMY_DATABASE_URL):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    yield engine
    drop_database(SQLALCHEMY_DATABASE_URL)


@pytest.fixture(scope="module")
def db(db_engine):
    connection = db_engine.connect()
    connection.begin()
    db = SessionTesting(bind=connection)
    yield db
    db.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = avoid_token
    with TestClient(app) as c:
        yield c
