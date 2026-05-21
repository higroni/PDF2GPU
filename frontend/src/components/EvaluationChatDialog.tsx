/**
 * EvaluationChatDialog
 * Dialog za chat sa konfiguracijom iz evaluacije
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  IconButton,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  Link,
  Popover,
  Paper,
} from '@mui/material';
import { Close as CloseIcon, Info as InfoIcon } from '@mui/icons-material';
import ChatWindow from './chat/ChatWindow';
import { createChatSessionFromEvaluation, type EvaluationChatSession } from '../api/evaluations';

interface EvaluationChatDialogProps {
  open: boolean;
  onClose: () => void;
  evaluationId: number;
  evaluationName: string;
}

export const EvaluationChatDialog: React.FC<EvaluationChatDialogProps> = ({
  open,
  onClose,
  evaluationId,
  evaluationName,
}) => {
  const [session, setSession] = useState<EvaluationChatSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [promptAnchor, setPromptAnchor] = useState<HTMLElement | null>(null);

  useEffect(() => {
    if (open && !session) {
      createSession();
    }
  }, [open]);

  const createSession = async () => {
    try {
      setLoading(true);
      setError(null);
      const sessionData = await createChatSessionFromEvaluation(evaluationId);
      setSession(sessionData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Greška pri kreiranju chat sesije');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSession(null);
    setError(null);
    setPromptAnchor(null);
    onClose();
  };

  const handlePromptClick = (event: React.MouseEvent<HTMLElement>) => {
    setPromptAnchor(event.currentTarget);
  };

  const handlePromptClose = () => {
    setPromptAnchor(null);
  };

  const getConfigSummary = () => {
    if (!session?.config) return null;
    
    const llm = session.config.llm || {};
    const search = session.config.search || {};
    const reranking = session.config.reranking || {};
    const chunking = session.config.chunking || {};
    
    return {
      model: llm.model || 'N/A',
      temperature: llm.temperature !== undefined ? llm.temperature : 'N/A',
      top_k: search.top_k || 'N/A',
      reranking: reranking.enabled ? 'Enabled' : 'Disabled',
      chunking: chunking.strategy || 'N/A',
      systemPrompt: llm.system_prompt || 'N/A'
    };
  };

  const configSummary = getConfigSummary();
  const promptOpen = Boolean(promptAnchor);

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="xl"
      fullWidth
      PaperProps={{
        sx: {
          height: '90vh',
          maxHeight: '90vh',
        },
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6">
            Chat - {evaluationName}
          </Typography>
          {session && configSummary && (
            <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap', gap: 0.5 }}>
              <Chip label={`Model: ${configSummary.model}`} size="small" color="primary" variant="outlined" />
              <Chip label={`Temp: ${configSummary.temperature}`} size="small" color="primary" variant="outlined" />
              <Chip label={`Top-K: ${configSummary.top_k}`} size="small" color="primary" variant="outlined" />
              <Chip label={`Reranking: ${configSummary.reranking}`} size="small" color="primary" variant="outlined" />
              <Chip label={`Chunking: ${configSummary.chunking}`} size="small" color="primary" variant="outlined" />
              <Link
                component="button"
                variant="caption"
                onClick={handlePromptClick}
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 1 }}
              >
                <InfoIcon fontSize="small" />
                Prikaži System Prompt
              </Link>
            </Stack>
          )}
        </Box>
        <IconButton onClick={handleClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      {/* System Prompt Popover */}
      <Popover
        open={promptOpen}
        anchorEl={promptAnchor}
        onClose={handlePromptClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
      >
        <Paper sx={{ p: 2, maxWidth: 600, maxHeight: 400, overflow: 'auto' }}>
          <Typography variant="subtitle2" gutterBottom>
            System Prompt:
          </Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem' }}>
            {configSummary?.systemPrompt || 'N/A'}
          </Typography>
        </Paper>
      </Popover>

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box sx={{ p: 3 }}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Box>
        )}

        {session && !loading && !error && (
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <ChatWindow
              sessionId={session.session_id.toString()}
              collectionId={session.collection_id}
              collectionName={evaluationName}
              evaluationConfig={session.config}
              onClose={handleClose}
            />
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default EvaluationChatDialog;

// Made with Bob
