import React from 'react';
import { useParams } from 'react-router-dom';
import socketio from 'socket.io-client';

import './callScreen.css'

const CallScreen = (): JSX.Element => {
    const params = useParams();
    const { username, room } = params;
    const localVideoRef = React.useRef(null);
    const remoteVideoRef = React.useRef(null);

    const socket = socketio('http://localhost:9000', {
        autoConnect: false,
    });

    let RTC_PEER_CONNECTION: RTCPeerConnection | null;

    const sendData = (data) => {
        socket.emit('data', {
            username,
            room,
            data,
        });
    };

    const startConnection = () => {
        navigator.mediaDevices.getUserMedia({ audio: false, video: { height: 350, width: 350 } })
            .then( (stream) => {
                console.log('local stream found');
                localVideoRef.current.srcObject = stream;
                socket.connect();
                socket.emit('join', {username, room} )
            })
            .catch( (error) => {
                console.error('Stream not found:' , error)
            });
    };

    const stopConnection = () => {
        socket.emit('leave', {username, room})
    }

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
    
      const createPeerConnection = () => {
        try {
          RTC_PEER_CONNECTION = new RTCPeerConnection({});
          RTC_PEER_CONNECTION.onicecandidate = onIceCandidate;
          RTC_PEER_CONNECTION.ontrack = onTrack;

          const localStream = localVideoRef.current.srcObject;

          for (const track of localStream.getTracks()) {
            RTC_PEER_CONNECTION.addTrack(track, localStream);
          }
          console.log("PeerConnection created");
        } catch (error) {
          console.error("PeerConnection failed: ", error);
        }
      };

      const setAndSendLocalDescription = (sessionDescription: RTCLocalSessionDescriptionInit) => {
        RTC_PEER_CONNECTION.setLocalDescription(sessionDescription);
        console.log("Local description set");
        sendData(sessionDescription);
      };
    
      const sendOffer = () => {
        console.log("Sending offer");
        RTC_PEER_CONNECTION.createOffer().then(setAndSendLocalDescription, (error) => {
          console.error("Send offer failed: ", error);
        });
      };
    
      const sendAnswer = () => {
        console.log("Sending answer");
        RTC_PEER_CONNECTION.createAnswer().then(setAndSendLocalDescription, (error) => {
          console.error("Send answer failed: ", error);
        });
      };

      const signalingDataHandler = (data) => {
        if (data.type === "offer") {
          createPeerConnection();
          RTC_PEER_CONNECTION.setRemoteDescription(new RTCSessionDescription(data));
          sendAnswer();
        } else if (data.type === "answer") {
          RTC_PEER_CONNECTION.setRemoteDescription(new RTCSessionDescription(data));
        } else if (data.type === "candidate") {
          RTC_PEER_CONNECTION.addIceCandidate(new RTCIceCandidate(data.candidate));
        } else {
          console.log("Unknown Data");
        }
      };

      socket.on("ready", () => {
        console.log("Ready to Connect!");
        createPeerConnection();
        sendOffer();
      });
    
      socket.on("data", (data) => {
        console.log("Data received: ", data);
        signalingDataHandler(data);
      });
    
      React.useEffect(() => {

        startConnection();

        return function cleanup() {
            RTC_PEER_CONNECTION?.close();
            stopConnection();
        };
      }, []);


    return (
        <div>
            <label>{'Username:' + username}</label>
            <label>{'Room ID:' + room}</label>
            <video autoPlay muted playsInline ref={localVideoRef} />
            <video autoPlay muted playsInline ref={remoteVideoRef} />
        </div>
    )
}

export default CallScreen;