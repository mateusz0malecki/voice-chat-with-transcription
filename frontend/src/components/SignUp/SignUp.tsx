import React from 'react';
import { useNavigate } from "react-router-dom";

import useFetch from '../../hooks/useFetch';
import { path } from '../../helpers/configs'
import './signUp.css'

const SignUp = (): JSX.Element => {
    const navigate = useNavigate();
    const { userSignUp } = useFetch();
    const { signInPage } = path;

    const handleSubmit = async (): Promise<void> => {
        const email = (document.querySelector('#signUp-email') as HTMLInputElement).value;
        const name = (document.querySelector('#signUp-name') as HTMLInputElement).value;
        const password = (document.querySelector('#signUp-password') as HTMLInputElement).value;

        const userData = new URLSearchParams({
            'email': email,
            'name': name,
            'password': password,
        });

        const signedUpUserData = await userSignUp(userData);


        signedUpUserData && navigate(signInPage);
    }

    return (
        <>
            <div className="signUp__wrap">
                <div className="signUp">
                    <h4 className="signUp__title">Sign Up</h4>
                    <div className="signUp__input--wrap">
                        <input
                            className="signUp__input"
                            type="text"
                            name="signUp-name"
                            id="signUp-name"
                            placeholder="Your Name"
                            autoComplete="off"
                        />
                        <i className="input__icon input__icone--first"></i>
                    </div>
                    <div className="signUp__input--wrap">
                        <input
                            className="signUp__input"
                            type="email"
                            name="signUp-email"
                            id="signUp-email"
                            placeholder="Your Email"
                            autoComplete="off"
                        />
                        <i className="input__icon input__icone--second"></i>
                    </div>
                    <div className="signUp__input--wrap">
                        <input
                            className="signUp__input"
                            type="password"
                            name="signUp-password"
                            id="signUp-password"
                            placeholder="Your Password"
                            autoComplete="off"
                        />
                        <i className="input__icon input__icone--third"></i>
                    </div>
                    <button className="signUp__button" onClick={handleSubmit}>submit</button>
                    <a onClick={() => navigate(signInPage)} className="signIn__link">Don you have an account?</a>
                </div>
            </div>
        </>
    )
}

export default SignUp;