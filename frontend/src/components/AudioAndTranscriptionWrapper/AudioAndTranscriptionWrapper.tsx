import React from "react";
import { Link } from "react-router-dom";

import Nav from "@/components/Nav/Nav";
import useFetch from "@/hooks/useFetch";

import "./AudioAndTranscriptionWrapper.css";

interface RoomItemData {
  createdAt: string;
  name: string;
  recording: {
    createdAt: string;
    duration: number;
    filename: string;
    id: number;
    url: string;
  }
  transcription: {
    createdAt: string;
    filename: string;
    id: number;
    url: string;
  }
  users: {
    email: string;
    name: string;
    id: number;
    }[];
}

const AudioAndTranscriptionWrapper = () => {
  const { getUserRoomsData } = useFetch();
  const [roomsData, setRoomsData] = React.useState(null);

  React.useEffect(() => {
    getAllRoomsData();
  }, []);

  const getAllRoomsData = async (): Promise<void> => {
    const data: any = await getUserRoomsData();
    const records = data.records;

    setRoomsData(records);
  };

  const renderRoomsData = () => {
    if (!roomsData) return;

    return roomsData.map((item: RoomItemData) => {
      const { createdAt, name, recording, transcription, users } = item;
      const formatedDate = new Date(createdAt).toLocaleString();

      return (
        <div className="conversation__item" key={name}>

          <h3 className="item__title">Call ID/Name: {name}</h3>
          <span className="item__date">Created At: {formatedDate}</span>

          <Link to={`/audio-and-transcription/${name}`} state={{ formatedDate, name, recording, transcription, users }}>
            <button className="item__button">View</button>
          </Link>

        </div>
      );
    });
  };

  return (
    <div className="wrap">
      <Nav />
      <div className="conversation__wrap">
        <h2 className="conversation__title">
          Audio & Transcription Saved Data
        </h2>

        {renderRoomsData()}
      </div>
    </div>
  );
};

export default AudioAndTranscriptionWrapper;
