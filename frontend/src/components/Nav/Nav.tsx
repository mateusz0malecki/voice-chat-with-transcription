import React from 'react';
import { useNavigate } from 'react-router-dom';

import { path } from '../../helpers/configs'
import './nav.css';

const Nav = (): JSX.Element => {
    const [menuOpen, setMenuOpen] = React.useState(false);
    const navigate = useNavigate();
    const {signInPage, homeScreenPage, callScreenPage, audioAndTranscriptionPage} = path;

    const handleSignOut = (): void => {
        window.localStorage.clear();
        navigate(signInPage)
    }

    const handleMenuToggle = (): void => {
        setMenuOpen(!menuOpen);
    }

    const handleNavigate = (path: string) => {
        setMenuOpen(false);
        navigate(path)
    }

    return (
        <nav className='nav'>
            <div className='nav__hamburger-icon' onClick={handleMenuToggle}>
                <span className={`hamburger-icon__line ${menuOpen ? 'hamburger-icon__line--open' : ''}`}></span>
                <span className={`hamburger-icon__line ${menuOpen ? 'hamburger-icon__line--open' : ''}`}></span>
                <span className={`hamburger-icon__line ${menuOpen ? 'hamburger-icon__line--open' : ''}`}></span>
            </div>
            <ul className={`nav__list ${menuOpen ? 'nav__list--open' : ''}`}>
                <li className='list__item list__item--open' onClick={() => handleNavigate(homeScreenPage)}>
                    CreateRoom
                </li>
                <li className='list__item list__item--open' onClick={() => handleNavigate(callScreenPage)}>
                    JoinRoom
                </li>
                <li className='list__item list__item--open' onClick={() => handleNavigate(audioAndTranscriptionPage)}>
                    Audio & Transcription
                </li>
                <li className='list__item list__item--open list__item--leave' onClick={handleSignOut}>
                    LogOut
                </li>
            </ul>
        </nav>
    )

    // return (
    //     <nav className='nav'>
    //         <ul className='nav__list'>
    //             <li className='list__item' onClick={() => navigate(homeScreenPage)}>
    //                 CreateRoom
    //             </li>
    //             <li className='list__item' onClick={() => navigate(callScreenPage)}>
    //                 JoinRoom
    //             </li>
    //             <li className='list__item' onClick={() => navigate(audioAndTranscriptionPage)}>
    //                 Audio & Transcription
    //             </li>
    //             <li className='list__item list__item--leave' onClick={handleSignOut}>
    //                 LogOut
    //             </li>
    //         </ul>
    //     </nav>
    // )
}

export default Nav;
