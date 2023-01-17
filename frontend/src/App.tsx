import { BrowserRouter as Router } from "react-router-dom";
import RouteList from "./components/screens/RouteList";

import './app.css'

const App = (): JSX.Element => {
  
  return (
    <Router>
      <RouteList />
    </Router>
  )
}

export default App
