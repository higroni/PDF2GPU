/**
 * ChatMessage Component
 * Prikazuje pojedinačnu chat poruku (user ili assistant)
 */
import React, { useState } from 'react';
import { Box, Paper, Typography, Avatar, IconButton, Tooltip, Chip } from '@mui/material';
import {
  Person,
  SmartToy,
  ThumbUp,
  ThumbDown,
  ThumbUpOutlined,
  ThumbDownOutlined,
  ContentCopy,
  Check,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

export interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  messageId?: number;
  sources?: Array<{ filename: string; page?: number }>;
  onFeedback?: (messageId: number, isPositive: boolean) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  timestamp,
  messageId,
  sources,
  onFeedback,
}) => {
  const isUser = role === 'user';
  const isSystem = role === 'system';
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);
  const [copied, setCopied] = useState(false);

  const handleFeedback = (isPositive: boolean) => {
    const newFeedback = feedback === (isPositive ? 'positive' : 'negative') ? null : (isPositive ? 'positive' : 'negative');
    setFeedback(newFeedback);
    if (messageId && onFeedback) {
      onFeedback(messageId, isPositive);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  if (isSystem) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
        <Typography variant="caption" color="text.secondary">
          {content}
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: isUser ? 'row-reverse' : 'row',
          alignItems: 'flex-start',
          maxWidth: '75%',
          gap: 1,
        }}
      >
        <Avatar
          sx={{
            bgcolor: isUser ? 'primary.main' : 'secondary.main',
            width: 32,
            height: 32,
          }}
        >
          {isUser ? <Person fontSize="small" /> : <SmartToy fontSize="small" />}
        </Avatar>

        <Paper
          elevation={1}
          sx={{
            p: 2,
            bgcolor: isUser ? 'primary.light' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
            borderRadius: 2,
          }}
        >
          <Box sx={{ mb: 0.5 }}>
            {isUser ? (
              <Typography variant="body1">{content}</Typography>
            ) : (
              <ReactMarkdown
                components={{
                  p: ({ children }: { children?: React.ReactNode }) => (
                    <Typography variant="body1" component="span" sx={{ display: 'block', mb: 1 }}>
                      {children}
                    </Typography>
                  ),
                  code: ({ children }: { children?: React.ReactNode }) => (
                    <Box
                      component="code"
                      sx={{
                        bgcolor: 'grey.100',
                        color: 'grey.900',
                        px: 0.5,
                        py: 0.25,
                        borderRadius: 0.5,
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                      }}
                    >
                      {children}
                    </Box>
                  ),
                  pre: ({ children }: { children?: React.ReactNode }) => (
                    <Box
                      component="pre"
                      sx={{
                        bgcolor: 'grey.100',
                        color: 'grey.900',
                        p: 1.5,
                        borderRadius: 1,
                        overflow: 'auto',
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                      }}
                    >
                      {children}
                    </Box>
                  ),
                }}
              >
                {content}
              </ReactMarkdown>
            )}
          </Box>

          {/* Sources */}
          {!isUser && sources && sources.length > 0 && (
            <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {sources.map((source, idx) => (
                <Chip
                  key={idx}
                  label={`${source.filename}${source.page ? ` (str. ${source.page})` : ''}`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              ))}
            </Box>
          )}

          {/* Timestamp and Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
            {timestamp && (
              <Typography variant="caption" color="text.secondary">
                {new Date(timestamp).toLocaleTimeString('sr-RS', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </Typography>
            )}

            {/* Feedback buttons for assistant messages */}
            {!isUser && (
              <Box sx={{ display: 'flex', gap: 0.5, ml: 'auto' }}>
                <Tooltip title="Kopiraj">
                  <IconButton size="small" onClick={handleCopy}>
                    {copied ? <Check fontSize="small" /> : <ContentCopy fontSize="small" />}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Dobar odgovor">
                  <IconButton
                    size="small"
                    onClick={() => handleFeedback(true)}
                    color={feedback === 'positive' ? 'success' : 'default'}
                  >
                    {feedback === 'positive' ? (
                      <ThumbUp fontSize="small" />
                    ) : (
                      <ThumbUpOutlined fontSize="small" />
                    )}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Loš odgovor">
                  <IconButton
                    size="small"
                    onClick={() => handleFeedback(false)}
                    color={feedback === 'negative' ? 'error' : 'default'}
                  >
                    {feedback === 'negative' ? (
                      <ThumbDown fontSize="small" />
                    ) : (
                      <ThumbDownOutlined fontSize="small" />
                    )}
                  </IconButton>
                </Tooltip>
              </Box>
            )}
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatMessage;

// Made with Bob
