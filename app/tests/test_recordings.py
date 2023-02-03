import os
import json
import pytest
from settings import get_settings

app_settings = get_settings()


@pytest.mark.xfail
def test_empty_db_recordings(client):
    response = client.get(f'{app_settings.root_path}/recordings')
    assert len(response.json()["records"]) == 1


def test_upload_recording_file(client):
    data_user = {
        "name": "name",
        "email": "email@email.com",
        "password": "password"
    }
    client.post(f'{app_settings.root_path}/register', json.dumps(data_user))

    data_room = {"name": "test"}
    client.post(f'{app_settings.root_path}/rooms', json.dumps(data_room))

    file_path = "tests/test-audio.wav"
    with open(file_path, "rb") as f:
        response = client.post(
            f"{app_settings.root_path}/recordings-file",
            files={"file": f},
            data={"room_name": "test"}
        )
    assert response.status_code == 201
    assert len(response.json()["info"]) == 37


def test_get_recording(client):
    response_info = client.get(f'{app_settings.root_path}/recordings/1')
    assert response_info.status_code == 200
    assert response_info.json()["duration"] == 1.542108843537415
    filename = response_info.json()["filename"]
    response_file = client.get(f'api/v1/recordings/file/{filename}')
    assert response_file.headers["content-type"] == "audio/wav"


def test_get_all_recordings(client):
    response = client.get(f'{app_settings.root_path}/recordings')
    assert response.status_code == 200
    assert len(response.json()["records"]) == 1


def test_delete_recording(client):
    filename = client.get(f'{app_settings.root_path}/recordings/1').json()["filename"]
    response = client.delete(f'{app_settings.root_path}/recordings/1')
    assert response.status_code == 204
    assert os.path.exists(f'{app_settings.recordings_path}{filename}') is False
