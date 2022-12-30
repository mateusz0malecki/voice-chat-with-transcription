import React from "react";
import { io } from "socket.io-client";

const useTranscribe = () => {
  let bufferSize: 2048,
    audioContext,
    context: AudioContext,
    worklet: AudioWorkletNode,
    input: MediaStreamAudioSourceNode,
    globalStream: MediaStream

  const socket = io("http://localhost:9000");

  const mediaConstraints = {
    audio: true,
    video: false
  };

  let url_worklet = URL.createObjectURL( new Blob([ '(', function(){

    class WorkletProcessor extends AudioWorkletProcessor {
      constructor () { 
        super();
      }
      
      process(inputs, outputs) {

        // console.log('in' , inputs)

        if (!inputs || !inputs[0] || !inputs[0][0]) {
          return true;
        }
  
        const left = inputs[0][0];
        // console.log('left' , left ); // the onaudioprocess code here

        const convertFloat32ToInt16 = (buffer) => {
          let l = buffer.length;
          let buf = new Int16Array(l / 3);

          while (l--) {
            if (l % 3 === 0) {
              buf[l / 3] = buffer[l] * 0xffff;
            }
          }
          return buf.buffer;
        }; 

        const left16 = convertFloat32ToInt16(left);
        
        this.port.onmessage = (e) => {
          console.log('e1' , e.data);
          this.port.postMessage(left16);
        };

        return true; 
      }
    }
    registerProcessor('worklet-processor', WorkletProcessor);
  
  }.toString(), ')()' ], { type: 'application/javascript' } ) );




  const initRecording = async (transcribeConfig, onData, onError) => {
    socket.emit("startGoogleCloudStream", { ...transcribeConfig });

    audioContext = window.AudioContext || window.webkitAudioContext;

    context = new AudioContext();

    await context.audioWorklet.addModule( url_worklet ).then(() => {
      // console.log("Audio worklet module loaded successfully.");


      worklet = new AudioWorkletNode(context, "worklet-processor");

      // worklet.port.postMessage('ping');

      setInterval(() => worklet.port.postMessage('ping'), 1000);
      worklet.port.onmessage = (e) => console.log('1dsadas' , e.data);

      // console.log("AudioWorkletNode created successfully.");
      
      worklet.connect(context.destination);

      // const source = context.createBufferSource();
      // source.connect(worklet);
      // source.start();
    });

    context.resume();


    navigator.permissions.query({name: 'microphone'}).then((result) => {
        if (result.state === 'granted') {
          navigator.mediaDevices.getUserMedia(mediaConstraints).then((stream) => {
            // console.log("AudioWorkletNode connected to audio graph.");
            globalStream = stream;

            input = context.createMediaStreamSource(globalStream);
            
            input.connect(worklet);
            
            worklet.port.onmessage = (e) => {
              console.log("Received audio data: ", e.data);
              console.log("worklet.port.onmessage event handler called.");
              // microphoneProcess(e);

              socket.emit("binaryAudioData", e.data);
            };

            // console.log('wor' , worklet)

          });
        } else {
          console.error('Permission denied');
        }
      });


    if (onData) {
      console.log('on' , onData)
      socket.on("speechData", (data) => {
        console.log('resp' , data)
        onData(response.data, response.isFinal);
      });
    }

    socket.on("googleCloudStreamError", (error) => {
      if (onError) {
        console.log('rr')
        onError("error");
      }
      console.log('dada')
      closeAll();
    });

    socket.on("endGoogleCloudStream", () => {
      closeAll();
    });
  };

  const stopRecording = () => {
    socket.emit("endGoogleCloudStream");
    closeAll();
  };

  // const microphoneProcess = (e) => {
  //   console.log('e')
  //   const left = e.inputBuffer.getChannelData(0);
  //   const left16 = convertFloat32ToInt16(left);
  //   socket.emit("binaryAudioData", left16);
  // };

  // const convertFloat32ToInt16 = (buffer) => {
  //   let l = buffer.length;
  //   let buf = new Int16Array(l / 3);

  //   while (l--) {
  //     if (l % 3 === 0) {
  //       buf[l / 3] = buffer[l] * 0xffff;
  //     }
  //   }
  //   return buf.buffer;
  // };

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
        audioContext = null
      });
    }
  };

  return [initRecording, closeAll, stopRecording];
};

export default useTranscribe;
