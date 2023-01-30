import React from 'react';
import { useNavigate } from 'react-router-dom';

import { path } from '../../helpers/configs'
import './nav.css';

const Nav = (): JSX.Element => {
    const navigate = useNavigate();
    const {signInPage, homeScreenPage, callScreenPage, audioAndTranscriptionPage} = path;

    const handleSignOut = (): void => {
        window.localStorage.clear();
        navigate(signInPage)
    }

    return (
        <nav className='nav'>
            <ul className='nav__list'>
                <li className='list__item' onClick={() => navigate(homeScreenPage)}>
                    CreateRoom
                </li>
                <li className='list__item' onClick={() => navigate(callScreenPage)}>
                    JoinRoom
                </li>
                <li className='list__item' onClick={() => navigate(audioAndTranscriptionPage)}>
                    Audio & Transcription
                </li>
                <li className='list__item list__item--leave' onClick={handleSignOut}>
                    LogOut
                </li>
            </ul>
        </nav>
    )
}

export default Nav;
