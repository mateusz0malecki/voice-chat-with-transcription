import React from "react";
import { v4 as uuidv4 } from "uuid";
import { Link } from "react-router-dom";

import Nav from "../../Nav/Nav";

import "./homeScreen.css";

const HomeScreen = (): JSX.Element => {
  const [room, setRoom] = React.useState("");
  const [username, setUsername] = React.useState("");

  React.useEffect(() => {
    creteRoom();
  }, []);

  const creteRoom = (): void => {
    const roomID = uuidv4();
    setRoom(roomID);
  };

  return (
    <div className="form__wrap">
      <Nav />
      <form method="post" action="" className="form">
        <label htmlFor="username" className="form__label">
          Username
        </label>
        <input
          className="form__input"
          value={username}
          title="username"
          onInput={(e: React.FormEvent<HTMLInputElement>) =>
            setUsername((e.target as HTMLInputElement).value)
          }
        />

        <Link to={`/call/${username}/${room}`}>
          <button className="form__button">Crete Room!</button>
        </Link>
      </form>
    </div>
  );
};

export default HomeScreen;
