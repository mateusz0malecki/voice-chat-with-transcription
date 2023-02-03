import os
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'sa-key.json'
speech_client = speech.SpeechClient()


def transcript_small_local_file_gcp(media_file_name):
    """
    Uses Google speech-to-text to transcript local file that is shorter than 60 sec and weights less than 10MB.
    :param: media_file_name: path to local file
    :return: transcript text and Google total billed time
    """
    with open(media_file_name, 'rb') as f1:
        byte_data_wav = f1.read()

    details_audio = dict(content=byte_data_wav)
    audio = speech.RecognitionAudio(details_audio)

    details_config = dict(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="pl-PL",
        enable_automatic_punctuation=True,
        model='default',
        enable_word_time_offsets=True,
    )
    config = speech.RecognitionConfig(details_config)
    response = speech_client.recognize(config=config, audio=audio)
    return response


def transcript_big_bucket_file_gcp(media_uri):
    """
    Uses Google speech-to-text to transcript file that is longer than 60 sec or weights more than 10MB.
    File has to be uploaded to Cloud Storage bucket.
    :param: media_uri: URI to file sored in Cloud Storage Bucket
    :return: transcript text and Google total billed time
    """
    audio = speech.RecognitionAudio(uri=media_uri)
    detail_config = dict(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="pl-PL",
        enable_automatic_punctuation=True,
        use_enhanced=True,
        model='latest_long',
        audio_channel_count=1,
        enable_word_time_offsets=True,
    )
    config = speech.RecognitionConfig(detail_config)
    operation = speech_client.long_running_recognize(config=config, audio=audio)
    response = operation.result()
    return response
