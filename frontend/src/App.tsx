import { BrowserRouter as Router } from "react-router-dom";
import RouteList from "./components/screens/RouteList";

import Transribe from "./components/Transcribe/Transcribe";

import './app.css'

const App = (): JSX.Element => {
  
  // return (
  //   <Router>
  //     <RouteList />
  //   </Router>
  // )

  return (
    <>
      <Transribe />
    </>
  )
}

export default App
