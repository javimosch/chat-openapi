import { useState, useEffect, useCallback } from 'react';
import { WebSocketMessage } from '../types';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

export function useWebSocket() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messageBuffer, setMessageBuffer] = useState<string>(''); // Buffer for accumulating message content
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const connect = useCallback(() => {
    try {
      const socket = new WebSocket(WS_URL);
      setWs(socket);

      socket.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      socket.onclose = () => {
        setIsConnected(false);
        setTimeout(connect, 3000);
      };

      socket.onerror = (event) => {
        setError('WebSocket error occurred');
        setIsConnected(false);
      };

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect');
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      ws?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((message: string) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ content: message }));
      return true;
    }
    return false;
  }, [ws]);

  const subscribeToMessages = useCallback((
    onMessage: (message: WebSocketMessage) => void
  ) => {
    if (!ws) return;

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        if (message.type === 'stream') {
          // Accumulate message content
          setMessageBuffer(prev => prev + (message.content || ''));
        } else if (message.type === 'token') {
          // Handle complete message
          const completeMessage: WebSocketMessage = {
            ...message,
            content: messageBuffer + (message.content || ''),
          };
          setLastMessage(completeMessage);
          onMessage(completeMessage);
          setMessageBuffer(''); // Clear buffer after sending complete message
        } else if (message.type === 'end') {
          // Handle end of message stream
          const finalMessage: WebSocketMessage = {
            type: 'final',
            content: messageBuffer,
          };
          setLastMessage(finalMessage);
          onMessage(finalMessage);
          setMessageBuffer(''); // Clear buffer after final message
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };
  }, [ws, messageBuffer]);

  return {
    isConnected,
    error,
    sendMessage,
    subscribeToMessages,
    lastMessage,
  };
}

export default useWebSocket;
