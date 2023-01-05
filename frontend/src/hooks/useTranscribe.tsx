import React from "react";
import { io } from "socket.io-client";

import recorderProcessor from "../utils/recorder-processor";

let audioContext,
  context: AudioContext,
  worklet: AudioWorkletNode,
  input: MediaStreamAudioSourceNode,
  globalStream: MediaStream;

const useTranscribe = () => {
  const socket = io("http://localhost:9000");

  const mediaConstraints = {
    audio: true,
    video: false,
  };

  const initRecording = async (transcribeConfig, onData, onError) => {
    socket.emit("startGoogleCloudStream", { ...transcribeConfig });

    audioContext = window.AudioContext || window.webkitAudioContext;

    context = new AudioContext();

    await context.audioWorklet.addModule(recorderProcessor).then(() => {
      // console.log("Audio worklet module loaded successfully.");

      worklet = new AudioWorkletNode(context, "recorder.worklet");
      worklet.port.postMessage("ping");
      // console.log("AudioWorkletNode created successfully.");

      worklet.connect(context.destination);
    });

    context.resume();

    navigator.mediaDevices.getUserMedia(mediaConstraints).then((stream) => {
      // console.log("AudioWorkletNode connected to audio graph.");
      globalStream = stream;

      input = context.createMediaStreamSource(globalStream);
      input.connect(worklet);

      worklet.port.onmessage = (e) => {
        // console.log("Received audio data: ", e.data);
        // console.log("worklet.port.onmessage event handler called.");
        socket.emit("binaryAudioData", e.data);
      };
    });

    if (onData) {
      socket.on("speechData", (response) => {
        onData(response.data, response.isFinal);
      });
    }

    socket.on("googleCloudStreamError", (error) => {
      if (onError) {
        onError("error");
      }
      closeAll();
    });

    socket.on("endGoogleCloudStream", () => {
      closeAll();
    });
  };

  const stopRecording = () => {
    closeAll();
    socket.emit("endGoogleCloudStream");
  };

  const closeAll = () => {
    socket.off("speechData");
    socket.off("googleCloudStreamError");

    const tracks = globalStream ? globalStream.getTracks() : null;
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
      context.close().then(() => {
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
