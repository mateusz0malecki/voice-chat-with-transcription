import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import socketio from "socket.io-client";

import Transcribe from '../../Transcribe/Transcribe'
import { path } from '../../../helpers/configs'
import "./callScreen.css";

const socket = socketio("https://test-digi-speech2txt.com/sockets/", {
  autoConnect: false,
  path: '/sockets/',
});

const CallScreen = (): JSX.Element => {
  const params = useParams();
  const navigate = useNavigate();
  const localVideoRef = React.useRef<HTMLVideoElement>(null);
  const remoteVideoRef = React.useRef<HTMLVideoElement>(null);
  const [isTranscript, setIsTranscript] = React.useState(false);
  const [ leaveAction, setLeaveAction ] = React.useState(false)
  const { homeScreenPage } = path;
  const { username, room } = params;
  const peerConnections = new Map();

  React.useEffect(() => {
    startConnection();

    return function cleanup() {
      stopConnection();
      peerConnections.forEach((peerConnection) => {
        peerConnection.close();
      });
    };
  }, []);

  React.useEffect(() => {
    if(!leaveAction) return;
      leaveAction && stopConnection();
  },[leaveAction])
  
  socket.on("ready", () => {
    createPeerConnection(socket.id);
    sendOffer(socket.id);
  });

  socket.on("data", (data) => {
    signalingDataHandler(data, socket.id);
    setIsTranscript(true);
  });

  socket.on("leave", (data) => {
    const remoteVideo = document.querySelector('.video--remote');
    remoteVideo && remoteVideo.remove();
  });

  const startConnection = (): void => {
    navigator.mediaDevices
      .getUserMedia({ audio: false, video: { height: 350, width: 350 } })
      .then( (stream) => {
        localVideoRef.current.srcObject = stream;

        socket.connect();
        socket.emit("join", username, room);
      })
      .catch((error) => {
        console.error("Stream not found:", error);
      });
  };

  const stopConnection = (): void => {
    socket.emit("leave", username, room);
    setIsTranscript(false);
    navigate(homeScreenPage);
  };

  const sendData = (data: { type: string, candidate: RTCIceCandidate } | RTCLocalSessionDescriptionInit ) => {
    socket.emit("data", username, room, data);
  };

  const onIceCandidate = (event: RTCPeerConnectionIceEvent): void => {
    if (!event.candidate) return;
    
    sendData({ type: "candidate", candidate: event.candidate });
  };

  const onTrack = (event: RTCTrackEvent): void => {
    remoteVideoRef.current.srcObject = event.streams[0];
  };

  const createPeerConnection = (peerID: string): void => {
      const peerConnection = new RTCPeerConnection({});

      if(!peerConnection) return;

      peerConnection.onicecandidate = onIceCandidate;
      peerConnection.ontrack = onTrack;
      const localStream = localVideoRef.current?.srcObject as MediaStream;

      for (const track of localStream?.getTracks()) {
        peerConnection.addTrack(track, localStream);
      }

      peerConnections.set(peerID, peerConnection);
    }
  ;

  const setAndSendLocalDescription = async ( sessionDescription: RTCLocalSessionDescriptionInit, peerID: string ) => {
    const peerConnection = peerConnections.get(peerID);

    if (!peerConnection) return;

    await peerConnection.setLocalDescription(sessionDescription);
    sendData(sessionDescription);
  };

  const sendOffer = (peerID: string) => {
    const peerConnection = peerConnections.get(peerID);

    if (!peerConnection) return;

    peerConnection.createOffer()
      .then((sessionDescription: RTCLocalSessionDescriptionInit) => {
        setAndSendLocalDescription(sessionDescription, peerID);
      })
      .catch((error: Error) => {
        console.error("Send offer failed: ", error);
      });
  };

  const sendAnswer = (peerID: string) => {
    const peerConnection = peerConnections.get(peerID);

    if (!peerConnection) return

    peerConnection.createAnswer()
      .then((sessionDescription: RTCLocalSessionDescriptionInit) => {
        setAndSendLocalDescription(sessionDescription, peerID);
      })
      .catch((error: Error) => {
        console.error("Send offer failed: ", error);
      });
  };

  const signalingDataHandler = (data: any, peerID:string) => {
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

  return (
    <div className="wrap">
      <section className="section__video">
        <span className="video__room">{"Room name: " + room}</span>
        <div className="video__holder">
          <div>
            <video className="video video--local" autoPlay muted playsInline ref={localVideoRef} />
            {/* <span>{"Username:" + username}</span> */}
          </div>
          <div>
            <video className="video video--remote" autoPlay muted playsInline ref={remoteVideoRef} />
            {/* <span>{"Username:" + username}</span> */}
          </div>
        </div>
      </section>
      <button className="video__button" onClick={() => setLeaveAction(true)}>Leave</button>

      <Transcribe isTranscript={isTranscript} leaveAction={leaveAction} />
    </div>
  );
};

export default CallScreen;