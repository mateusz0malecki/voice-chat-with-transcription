import React from 'react';
import { Link } from 'react-router-dom';

import useLocalStorage from '../../../hooks/useLocalStorage';
import useFetch from '../../../hooks/useFetch'

import './homeScreen.css'

const HomeScreen = (): JSX.Element => {
    const [room, setRoom] = React.useState('');
    const [username, setUsername] = React.useState('');
    const { setLocalStorage } = useLocalStorage();
    const { userSignIn } = useFetch();;

    React.useEffect(() => {
        singIn()
    },[])

    const singIn = async (): Promise<void> => {

        const email: string = 'admin@admin.com';
        const password: string = 'admin';
        
        const userData: URLSearchParams = new URLSearchParams({
            'username': email,
            'password': password,
        });
    
        const signInResponse = await userSignIn(userData);

        signInResponse && setLocalStorage(signInResponse);
    };

    return(
        <div className='form__wrap'>
            <form method='post' action='' className='form'>
                <label htmlFor="username" className='form__label'>Username</label>
                <input
                    className='form__input' 
                    value={username}
                    title='username'
                    onInput={ (e: React.FormEvent<HTMLInputElement>) => setUsername( (e.target as HTMLInputElement).value ) }
                />

                <label htmlFor='room' className='form__label'>Room</label>
                <input
                    className='form__input' 
                    value={room}
                    title='room'
                    onInput={ (e: React.FormEvent<HTMLInputElement>) => setRoom( (e.target as HTMLInputElement).value ) }
                />

                <Link to={`/call/${username}/${room}`}>
                    <button className='form__button' >
                        Join Room
                    </button>
                </Link>
            </form>
        </div>
    );
}

export default HomeScreen;
