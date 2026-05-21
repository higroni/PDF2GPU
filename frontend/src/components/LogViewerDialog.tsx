/**
 * LogViewerDialog
 * Real-time log viewer for evaluation execution
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Paper,
  IconButton,
  Chip
} from '@mui/material';
import {
  Close,
  Download,
  Clear,
  Stop
} from '@mui/icons-material';
import { stopEvaluation } from '../api/evaluations';

interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG';
  message: string;
}

interface LogViewerDialogProps {
  open: boolean;
  onClose: () => void;
  evaluationId: number;
  evaluationName: string;
}

const LogViewerDialog: React.FC<LogViewerDialogProps> = ({
  open,
  onClose,
  evaluationId,
  evaluationName
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && evaluationId) {
      connectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [open, evaluationId]);

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8000/ws/evaluation/${evaluationId}/logs`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected for logs');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const logEntry: LogEntry = JSON.parse(event.data);
        setLogs(prev => [...prev, logEntry]);
      } catch (error) {
        console.error('Failed to parse log entry:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const handleClearLogs = () => {
    setLogs([]);
  };

  const handleDownloadLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp}] ${log.level}: ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evaluation_${evaluationId}_logs.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleStopEvaluation = async () => {
    try {
      setIsStopping(true);
      await stopEvaluation(evaluationId);
      // Log will be updated via WebSocket
    } catch (error) {
      console.error('Failed to stop evaluation:', error);
      alert('Greška pri zaustavljanju evaluacije');
    } finally {
      setIsStopping(false);
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR': return 'error';
      case 'WARNING': return 'warning';
      case 'INFO': return 'info';
      case 'DEBUG': return 'default';
      default: return 'default';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '80vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h6">
              Log Evaluacije: {evaluationName}
            </Typography>
            <Box display="flex" gap={1} mt={1}>
              <Chip
                label={isConnected ? 'Povezano' : 'Nije povezano'}
                color={isConnected ? 'success' : 'error'}
                size="small"
              />
              <Chip
                label={`${logs.length} poruka`}
                size="small"
              />
            </Box>
          </Box>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Paper
          elevation={0}
          sx={{
            bgcolor: '#1e1e1e',
            color: '#d4d4d4',
            p: 2,
            height: '100%',
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: '0.875rem'
          }}
        >
          {logs.length === 0 ? (
            <Typography color="text.secondary" align="center">
              Nema log poruka...
            </Typography>
          ) : (
            logs.map((log, index) => (
              <Box
                key={index}
                sx={{
                  mb: 0.5,
                  p: 0.5,
                  borderRadius: 1,
                  '&:hover': {
                    bgcolor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                <Box display="flex" gap={1} alignItems="center">
                  <Typography
                    component="span"
                    sx={{
                      color: '#858585',
                      fontSize: '0.75rem',
                      minWidth: '140px'
                    }}
                  >
                    {log.timestamp}
                  </Typography>
                  <Chip
                    label={log.level}
                    color={getLevelColor(log.level) as any}
                    size="small"
                    sx={{ minWidth: '80px', fontSize: '0.7rem' }}
                  />
                  <Typography
                    component="span"
                    sx={{
                      color: log.level === 'ERROR' ? '#f48771' : 
                             log.level === 'WARNING' ? '#dcdcaa' : 
                             '#d4d4d4'
                    }}
                  >
                    {log.message}
                  </Typography>
                </Box>
              </Box>
            ))
          )}
          <div ref={logEndRef} />
        </Paper>
      </DialogContent>

      <DialogActions>
        <Button
          startIcon={<Stop />}
          onClick={handleStopEvaluation}
          disabled={isStopping}
          color="error"
          variant="contained"
        >
          {isStopping ? 'Zaustavljanje...' : 'Zaustavi Evaluaciju'}
        </Button>
        <Box sx={{ flexGrow: 1 }} />
        <Button
          startIcon={<Clear />}
          onClick={handleClearLogs}
          disabled={logs.length === 0}
        >
          Obriši Log
        </Button>
        <Button
          startIcon={<Download />}
          onClick={handleDownloadLogs}
          disabled={logs.length === 0}
        >
          Preuzmi Log
        </Button>
        <Button onClick={onClose} variant="contained">
          Zatvori
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LogViewerDialog;

// Made with Bob