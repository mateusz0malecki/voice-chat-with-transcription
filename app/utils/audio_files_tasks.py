from fastapi import HTTPException, status
import soundfile as sf
from librosa import get_duration
from pydub import AudioSegment

import subprocess
import os
from datetime import datetime


def convert_and_save_file(browser: str, file: bytes, room_name: str, number: int):
    """
    Converts and saves given audio file in bytes to WAV audio extension.
    """
    dir_ = f"data/recordings/"
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    filename = f"{datetime.now().strftime('%d-%m-%Y')}-{room_name}-{str(number+1)}.wav"
    final_file_location = f"{dir_}/{filename}"

    if browser == "chrome":
        temp_file_location = f"data/temp/{filename}.webm"
        with open(temp_file_location, "wb+") as file_object:
            file_object.write(file)
        command = ['ffmpeg', "-y", '-i', temp_file_location, final_file_location]
        subprocess.run(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    elif browser == "firefox":
        temp_file_location = f"data/temp/{filename}.ogg"
        with open(temp_file_location, "wb+") as file_object:
            file_object.write(file)
        data, samplerate = sf.read(temp_file_location)
        sf.write(final_file_location, data, samplerate)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported browser.")

    try:
        duration = get_duration(filename=final_file_location)
    except Exception as e:
        os.remove(temp_file_location)
        raise HTTPException(status_code=400, detail={"info": f"Broken file: {e}"})

    os.remove(temp_file_location)
    return filename, final_file_location, duration


def convert_to_wav_and_save_file(filepath: str, filename: str):
    """
    Converts audio file to WAV extension.
    """
    extension_list = ("mp4", "mp3", "m4a")
    dir_ = f"data/recordings/"
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    for extension in extension_list:
        if filename.lower().endswith(extension):
            audio = AudioSegment.from_file(filepath + filename, extension)
            new_audio = audio.set_frame_rate(frame_rate=16000)
            new_filename = f"{filename.split('.')[0]}.wav"
            new_filepath = f"{dir_}{new_filename}"
            new_audio.export(new_filepath, format="wav")
            duration = get_duration(filename=new_filepath)
            return new_filename, duration

    os.remove(filepath + filename)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file extension.")


def delete_audio_file(filepath):
    """
    Deletes temp file created for partial audio response.
    """
    if os.path.exists(filepath):
        os.remove(filepath)
