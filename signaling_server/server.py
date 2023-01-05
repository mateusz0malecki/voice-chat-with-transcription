import socketio
from aiohttp import web

from speech_wrapper import GoogleSpeechWrapper

app = web.Application()
sio = socketio.AsyncServer(cors_allowed_origins='*')

sio.attach(app)


@sio.on('join')
def join(sid, username, room):
    sio.enter_room(sid, room)
    print(f'RoomEvent: {username} has joined the room {room}\n')
    sio.emit('ready', {username: username}, to=room, skip_sid=sid)


@sio.on('data')
def transfer_data(sid, username, room, data):
    print(f'DataEvent: {username} has sent the data:\n {data}\n')
    sio.emit('data', data, to=room, skip_sid=sid)


@sio.on('leave')
def leave(sid, username, room):
    sio.leave_room(sid, room)
    print(f'RoomEvent: {username} has left the room {room}\n')
    sio.emit('leave', {username: username}, to=room, skip_sid=sid)


@sio.on('startGoogleCloudStream')
async def start_google_stream(sid, config):
    print(f'Starting streaming audio data from client {sid}')
    await GoogleSpeechWrapper.start_recognition_stream(sio, sid, config)


@sio.on('binaryAudioData')
async def receive_binary_audio_data(sid, message):
    # print('mes' , message, sid)
    GoogleSpeechWrapper.receive_data(sid, message)


@sio.on('endGoogleCloudStream')
async def close_google_stream(sid):
    print(f'Closing streaming data from client {sid}')
    await GoogleSpeechWrapper.stop_recognition_stream(sid)


if __name__ == '__main__':
    web.run_app(app, host="0.0.0.0", port=9000)