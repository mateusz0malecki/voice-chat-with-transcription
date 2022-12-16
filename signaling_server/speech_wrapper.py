import asyncio
import queue
import sys
import threading
from typing import Dict

from google.cloud import speech

from settings import GOOGLE_SERVICE_JSON_FILE

clients = {}


class ClientData:
    def __init__(self, transcribe_thread, conn, config: Dict):
        self._buff = queue.Queue()
        self._thread = transcribe_thread
        self._closed = True
        self._conn = conn
        self.general_config = {dict_key: config[dict_key] for dict_key in config if dict_key != 'audio'}
        self.audio_config = config['audio']

    async def close(self):
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


async def listen_print_loop(responses, client: ClientData):
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
        transcript = result.alternatives[0].transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            interim_flush_counter += 1

            if client and interim_flush_counter % 3 == 0:
                interim_flush_counter = 0
                await client.send_client_data(transcript + overwrite_chars + "\r", False)
            num_chars_printed = len(transcript)
        else:
            text = transcript + overwrite_chars
            print(text)

            if client:
                await client.send_client_data(text, True)
            num_chars_printed = 0


class GoogleSpeechWrapper:
    encoding_map = {'LINEAR16': speech.RecognitionConfig.AudioEncoding.LINEAR16}

    @staticmethod
    async def start_listen(client_id: str):
        client = clients[client_id]
        speech_client = speech.SpeechClient.from_service_account_json(GOOGLE_SERVICE_JSON_FILE)
        config = speech.RecognitionConfig(
            encoding=GoogleSpeechWrapper.encoding_map[client.audio_config['encoding']],
            sample_rate_hertz=client.audio_config['sampleRateHertz'],
            language_code=client.audio_config['languageCode'],
            enable_automatic_punctuation=True
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=client.general_config['interimResults']
        )
        audio_generator = client.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
        responses = speech_client.streaming_recognize(streaming_config, requests)
        await listen_print_loop(responses, client)

    @staticmethod
    async def start_recognition_stream(sio, client_id: str, config: Dict):
        if client_id not in clients:
            clients[client_id] = ClientData(
                threading.Thread(
                    target=asyncio.run,
                    args=(GoogleSpeechWrapper.start_listen(client_id),)
                ),
                sio,
                config
            )
            clients[client_id].start_transcribing()
        else:
            print('Warning - already running transcription for client')

    @staticmethod
    async def stop_recognition_stream(client_id: str):
        if client_id in clients:
            await clients[client_id].close()
            del clients[client_id]

    @staticmethod
    def receive_data(client_id: str, data):
        if client_id not in clients:
            return
        clients[client_id].add_data(data)
