import { Routes, Route } from "react-router-dom";

import SignIn from "@/components/SignIn/SignIn";
import SignUp from "@/components/SignUp/SignUp"
import CallScreen from '@/components/Screens/CallScreen/CallScreen';
import HomeScreen from "@/components/Screens/HomeScreen/HomeScreen";
import ConnectionScreen from '@/components/Screens/ConnectionScreen/ConnectionScreen'
import AudioAndTranscription from '@/components/AudioAndTranscription/AudioAndTranscription'

import { path } from '../../helpers/configs'

const Router = (): JSX.Element => {
  const { signInPage, signUpPage, homeScreenPage, callScreenPage, connectionScreen, audioAndTranscriptionPage } = path;

  return (
    <Routes>
      <Route path={ signInPage } element={<SignIn />} />
      <Route path={signUpPage} element={<SignUp />} />
      <Route path={homeScreenPage} element={<HomeScreen />} />
      <Route path={callScreenPage} element={<CallScreen />} />
      <Route path={connectionScreen} element={<ConnectionScreen />} />
      <Route path={audioAndTranscriptionPage} element={<AudioAndTranscription />} />
    </Routes>
  );
}

export default Router;
