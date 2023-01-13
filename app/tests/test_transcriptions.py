import json
import os
import pytest
from settings import get_settings

app_settings = get_settings()


@pytest.mark.xfail
def test_empty_db_transcriptions(client):
    response = client.get(f'{app_settings.root_path}/transcriptions')
    assert len(response.json()["records"]) == 1


def test_save_stream_transcription(client):
    data = {"text": "Test test 123."}
    response = client.post(f'{app_settings.root_path}/transcriptions', json.dumps(data))
    assert response.status_code == 201


def test_get_transcription(client):
    response_info = client.get(f'{app_settings.root_path}/transcriptions/1')
    assert response_info.status_code == 200
    filename = response_info.json()["filename"]
    response_file = client.get(f'/transcriptions/file/{filename}')
    assert response_file.headers["content-type"] == "application/json"


def test_get_all_transcriptions(client):
    response = client.get(f'{app_settings.root_path}/transcriptions')
    assert response.status_code == 200
    assert len(response.json()["records"]) == 1


def test_delete_transcription(client):
    filename = client.get(f'{app_settings.root_path}/transcriptions/1').json()["filename"]
    response = client.delete(f'{app_settings.root_path}/transcriptions/1')
    assert response.status_code == 204
    assert os.path.exists(f'{app_settings.transcriptions_path}{filename}') is False
