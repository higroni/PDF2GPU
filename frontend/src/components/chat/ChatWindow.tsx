/**
 * ChatWindow Component
 * Glavni chat prozor koji integriše MessageList i MessageInput
 */
import React, { useState, useCallback, useEffect } from 'react';
import { Box, Paper, Typography, IconButton, Chip } from '@mui/material';
import { Close, Refresh } from '@mui/icons-material';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { useWebSocket, WebSocketMessage } from '../../hooks/useWebSocket';
import { ChatMessageProps } from './ChatMessage';

export interface ChatWindowProps {
  sessionId: string | null;
  collectionId?: number;
  collectionName?: string;
  onClose?: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  sessionId,
  collectionId,
  collectionName,
  onClose,
}) => {
  const [messages, setMessages] = useState<ChatMessageProps[]>([]);
  const [streamingContent, setStreamingContent] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'status':
        console.log('Status:', message.content);
        break;

      case 'context':
        console.log('Context retrieved:', message.content);
        break;

      case 'token':
        // Append token to streaming content
        setStreamingContent((prev) => prev + message.content);
        break;

      case 'complete':
        // Finalize the assistant message
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: streamingContent + message.content,
            timestamp: new Date().toISOString(),
          },
        ]);
        setStreamingContent('');
        setIsProcessing(false);
        break;

      case 'error':
        console.error('WebSocket error:', message.content);
        setMessages((prev) => [
          ...prev,
          {
            role: 'system',
            content: `Greška: ${message.content}`,
            timestamp: new Date().toISOString(),
          },
        ]);
        setStreamingContent('');
        setIsProcessing(false);
        break;

      case 'pong':
        console.log('Pong received');
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  }, [streamingContent]);

  const { isConnected, isConnecting, sendQuery } = useWebSocket(sessionId, {
    onMessage: handleWebSocketMessage,
    onConnect: () => console.log('Connected to chat'),
    onDisconnect: () => console.log('Disconnected from chat'),
    onError: (error) => console.error('WebSocket error:', error),
  });

  const handleSendMessage = useCallback(
    (content: string) => {
      if (!isConnected || isProcessing) return;

      // Add user message to the list
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          content,
          timestamp: new Date().toISOString(),
        },
      ]);

      // Send query via WebSocket
      setIsProcessing(true);
      setStreamingContent('');
      sendQuery(content, collectionId, true);
    },
    [isConnected, isProcessing, sendQuery, collectionId]
  );

  const handleRefresh = () => {
    setMessages([]);
    setStreamingContent('');
    setIsProcessing(false);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          bgcolor: 'primary.main',
          color: 'white',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6">Chat</Typography>
          {collectionName && (
            <Chip
              label={collectionName}
              size="small"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
              }}
            />
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {/* Connection status */}
          <Chip
            label={isConnecting ? 'Povezivanje...' : isConnected ? 'Povezano' : 'Nije povezano'}
            size="small"
            color={isConnected ? 'success' : 'default'}
            sx={{
              bgcolor: isConnected ? 'success.main' : 'rgba(255, 255, 255, 0.2)',
              color: 'white',
            }}
          />

          <IconButton size="small" onClick={handleRefresh} sx={{ color: 'white' }}>
            <Refresh />
          </IconButton>

          {onClose && (
            <IconButton size="small" onClick={onClose} sx={{ color: 'white' }}>
              <Close />
            </IconButton>
          )}
        </Box>
      </Box>

      {/* Messages */}
      <MessageList
        messages={messages}
        isLoading={isProcessing && !streamingContent}
        streamingContent={streamingContent}
      />

      {/* Input */}
      <MessageInput
        onSend={handleSendMessage}
        disabled={!isConnected || isProcessing}
        placeholder={
          isConnected
            ? 'Unesite pitanje...'
            : 'Čekanje na konekciju...'
        }
      />
    </Paper>
  );
};

export default ChatWindow;

// Made with Bob
