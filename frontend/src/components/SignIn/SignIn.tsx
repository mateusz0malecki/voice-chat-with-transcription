import React from 'react';
import { useNavigate } from "react-router-dom";

import useLocalStorage from '../../hooks/useLocalStorage';
import useFetch from '../../hooks/useFetch';
import { path } from '../../helpers/configs'
import './signIn.css'

const SignIn = (): JSX.Element => {
    const navigate = useNavigate();
    const { userSignIn } = useFetch();
    const { setLocalStorage } = useLocalStorage();
    const { homeScreenPage, signUpPage } = path;


    const handleSubmit = async (): Promise<void> => {
        const email = ( document.querySelector('#signIn-email') as HTMLInputElement ).value;
        const password = ( document.querySelector('#signIn-password') as HTMLInputElement ).value;

        const userData = new URLSearchParams({
            'username': email,
            'password': password,
        });

        const signedInUserData = await userSignIn(userData)

        if(signedInUserData) {
            setLocalStorage(signedInUserData);
            navigate(homeScreenPage)
        }
    }

    return (
        <div className="signIn__wrap">
            <div className="signIn">
                    <h4 className="signIn__title">Sign In</h4>
                    <div className="signIn__input--wrap">
                        <input 
                            className="signIn__input" 
                            type="email" 
                            name="signIn-email" 
                            id="signIn-email" 
                            placeholder="Your Email" 
                            autoComplete="off" 
                        />
                            <i className="input__icon input__icon--first"></i>
                    </div>
                    <div className="signIn__input--wrap">
                        <input 
                            className="signIn__input" 
                            type="password" 
                            name="signIn-password" 
                            id="signIn-password" 
                            placeholder="Your Password" 
                            autoComplete="off" 
                        />
                            <i className="input__icon input__icon--second"></i>
                    </div>
                    <button className="signIn__button" onClick={handleSubmit}>Submit</button>
                    <a onClick={() => navigate(signUpPage)} className="signIn__link">Dont have an account?</a>
            </div>
        </div>
    )
}

export default SignIn;
