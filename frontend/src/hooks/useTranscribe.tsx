import React from "react";
import { io } from "socket.io-client";

//@ts-ignore
import recorderProcessor from "../utils/recorder-processor";
import useLocalStorage from "./useLocalStorage";

interface TranscriptionConfig {
  audio: {
    encoding: string;
    sampleRateHertz: number;
    languageCode: string;
  };
  interimResults: boolean;
}

interface DataRecieved {
  (data: string, isFinal: boolean): void;
}

let audioContext,
  context: AudioContext,
  worklet: AudioWorkletNode,
  input: MediaStreamAudioSourceNode,
  globalStream: MediaStream;
  
const socket = io("http://localhost/" , {
  path: '/sockets/',
});

const useTranscribe = () => {
  const { getLocalStorage } = useLocalStorage();

  const { access_token } = getLocalStorage();

  const mediaConstraints = {
    audio: true,
    video: false,
  };

  const initRecording = async (transcribeConfig: TranscriptionConfig, handleDataRecived: DataRecieved): Promise<void> => {
    socket.emit("startGoogleCloudStream", { ...transcribeConfig }, access_token);

    audioContext = window.AudioContext;
    context = new AudioContext();

    await context.audioWorklet.addModule(recorderProcessor)
      .then( () => {
        worklet = new AudioWorkletNode(context, "recorder.worklet");
        worklet.port.postMessage("ping");
        worklet.connect(context.destination);
      });

    context.resume();

    navigator.mediaDevices.getUserMedia(mediaConstraints)
      .then( (stream) => {
        globalStream = stream;
        
        input = context.createMediaStreamSource(globalStream);
        input.connect(worklet);

        worklet.port.onmessage = (e) => {
          socket.emit("binaryAudioData", e.data);
        };
      });

    if (handleDataRecived) {
      socket.on("speechData", (response) => {
        handleDataRecived(response.data, response.isFinal);
      });
    }
  };

  const stopRecording = (): void => {
    socket.emit("endGoogleCloudStream", access_token);
    closeAll();
  };

  const closeAll = () => {
    socket.off("speechData");

    const tracks:  MediaStreamTrack[] | null = globalStream ? globalStream.getTracks() : null;
    const track = tracks ? tracks[0] : null;

    if (track) {
      track.stop();
    }

    if (worklet) {
      if (input) {
        try {
          input.disconnect(worklet);
        } catch (error) {
          console.warn("Attempt to disconnect input failed.");
        }
      }
      worklet.disconnect(context.destination);
    }

    if (context) {
      context.close()
        .then(() => {
          input = null;
          worklet = null;
          context = null;
          audioContext = null;
        });
      }
  };

  return [initRecording, stopRecording];
};

export default useTranscribe;
