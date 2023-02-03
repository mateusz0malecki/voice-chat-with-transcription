import json
import pytest
from settings import get_settings

app_settings = get_settings()


@pytest.mark.xfail
def test_empty_db_rooms(client):
    response = client.get(f'{app_settings.root_path}/rooms')
    assert len(response.json()["records"]) == 10


def test_upload_room(client):
    data_user = {
        "name": "name",
        "email": "email@email.com",
        "password": "password"
    }
    client.post(f'{app_settings.root_path}/register', json.dumps(data_user))

    data_room = {"name": "test"}
    response = client.post(f'{app_settings.root_path}/rooms', json.dumps(data_room))

    data = {
        "text": "Test test 123.",
        "roomName": "test"
    }
    client.post(f'{app_settings.root_path}/transcriptions', json.dumps(data))

    file_path = "tests/test-audio.wav"
    with open(file_path, "rb") as f:
        client.post(
            f"{app_settings.root_path}/recordings-file",
            files={"file": f},
            data={"room_name": "test"}
        )
    assert response.status_code == 201


def test_get_all_rooms(client):
    response = client.get(f'{app_settings.root_path}/rooms')
    assert response.status_code == 200
    assert len(response.json()["records"]) == 1


def test_get_room(client):
    response = client.get(f'{app_settings.root_path}/rooms/test')
    assert response.status_code == 200
    assert response.json()["name"] == "test"
    assert response.json()["recordings"][0]["duration"] == 1.542108843537415
    assert response.json()["transcriptions"] is not None
    assert len(response.json()["users"]) == 1


def test_delete_room(client):
    response = client.delete(f'{app_settings.root_path}/rooms/test')
    assert response.status_code == 204
    transcriptions = client.get(f'{app_settings.root_path}/transcriptions').json()["records"]
    recordings = client.get(f'{app_settings.root_path}/recordings').json()["records"]
    assert len(transcriptions) == 0
    assert len(recordings) == 0
