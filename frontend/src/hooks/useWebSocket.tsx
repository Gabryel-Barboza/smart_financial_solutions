import { useState, useEffect } from 'react';

const useWebSocket = (API_URL: string, sessionId: string) => {
  const url = API_URL.replace('http', 'ws') + `/websocket/${sessionId}`;
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    if (!API_URL || !sessionId) return;

    const ws = new WebSocket(url);
    setWebsocket(ws);

    return () => ws.close();
  }, [url, API_URL, sessionId]);

  return { websocket };
};

export default useWebSocket;
