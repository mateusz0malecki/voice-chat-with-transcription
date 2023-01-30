import React from 'react';
import { useParams } from "react-router-dom";

import { detectBrowserName } from '@/helpers/browserDetect'
import useFetch from './useFetch';

export interface MediaRecorderData {
    startRecordingAudio: () => void;
    stopRecordingAudio: () => void;
    playRecord: () => void;
    prepereRecord: () => Blob;
    clearMediaRecorderState: () => void;
}

const useMediaRecorder = (): MediaRecorderData => {
    const [mediaRecorder, setMediaRecorder] = React.useState<MediaRecorder>(new MediaRecorder(new MediaStream()));
    const [audioBlob, setAudioBlob] = React.useState<Blob>(null);
    const [audioUrl, setAudioUrl] = React.useState('');

    const params = useParams();
    const { room } = params;
    const { sendRecord } = useFetch();

    const constraints = { audio: true, video: false };
    const browserName = detectBrowserName();
    
    React.useEffect(() => {
        recorderInit();
    }, [])

    const recorderInit = (): void => {
        if (!navigator.mediaDevices) return;

        navigator.mediaDevices.getUserMedia(constraints)
            .then((stream) => {
                let newChunks: BlobPart[] = []
                console.log('newChunks' , newChunks)
                let newMediaRecorder: MediaRecorder;
                console.log('newMediaRec', newMediaRecorder)

                if (browserName === 'firefox') {
                    newMediaRecorder = new MediaRecorder(stream, {mimeType:'audio/ogg;codecs=opus'})
                } else if(browserName === 'safari') {
                    newMediaRecorder = new MediaRecorder(stream, {mimeType:'audio/mp4;codecs=opus'})
                } else {
                    newMediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
                }

                newMediaRecorder.addEventListener('dataavailable', event => {
                    console.log('dataavailable' , event.data)
                    const data = event.data;

                    if (data && data.size > 0) newChunks.push(data);
                });

                newMediaRecorder.addEventListener('stop', () => {
                    console.log('stop')
                    const newBlob = new Blob(newChunks, { type: newMediaRecorder.mimeType });
                    const newAudioUrl = URL.createObjectURL(newBlob);
                    
                    console.log('newBlob' , newBlob)
                    const recordData = new FormData();
                    recordData.append('room_name' , room);
                    recordData.append('browser' , browserName);
                    recordData.append('file' , newBlob);
                    sendRecord(recordData)

                    setAudioBlob(newBlob);
                    setAudioUrl(newAudioUrl);
                    newChunks = []
                })
                setMediaRecorder(newMediaRecorder);
            });
    };

    const startRecordingAudio = (): void => {
        mediaRecorder.start();
    }

    const stopRecordingAudio = (): void => {
        mediaRecorder.stop();
    }

    const playRecord = (): void => {
        const audio = new Audio(audioUrl);
        audio.play();
    }

    const clearMediaRecorderState = (): void => {
        setAudioUrl('');
        setAudioBlob(null);
    }

    const prepereRecord = (): Blob => {
        return audioBlob;
    }

    return { startRecordingAudio, stopRecordingAudio, playRecord, prepereRecord, clearMediaRecorderState }
}

export default useMediaRecorder;


