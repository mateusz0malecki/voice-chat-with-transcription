import { _fetch } from '../helpers/fetchProvider';
import { serverEndpoints } from '../helpers/configs';
import useLocalStorage from './useLocalStorage';

interface SignInAndUpResponse {
    "access_token": string;
}

export interface RecordData {
    "info": "string"
}

const useFetch = () => {
    const { getLocalStorage } = useLocalStorage();
    const { access_token } = getLocalStorage() || {};
    const { login, register, recording, transcriptions} = serverEndpoints;

    const userSignIn = (userData: URLSearchParams): Promise<SignInAndUpResponse> => {
        const additionalPath = login;
        const options = { 
            method: 'POST', 
            body: userData,
        }

        return _fetch({ additionalPath, options })
    };

    const userSignUp = (userData:any): Promise<SignInAndUpResponse> => {
        const additionalPath = register;
        const options = { 
            method: 'POST', 
            body: userData,
        }

        return _fetch({ additionalPath, options })
    };

    const sendRecord = (recordData: FormData): Promise<RecordData> => {
        const additionalPath = recording;
        const options = { 
            method: 'POST', 
            body: recordData, 
            headers: { Authorization: `Bearer ${access_token}` } 
        };

        return _fetch({additionalPath, options});
    };

    const getTranscription = () => {
        // const additionalPath = `transcriptions/file/${filename}`
        const additionalPath = transcriptions;
        const options = { 
            method: 'GET', 
            headers: { Authorization: `Bearer ${access_token}` } 
        };

        return _fetch({additionalPath, options});
    }

    return { userSignIn, userSignUp, sendRecord , getTranscription}
}

export default useFetch;
