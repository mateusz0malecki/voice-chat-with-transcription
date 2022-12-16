import os
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from dotenv import load_dotenv
from speech_wrapper import GoogleSpeechWrapper

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('join')
def join(message):
    username = message.get('username')
    room = message.get('room')
    join_room(room)
    print(f'RoomEvent: {username} has joined the room {room}\n')
    emit('ready', {username: username}, to=room, skip_sid=request.sid)


@socketio.on('data')
def transfer_data(message):
    username = message.get('username')
    room = message.get('room')
    data = message.get('data')
    print(f'DataEvent: {username} has sent the data:\n {data}\n')
    emit('data', data, to=room, skip_sid=request.sid)


@socketio.on('leave')
def leave(message):
    username = message.get('username')
    room = message.get('room')
    leave_room(room)
    print(f'RoomEvent: {username} has left the room {room}\n')
    emit('leave', {username: username}, to=room, skip_sid=request.sid)


@socketio.on('startGoogleCloudStream')
async def start_google_stream(message):
    config = message.get('config')
    print(f'Starting streaming audio data from client {request.sid}')
    await GoogleSpeechWrapper.start_recognition_stream(socketio, request.sid, config)


@socketio.on('binaryAudioData')
async def receive_binary_audio_data(message):
    data = message.get('data')
    GoogleSpeechWrapper.receive_data(request.sid, data)


@socketio.on('endGoogleCloudStream')
async def close_google_stream():
    print(f'Closing streaming data from client {request.sid}')
    await GoogleSpeechWrapper.stop_recognition_stream(request.sid)


@socketio.on_error_default
def default_error_handler(e):
    print(f"Error: {e}")
    socketio.stop()


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=9000)
