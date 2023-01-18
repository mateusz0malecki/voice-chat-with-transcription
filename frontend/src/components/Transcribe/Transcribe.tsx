import React from "react";

import useTranscribe from "../../hooks/useTranscribe";
import './transcribe.css'

interface TranscriptionConfig {
  audio: {
    encoding: string;
    sampleRateHertz: number;
    languageCode: string;
  };
  interimResults: boolean;
}

const Transribe = ( {isTranscript, leaveAction}: {isTranscript: boolean, leaveAction: boolean}): JSX.Element => {
  const [transcribedData, setTranscribedData] = React.useState([]);
  const [interimTranscribedData, setInterimTranscribedData] = React.useState("");
  const [initRecording, stopRecording] = useTranscribe();

  React.useEffect( () => {
    if (isTranscript) onStart();
  },[isTranscript])

  React.useEffect(() => {
    if(leaveAction) onStop();
  },[leaveAction])

  console.log('leave' , leaveAction)

  const flushInterimData = (): void => {
    if (interimTranscribedData !== "") {
      setInterimTranscribedData("");
      setTranscribedData((prev) => [...prev, interimTranscribedData]);
    }
  };

  const handleDataRecived = (data:string, isFinal: boolean): void => {
    console.log('isFinal' , isFinal)
    if (!isFinal) setInterimTranscribedData(data);

    setInterimTranscribedData("");
    setTranscribedData((prev) => [...prev, data]);
  };

  const getTranscriptionConfig = (): TranscriptionConfig => {
    return {
      audio: {
        encoding: "LINEAR16",
        sampleRateHertz: 16000,
        languageCode: "pl-PL",
      },
      interimResults: true,
    };
  };

  const onStart = (): void => {
    const transcriptionConfig = getTranscriptionConfig();

    setTranscribedData([]);
    initRecording(transcriptionConfig, handleDataRecived);
  };

  const onStop = (): void => {
    const transcriptionConfig = getTranscriptionConfig();
    flushInterimData();
    stopRecording(transcriptionConfig, handleDataRecived);
  };

  return (
    <section className="section__wrap">
      <header className="section__header">
        <h3>Real-time transcription playgroud</h3>
      </header>
      <div className="section__transcription">
        <div className="section__transcription--output">
          {transcribedData.map( (transcription, index) => {
            return (
              <span key={index} className='transcription--output--item'>{transcription}</span>
            )
          })}
        </div>
      </div>
    </section>
  );
};

export default Transribe;
