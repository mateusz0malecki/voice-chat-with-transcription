export const serverEndpoints = {
    mainPath: 'https://digimonkeys-speech2txt.com/api/v1/',
    login: 'login',
    register: 'register',
    recording: 'recordings',
    transcriptions: 'transcriptions?page=1&page_size=10',
    rooms: 'rooms?page=1&page_size=10'
};

export const path = {
    signInPage: '/',
    signUpPage: '/sing-up',
    homeScreenPage: '/home-screen',
    callScreenPage: '/call-screan',
    audioAndTranscriptionPage: '/audio-and-transcription',
    connectionScreen: '/call/:username/:room',
    audioAndTranscriptionItem: '/audio-and-transcription/:name'
  };