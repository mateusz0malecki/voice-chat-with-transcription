import os
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from dotenv import load_dotenv

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


@socketio.on_error_default
def default_error_handler(e):
    print(f"Error: {e}")
    socketio.stop()


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=9000)
