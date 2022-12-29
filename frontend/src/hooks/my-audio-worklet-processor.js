class MyAudioWorkletProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
  }

  process(inputs, outputs) {
    console.log("process method called");

    const left = inputs[0][0];
    console.log("le", left);
    console.log("out", outputs);
    const processedAudioData = convertFloat32ToInt16(left);

    console.log("log", processedAudioData);

    socket.emit("binaryAudioData", processedAudioData);

    return true;
  }
}

// Make sure that the AudioWorklet API is available before trying to register the processor
if (window.AudioWorklet) {
    console.log('si')
  AudioWorklet.registerProcessor(
    "my-audio-worklet-processor",
    MyAudioWorkletProcessor
  );
} else {
  console.error("The Web Audio API is not available");
}

function convertFloat32ToInt16(buffer) {
  let l = buffer.length;
  let buf = new Int16Array(l / 3);

  while (l--) {
    if (l % 3 === 0) {
      buf[l / 3] = buffer[l] * 0xffff;
    }
  }
  return buf.buffer;
}
