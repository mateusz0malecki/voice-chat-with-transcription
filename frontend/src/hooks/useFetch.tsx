import { _fetch } from '../helpers/fetchProvider';
import { serverEndpoints } from '../helpers/configs';

interface SignInAndUpResponse {
    "access_token": string;
}

const useFetch = () => {
    const { login, register } = serverEndpoints;

    const userSignIn = (userData: URLSearchParams): Promise<SignInAndUpResponse> => {
        const additionalPath = login;
        const options = { 
            method: 'POST', 
            body: userData,
        }

        return _fetch({ additionalPath, options })
    };

    const userSignUp = (userData: URLSearchParams): Promise<SignInAndUpResponse> => {
        const additionalPath = register;
        const options = { 
            method: 'PUT', 
            body: userData,  
        }

        return _fetch({ additionalPath, options })
    };

    return { userSignIn, userSignUp }
}

export default useFetch;
