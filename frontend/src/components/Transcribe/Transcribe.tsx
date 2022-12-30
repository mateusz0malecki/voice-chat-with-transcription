import React from 'react';

import useTranscribe from '../../hooks/useTranscribe';


const Transribe = () => {
  const [transcribedData, setTranscribedData] = React.useState([]);
  const [interimTranscribedData, setInterimTranscribedData] = React.useState('');
  const [isRecording, setIsRecording] = React.useState(false);

  const [ initRecording, closeAll, stopRecording ] = useTranscribe()

  // console.log('a' , transcribedData);
  // console.log('b', interimTranscribedData)

    const flushInterimData = () => {
      if(interimTranscribedData !== '') {
        setInterimTranscribedData('');
        setTranscribedData( prev => [...prev, interimTranscribedData] );
      }
    }

    const handleDataRecived = (data, isFinal) => {
      if(!isFinal) setInterimTranscribedData(data);

      setInterimTranscribedData('');
      setTranscribedData( prev => [...prev, data] );
    }

    const getTranscriptionConfig = () => {
      return {
        audio: {
          encoding: 'LINEAR16',
          sampleRateHertz: 16000,
          languageCode: 'pl-PL',
        },
        interimResults: true
      }
    }
    
    const onStart = () => {
      const transcriptionConfig = getTranscriptionConfig();

      setTranscribedData([]);
      setIsRecording(true);
      initRecording(transcriptionConfig, handleDataRecived, (error) => {
        console.error('Error when transcribing', error);
        setIsRecording(false)
      });
    }

    const onStop = () => {
      setIsRecording(false);
      flushInterimData();
      stopRecording();
    }

    return (
        <section className='secton'>
          <header className='section__header'>
            <h3>
              Real-time transcription playgroud
            </h3>
          </header>

          <div className='section_buttons'>
            {!isRecording && <button onClick={onStart}>Start</button>}
            {isRecording && <button onClick={onStop}>Stop</button>}
          </div>
          <div className='section__transcription'>
            <p>{transcribedData}</p>
            <p className='section__transcription--output'>{interimTranscribedData}</p>
          </div>
        </section>
    );
}

export default Transribe;