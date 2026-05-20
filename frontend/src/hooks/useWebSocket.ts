/**
 * WebSocket Hook
 * Custom hook za WebSocket komunikaciju sa chat serverom
 */
import { useEffect, useRef, useState, useCallback } from 'react';

export interface WebSocketMessage {
  type: 'status' | 'context' | 'token' | 'complete' | 'error' | 'pong';
  content: any;
}

export interface WebSocketHookOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export const useWebSocket = (sessionId: string | null, options: WebSocketHookOptions = {}) => {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  const connect = useCallback(() => {
    if (!sessionId || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);

    const wsUrl = `ws://localhost:8000/api/chat/ws/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setIsConnecting(false);
      onConnect?.();
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        onMessage?.(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnecting(false);
      onError?.(error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setIsConnecting(false);
      onDisconnect?.();

      // Auto-reconnect
      if (autoReconnect && sessionId) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, reconnectInterval);
      }
    };

    wsRef.current = ws;
  }, [sessionId, onMessage, onConnect, onDisconnect, onError, autoReconnect, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

  const sendQuery = useCallback(
    (query: string, collectionId?: number, useContext: boolean = true) => {
      sendMessage({
        type: 'query',
        content: query,
        collection_id: collectionId,
        use_context: useContext,
      });
    },
    [sendMessage]
  );

  const ping = useCallback(() => {
    sendMessage({ type: 'ping' });
  }, [sendMessage]);

  // Connect on mount if sessionId is provided
  useEffect(() => {
    if (sessionId) {
      connect();
    }

    // Cleanup only on unmount or when sessionId changes
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [sessionId]); // FIXED: Removed connect/disconnect from dependencies

  // Ping every 20 seconds to keep connection alive (before backend 30s timeout)
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      ping();
    }, 20000); // FIXED: Changed from 30s to 20s

    return () => clearInterval(interval);
  }, [isConnected, ping]);

  return {
    isConnected,
    isConnecting,
    connect,
    disconnect,
    sendMessage,
    sendQuery,
    ping,
  };
};

export default useWebSocket;

// Made with Bob
