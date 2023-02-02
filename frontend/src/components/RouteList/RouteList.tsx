import { Routes, Route } from "react-router-dom";

import SignIn from "@/components/SignIn/SignIn";
import SignUp from "@/components/SignUp/SignUp"
import CallScreen from '@/components/screens/CallScreen/CallScreen';
import HomeScreen from "@/components/screens/HomeScreen/HomeScreen";
import ConnectionScreen from '@/components/screens/ConnectionScreen/ConnectionScreen';
import AudioAndTranscription from '@/components/AudioAndTranscriptionWrapper/AudioAndTranscriptionWrapper';
import AudioAndTranscriptionItem from '@/components/AudioAndTranscriptionItem/AudioAndTranscriptionItem';

import { path } from '../../helpers/configs'

const Router = (): JSX.Element => {
  const { signInPage, signUpPage, homeScreenPage, callScreenPage, connectionScreen, audioAndTranscriptionPage, audioAndTranscriptionItem } = path;

  return (
    <Routes>
      <Route path={ signInPage } element={<SignIn />} />
      <Route path={signUpPage} element={<SignUp />} />
      <Route path={homeScreenPage} element={<HomeScreen />} />
      <Route path={callScreenPage} element={<CallScreen />} />
      <Route path={connectionScreen} element={<ConnectionScreen />} />
      <Route path={audioAndTranscriptionPage} element={<AudioAndTranscription />} />
      <Route path={audioAndTranscriptionItem} element={<AudioAndTranscriptionItem />} />
    </Routes>
  );
}

export default Router;
