import { serverEndpoints } from "./configs";

interface FetchProps {
    options: any;
    additionalPath: string;
}

export const _fetch = <T,>(props: FetchProps): Promise<T> => {
    const { options, additionalPath } = props;
    const { mainPath } = serverEndpoints;

    const path = mainPath;
    const url = path + additionalPath;

    return fetch(url, options)
        .then((resp) => {
            if (resp.ok) return resp.json();

            return Promise.reject(resp);
        })
        .catch((err) => console.log('error' , err) );
};
