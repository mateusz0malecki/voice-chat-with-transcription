import json
import pytest
from settings import get_settings

app_settings = get_settings()


@pytest.mark.xfail
def test_empty_db_users(client):
    response = client.get(f'{app_settings.root_path}/users')
    assert len(response.json()["records"]) == 1


def test_register(client):
    data = {
        "name": "name",
        "email": "email@email.com",
        "password": "password"
    }
    response = client.post(f'{app_settings.root_path}/register', json.dumps(data))
    assert response.status_code == 201
    assert response.json()["name"] == "name"


def test_get_users(client):
    response = client.get(f'{app_settings.root_path}/users')
    assert response.status_code == 200
    assert len(response.json()["records"]) == 1


def test_me(client):
    response = client.get(f'{app_settings.root_path}/me')
    assert response.status_code == 200
    assert response.json()["email"] == "email@email.com"
