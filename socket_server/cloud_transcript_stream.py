import os
import asyncio
import queue
import threading
import requests
import json
from typing import Dict
from datetime import datetime

from google.cloud import speech

GOOGLE_SERVICE_JSON_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "sa-key.json")
clients = {}
users = []


class ClientData:
    def __init__(self, transcribe_thread, conn, config: Dict):
        self._buff = queue.Queue()
        self._thread = transcribe_thread
        self._closed = True
        self._conn = conn
        self.general_config = {dict_key: config[dict_key] for dict_key in config if dict_key != 'audio'}
        self.audio_config = config['audio']
        self.transcription_text = ''

    async def close(self, token: str, room: str):
        requests.post(
            url="http://app:8000/api/v1/transcriptions",
            data=json.dumps(
                {
                    "text": self.transcription_text,
                    "roomName": room
                }
            ),
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        self._closed = True
        self._buff.put(None)
        self._thread.join()
        await self._conn.emit('endGoogleCloudStream', '')

    def start_transcribing(self):
        self._closed = False
        self._thread.start()

    def add_data(self, data):
        self._buff.put(data)

    def generator(self):
        while not self._closed:
            chunk = self._buff.get()
            if chunk is None:
                return

            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)

    async def send_client_data(self, data, is_final: bool):
        await self._conn.emit('speechData', {'data': data, 'isFinal': is_final})


async def listen_print_loop(responses, client: ClientData, username):
    """
    Iterates through server responses and sends them back to client.
    The responses passed is a generator that will block until a response is provided by the server.
    """
    num_chars_printed = 0
    interim_flush_counter = 0
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        alternative = result.alternatives[0]
        transcript = alternative.transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))
        text = transcript.lower().strip() + overwrite_chars.lower().strip()

        if not result.is_final:
            interim_flush_counter += 1
            if client and interim_flush_counter % 3 == 0:
                interim_flush_counter = 0
            num_chars_printed = len(transcript)
        else:
            if client:
                timestamp = datetime.utcnow().strftime('%Y/%m/%d, %H:%M:%S')
                words = ''
                timestamps = ''
                for word_info in alternative.words:
                    words += f"{word_info.word.lower()} "
                    timestamps += f"{word_info.start_time.total_seconds()},"
                client.transcription_text += \
                    f"[{timestamp}] - [{username}] - [{timestamps[:-1]}] - {words.strip()}.\n"
                await client.send_client_data(f"[{timestamp}] {username} - {text.capitalize()}.\n", True)
            num_chars_printed = 0


class GoogleSpeechWrapper:
    encoding_map = {'LINEAR16': speech.RecognitionConfig.AudioEncoding.LINEAR16}

    @staticmethod
    async def start_listen(client_id: str, username: str):
        client = clients[client_id]
        speech_client = speech.SpeechClient.from_service_account_json(GOOGLE_SERVICE_JSON_FILE)
        config = speech.RecognitionConfig(
            encoding=GoogleSpeechWrapper.encoding_map[client.audio_config['encoding']],
            sample_rate_hertz=client.audio_config['sampleRateHertz'],
            language_code=client.audio_config['languageCode'],
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True,
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=client.general_config['interimResults']
        )
        audio_generator = client.generator()
        requests_google = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
        responses_google = speech_client.streaming_recognize(streaming_config, requests_google)
        await listen_print_loop(responses_google, client, username)

    @staticmethod
    async def start_recognition_stream(sio, client_id: str, config: Dict, token: str, room: str):
        user_response = requests.get(
            url="http://app:8000/api/v1/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        if user_response.status_code == 200:
            email = user_response.json()["email"]
            username = user_response.json()["name"]
            if email not in users:
                if client_id not in clients:
                    users.append(email)
                    clients[client_id] = ClientData(
                        threading.Thread(
                            target=asyncio.run,
                            args=(GoogleSpeechWrapper.start_listen(client_id, username),)
                        ),
                        sio,
                        config
                    )
                    clients[client_id].start_transcribing()
                    response = requests.get(
                        url=f"http://app:8000/api/v1/rooms/info/{room}",
                        headers={
                            "Authorization": f"Bearer {token}"
                        }
                    )
                    if response.status_code == 404:
                        requests.post(
                            url=f"http://app:8000/api/v1/rooms",
                            headers={
                                "Authorization": f"Bearer {token}"
                            },
                            data=json.dumps(
                                {
                                    "name": room
                                }
                            )
                        )
                    elif response.status_code == 200:
                        requests.put(
                            url=f"http://app:8000/api/v1/rooms/{room}",
                            headers={
                                "Authorization": f"Bearer {token}"
                            }
                        )
                else:
                    print('Warning - already running transcription for client')
            else:
                print('Warning - already running transcription for user')
        else:
            print('Not authenticated.')

    @staticmethod
    async def stop_recognition_stream(client_id: str, token: str, room: str):
        response = requests.get(
            url="http://app:8000/api/v1/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        if response.status_code == 200:
            email = response.json()["email"]
            if email in users:
                if client_id in clients:
                    await clients[client_id].close(token, room)
                    del clients[client_id]
                    users.remove(email)

    @staticmethod
    def receive_data(client_id: str, data):
        if client_id not in clients:
            return
        clients[client_id].add_data(data)
