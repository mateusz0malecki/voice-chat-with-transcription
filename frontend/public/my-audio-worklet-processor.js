// import { IAudioWorkletProcessor } from "standardized-audio-context";

// class MyAudioWorkletProcessor implements AudioWorkletProcessor {
//   process(inputs, outputs) {
//     const gain = this.parameters.get("gain");
//     const input = inputs[0];
//     const output = outputs[0];

//     for (let i = 0; i < input.length; i++) {
//       output[i] = input[i] * gain;
//     }

//     return true;
//   }
// }

registerProcessor('my-audio-worklet-processor', class extends AudioWorkletProcessor {
    constructor() { super(); }
    process(inputs, outputs) {
        let output = outputs[0][0];
        for(let i=0; i<output.length; ++i) output[i]=2*Math.random()-1;
        return true;
    }
});