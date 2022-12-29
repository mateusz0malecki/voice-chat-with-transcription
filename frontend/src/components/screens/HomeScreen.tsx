import React from 'react';
import { Link } from 'react-router-dom';

import './homeScreen.css'

const HomeScreen = () => {
    const [room, setRoom] = React.useState('');
    const [username, setUsername] = React.useState('');

    return(
        <form method='post' action=''>

            <label htmlFor="username">Username</label>
            <input 
                value={username}
                title='username'
                onInput={ (e: React.FormEvent<HTMLInputElement>) => setUsername( (e.target as HTMLInputElement).value ) }
            />

            <label htmlFor='room'>Room</label>
            <input 
                value={room}
                title='room'
                onInput={ (e) => setRoom( (e.target as HTMLInputElement).value ) }
            />

            <Link to={`/call/${username}/${room}`}>
                <input type='submit' name='submit' value='Join Room' />
            </Link>

        </form>
    );
}

export default HomeScreen;
