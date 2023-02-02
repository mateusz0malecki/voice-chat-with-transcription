import React from "react";
import { useLocation } from "react-router-dom";

import useFetch from "@/hooks/useFetch";
import Nav from '@/components/Nav/Nav'
import "./audioAndTranscriptionItem.css";

const AudioAndTranscriptionItem = () => {
  const [textData, setTextData] = React.useState<any>();
  const [blob, setBlob] = React.useState<any>();
  const { getRecording, getTranscribe } = useFetch();
  const { state } = useLocation();
  const { formatedDate, name, recording, transcription, users } = state;

  React.useEffect(() => {
    if (!recording) return;

    const { filename } = recording;

    getRecording(filename).then((res) => {
      const url = URL.createObjectURL(res as Blob);
      setBlob(url);
    });
  }, []);

  React.useEffect(() => {
    if (!transcription) return;
    
    const { filename } = transcription;

    getTranscribe(filename).then((resp) => {
      const { text } = resp;
      const extractedTextData = extractTextData(text);

      setTextData(extractedTextData);
    });
  }, []);

  React.useEffect(() => {
    if (!textData || !blob) return;
    highlightText();
  }, [textData, blob]);

  const renderParticipants = () => {
    return users.map( (user: {
      email: string,
      name: string,
      id: number
  } ) => {
      const { name } = user;
      return name;
    });
  };

  const extractTextData = (text: string): string[][] => {
    const result: string[][] = [];
    const lines = text.split("\n");

    for (const line of lines) {
      const parts = line.split(" - ");

      if (parts.length === 4) {
        result.push([parts[2], parts[3]]);
      }
    }
    return result;
  };

  const sortedTranscription = (data: Array<Array<string>>): (string | number)[][] => {
    const finalData: (Array<string | number>)[] = [];

    data.map(( dataItem ) => {
      const seconds = dataItem[0].split(" - ");
      const words = dataItem[1].split("  ");

      const secondsArray = seconds[0].slice(1, -1).split(",").map((sec) => parseFloat(sec));
      const wordsArray = words[0].split(" ");

      secondsArray.forEach((second, index) => {
        const newArray = [second, wordsArray[index]];

        finalData.push(newArray);
      });
    });
    return finalData;
  };

  const removeChildrenFromElement = (element: Element): void => {
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
  }

  const highlightText = (): void => {
    const textHolder = document.querySelector(".text__holder");
    removeChildrenFromElement(textHolder);

    const audioElement = document.querySelector("audio");
    const transcriptionDATA = sortedTranscription(textData);
    const transcriptionElements: { element: HTMLSpanElement; timing: number }[] = [];

    for (const [time, word] of transcriptionDATA) {
      const element = document.createElement("span");
      element.textContent = word as string;
      const timing = time as number;
      transcriptionElements.push({ element, timing });
      textHolder.appendChild(element);
    }

    audioElement.addEventListener("timeupdate", function () {
      for (let i = 0; i < transcriptionElements.length; i++) {

        const { element, timing } = transcriptionElements[i];
        const nextTime = i + 1 < transcriptionElements.length ? transcriptionElements[i + 1].timing : Infinity;
        
        if (audioElement.currentTime > timing && audioElement.currentTime <= nextTime) {
          element.style.backgroundColor = "rgb(225, 234, 129)";
        } else {
          element.style.backgroundColor = "";
        }
      }
    });
  }

  if (!blob) return;

  return (
    <div className="wrap wrap__preview">
      <Nav />
      <h3 className="preview__title">
        Recording of the conversation of: {formatedDate}
      </h3>
      <span className="preview__name">
        Name: {name}
      </span>
      <span className="preview__participants">
        Participants in this conversation were: {renderParticipants()}
      </span>

      <audio controls className="preview__audio">
        <source src={blob} />
      </audio>

      <div className="text__holder"></div>
    </div>
  );
};

export default AudioAndTranscriptionItem;
