import React from "react";
import { useParams } from "react-router-dom";
import socketio from "socket.io-client";
import Transribe from "../Transcribe/Transcribe";

import "./callScreen.css";

const CallScreen = (): JSX.Element => {
  const params = useParams();
  const { username, room } = params;
  const localVideoRef = React.useRef(null);
  const remoteVideoRef = React.useRef(null);

  const socket = socketio("http://localhost:9000", {
    autoConnect: false,
  });

  const peerConnections = new Map();

  const sendData = (data) => {
    socket.emit("data", username, room, data);
  };

  const startConnection = () => {
    navigator.mediaDevices
      .getUserMedia({ audio: false, video: { height: 350, width: 350 } })
      .then(async (stream) => {
        console.log("local stream found");
        localVideoRef.current.srcObject = stream;
        await socket.connect();
        socket.emit("join", username, room);
      })
      .catch((error) => {
        console.error("Stream not found:", error);
      });
  };

  const stopConnection = () => {
    socket.emit("leave", username, room);
  };

  const onIceCandidate = (event) => {
    if (event.candidate) {
      console.log("Sending ICE candidate");
      sendData({
        type: "candidate",
        candidate: event.candidate,
      });
    }
  };

  const onTrack = (event) => {
    console.log("Adding remote track");
    remoteVideoRef.current.srcObject = event.streams[0];
  };

  const createPeerConnection = (peerID) => {
    try {
      const peerConnection = new RTCPeerConnection({});
      peerConnection.onicecandidate = onIceCandidate;
      peerConnection.ontrack = onTrack;

      const localStream = localVideoRef.current.srcObject;

      for (const track of localStream.getTracks()) {
        peerConnection.addTrack(track, localStream);
      }

      peerConnections.set(peerID, peerConnection);

      console.log("PeerConnection created");
    } catch (error) {
      console.error("PeerConnection failed: ", error);
    }
  };

  const setAndSendLocalDescription = async (
    sessionDescription: RTCLocalSessionDescriptionInit,
    peerID
  ) => {

    const peerConnection = peerConnections.get(peerID);

    if (!peerConnection) return;

    try {
      await peerConnection.setLocalDescription(sessionDescription);
      console.log("ses", sessionDescription);
      sendData(sessionDescription);
    } catch (error) {
      console.error("Error setting local description: ", error);
    }
  };

  const sendOffer = (peerID) => {
    const peerConnection = peerConnections.get(peerID);

    if (!peerConnection) return;

    peerConnection.createOffer().then(
      (sessionDescription) => {
        setAndSendLocalDescription(sessionDescription, peerID);
        console.log("abc");
      },
      (error) => {
        console.error("Send offer failed: ", error);
      }
    );
  };

  const sendAnswer = (peerID) => {
    const peerConnection = peerConnections.get(peerID);
    if (!peerConnection) return;
    console.log("Sending answer");

    peerConnection.createAnswer().then(
      (sessionDescription) => {
        setAndSendLocalDescription(sessionDescription, peerID);
      },
      (error) => {
        console.error("Send offer failed: ", error);
      }
    );
  };

  const signalingDataHandler = (data, peerID) => {
    if (data.type === "offer") {
      createPeerConnection(peerID);
      const peerConnection = peerConnections.get(peerID);

      if (!peerConnection) return;

      peerConnection
        .setRemoteDescription(new RTCSessionDescription(data))
        .then(() => {
          sendAnswer(socket.id);
        });
    } else if (data.type === "answer") {
      const peerConnection = peerConnections.get(peerID);
      if (!peerConnection) return;
      peerConnection.setRemoteDescription(new RTCSessionDescription(data));
    } else if (data.type === "candidate") {
      const peerConnection = peerConnections.get(peerID);
      if (!peerConnection) return;
      peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
    } else {
      console.log("Unknown Data");
    }
  };

  socket.on("ready", () => {
    console.log("Ready to Connect!");
    createPeerConnection(socket.id);
    sendOffer(socket.id);
  });

  socket.on("data", (data) => {
    // console.log("Data received: ", data);
    signalingDataHandler(data, socket.id);
  });

  React.useEffect(() => {
    startConnection();

    return function cleanup() {
      stopConnection();

      peerConnections.forEach((peerConnection) => {
        peerConnection.close();
      });
    };
  }, []);

  return (
    <div>
      <label>{"Username:" + username}</label>
      <label>{"Room ID:" + room}</label>
      <video autoPlay muted playsInline ref={localVideoRef} />
      <video autoPlay muted playsInline ref={remoteVideoRef} />
    </div>
  );
};

export default CallScreen;
