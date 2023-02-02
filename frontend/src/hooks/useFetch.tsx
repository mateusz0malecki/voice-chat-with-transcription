import { _fetch } from '../helpers/fetchProvider';
import { serverEndpoints } from '../helpers/configs';
import useLocalStorage from './useLocalStorage';

interface SignInAndUpResponse {
    "access_token": string;
}

export interface RecordData {
    "info": "string"
}

interface TranscrieReponse {
  text: string;
  roomName: string;
};

const useFetch = () => {
    const { getLocalStorage } = useLocalStorage();
    const { access_token } = getLocalStorage() || {};
    const { login, register, recording, rooms, transcriptions } = serverEndpoints;

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

    const getUserRoomsData = () => {
        const additionalPath = rooms;
        const options = { 
            method: 'GET', 
            headers: { Authorization: `Bearer ${access_token}` } 
        };

        return _fetch({additionalPath, options});
    }

    const getRecording = (filename: string): Promise<Blob | void> => {
        const { mainPath } = serverEndpoints;
        const additionalPath = `recordings/file/${filename}`;
        const options = { 
            method: 'GET', 
            headers: { Authorization: `Bearer ${access_token}` } 
        };
        const url = mainPath + additionalPath;

        return fetch(url, options)
            .then((resp) => {
                if (resp.ok) return resp.blob();
            
                return Promise.reject(resp);
            })
            .catch((err) => console.log('error' , err) );
    }

    const getTranscribe = (filename: string): Promise<TranscrieReponse> => {
        const additionalPath = `transcriptions/file/${filename}`;
        const options = { 
            method: 'GET', 
            headers: { Authorization: `Bearer ${access_token}` } 
        };

        return _fetch({additionalPath, options});
    }

    return { userSignIn, userSignUp, sendRecord , getUserRoomsData, getRecording, getTranscribe }
}

export default useFetch;
