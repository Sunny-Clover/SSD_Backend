// pages/ViewerPage.tsx
import React, { useState, useRef, useEffect } from 'react';
import './ViewerPage.css';

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected';

const ViewerPage: React.FC = () => {
  const [wsStatus, setWsStatus] = useState<ConnectionStatus>('disconnected');
  // 用 useRef 儲存 WebSocket 與 RTCPeerConnection 實例
  const wsRef = useRef<WebSocket | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);

  // 取得 token
  const jwtToken = localStorage.getItem('jwtToken');
  if (!jwtToken) {
    window.location.href = '/login';
  }

  // 建立連線的函數
  const openConnection = () => {
    if (wsRef.current || pcRef.current) {
      console.log('WebSocket/PeerConnection already exists.');
      return;
    }

    setWsStatus('connecting');

    // 建立 WebSocket 連線（請根據實際設定調整 URL）
    const role = 'viewer';
    const wsBaseUrl = import.meta.env.VITE_WS_URL;
    const wsUrl = `${wsBaseUrl}/ws/${role}?token=${jwtToken}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    // 建立 RTCPeerConnection，並設定 STUN 伺服器
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
    });
    pcRef.current = pc;

    // 當接收到遠端的媒體軌道時，顯示到 video 元件上
    pc.ontrack = (event) => {
      const video = document.getElementById('video') as HTMLVideoElement;
      if (video) {
        video.srcObject = event.streams[0];
      }
    };

    ws.onopen = () => {
      console.log('WebSocket connected.');
      setWsStatus('connected');
    };

    ws.onclose = (event) => {
      console.log('WebSocket disconnected.', event);
      if (event.code === 403) {
        alert('WebSocket connection forbidden: You do not have permission to connect.');
      } else {
        alert(`WebSocket closed with code: ${event.code} (${event.reason})`);
      }
      setWsStatus('disconnected');
      wsRef.current = null;
      if (pcRef.current) {
        pcRef.current.close();
        pcRef.current = null;
      }
    };
    

    // 處理從 WebSocket 收到的訊息（SDP 與 ICE）
    ws.onmessage = async (message) => {
      const data = JSON.parse(message.data);
      if (data.sdp) {
        await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
        if (data.sdp.type === 'offer') {
          const answer = await pc.createAnswer();
          await pc.setLocalDescription(answer);
          ws.send(JSON.stringify({ sdp: pc.localDescription }));
        }
      } else if (data.ice) {
        await pc.addIceCandidate(new RTCIceCandidate(data.ice));
      }
    };

    // 當本地 ICE candidate 產生時，送出給 signaling server
    pc.onicecandidate = (event) => {
      if (event.candidate && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ ice: event.candidate }));
      }
    };
  };

  // 關閉連線的函數
  const closeConnection = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }
    setWsStatus('disconnected');
  };

  // 清理動作：當組件卸載時關閉連線
  useEffect(() => {
    return () => {
      closeConnection();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="viewer-container">
      <div className="control-panel">
        <h2>WebSocket Status: {wsStatus}</h2>
        <button onClick={openConnection} disabled={wsStatus === 'connected' || wsStatus === 'connecting'}>
          Open WebSocket
        </button>
        <button onClick={closeConnection} disabled={wsStatus !== 'connected'}>
          Close WebSocket
        </button>
      </div>
      <video id="video" autoPlay playsInline controls></video>
    </div>
  );
};

export default ViewerPage;
