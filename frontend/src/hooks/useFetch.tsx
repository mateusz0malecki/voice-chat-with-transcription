import { _fetch } from '../helpers/fetchProvider';
import { serverEndpoints } from '../helpers/configs';

interface SignInResponse {
    "access_token": string;
}

const useFetch = () => {
    const { login } = serverEndpoints;

    const userSignIn = (userData: URLSearchParams): Promise<SignInResponse> => {
        const additionalPath = login;
        const options = { 
            method: 'POST', 
            body: userData,
        }

        return _fetch({ additionalPath, options })
    };

    return { userSignIn }
}

export default useFetch;
