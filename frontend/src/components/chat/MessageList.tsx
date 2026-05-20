/**
 * MessageList Component
 * Prikazuje listu chat poruka sa auto-scroll funkcijom
 */
import React, { useEffect, useRef } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import ChatMessage, { ChatMessageProps } from './ChatMessage';

export interface MessageListProps {
  messages: ChatMessageProps[];
  isLoading?: boolean;
  streamingContent?: string;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading = false,
  streamingContent,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          color: 'text.secondary',
        }}
      >
        <Typography variant="h6" gutterBottom>
          Dobrodošli u PDF2GPU Chat
        </Typography>
        <Typography variant="body2">
          Postavite pitanje o vašim dokumentima
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        flex: 1,
        overflowY: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          role={message.role}
          content={message.content}
          timestamp={message.timestamp}
        />
      ))}

      {/* Streaming message (assistant typing) */}
      {streamingContent && (
        <ChatMessage
          role="assistant"
          content={streamingContent}
        />
      )}

      {/* Loading indicator */}
      {isLoading && !streamingContent && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            my: 2,
          }}
        >
          <CircularProgress size={20} />
          <Typography variant="body2" color="text.secondary">
            Razmišljam...
          </Typography>
        </Box>
      )}

      {/* Invisible element for auto-scroll */}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default MessageList;

// Made with Bob
