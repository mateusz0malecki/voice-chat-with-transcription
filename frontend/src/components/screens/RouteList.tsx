import { Routes, Route } from "react-router-dom";
import CallScreen from './CallScreen/CallScreen'
import HomeScreen from "./HomeScreen/HomeScreen";

const RouteList = (): JSX.Element => {
  return (
    <Routes>
      <Route path="/" element={<HomeScreen />} />
      <Route path="/call/:username/:room" element={<CallScreen />} />
    </Routes>
  );
}

export default RouteList;
