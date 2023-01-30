import React from 'react';

import Nav from '@/components/Nav/Nav'
import useFetch from '@/hooks/useFetch';

const AudioAndTranscription = () => {
    const { getTranscription } = useFetch();

    React.useEffect(() => {
        // const filename = '891ec464-6dcd-4073-9038-8d62c3908ab4'
        // const abc = getTranscription();
        // console.log('abc' , abc)
        getAllTranscription()
    },[])

    const getAllTranscription = async () => {
        const abc = await getTranscription();
        console.log('abc' , abc)
    }

    const transcriptionsAndAudiosArray: any[] = []

    return (
        <div className='wrap'>
            <Nav />
            <h1>AAA</h1>

            {transcriptionsAndAudiosArray.map( transcriptionData => {
                const { id, transcription, audioBlob } = transcriptionData;

                const audioUrl = URL.createObjectURL(audioBlob);

                return (
                    <div key={id}>   
                
                    </div>
                )
            })}
        </div>
    )
}

export default AudioAndTranscription;