/**
 * ChatPage
 * Stranica za chat funkcionalnost sa selekcijom evaluacije (konfiguracije)
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  Link,
  Popover,
  Paper,
  IconButton,
} from '@mui/material';
import { Chat as ChatIcon, Info as InfoIcon, Close as CloseIcon } from '@mui/icons-material';
import ChatWindow from '../components/chat/ChatWindow';
import { getEvaluations, createChatSessionFromEvaluation, type Evaluation, type EvaluationChatSession } from '../api/evaluations';

export const ChatPage: React.FC = () => {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [selectedEvaluationId, setSelectedEvaluationId] = useState<number | null>(null);
  const [session, setSession] = useState<EvaluationChatSession | null>(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [isLoadingEvaluations, setIsLoadingEvaluations] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [promptAnchor, setPromptAnchor] = useState<HTMLElement | null>(null);

  useEffect(() => {
    loadEvaluations();
  }, []);

  const loadEvaluations = async () => {
    try {
      setIsLoadingEvaluations(true);
      const data = await getEvaluations(0, 100);
      // Filter only evaluations with collection_id
      const validEvaluations = data.filter(e => e.collection_id);
      setEvaluations(validEvaluations);
      
      // Auto-select first evaluation if available
      if (validEvaluations.length > 0 && !selectedEvaluationId) {
        setSelectedEvaluationId(validEvaluations[0].id);
      }
    } catch (err) {
      setError('Greška pri učitavanju evaluacija');
    } finally {
      setIsLoadingEvaluations(false);
    }
  };

  const handleStartChat = async () => {
    if (!selectedEvaluationId) {
      setError('Molimo izaberite evaluaciju');
      return;
    }

    setIsCreatingSession(true);
    setError(null);

    try {
      const sessionData = await createChatSessionFromEvaluation(selectedEvaluationId);
      setSession(sessionData);
    } catch (err: any) {
      console.error('Failed to create chat session:', err);
      setError(err.response?.data?.detail || 'Greška pri kreiranju chat sesije');
    } finally {
      setIsCreatingSession(false);
    }
  };

  const handleEndChat = () => {
    setSession(null);
    setError(null);
    setPromptAnchor(null);
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

  const selectedEvaluation = evaluations.find(e => e.id === selectedEvaluationId);
  const configSummary = getConfigSummary();
  const promptOpen = Boolean(promptAnchor);

  if (session) {
    return (
      <Container maxWidth="xl" sx={{ height: 'calc(100vh - 100px)', py: 3 }}>
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6">
              Chat - {session.evaluation_name}
            </Typography>
            {configSummary && (
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
          <IconButton onClick={handleEndChat} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

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

        <ChatWindow
          sessionId={session.session_id.toString()}
          collectionId={session.collection_id}
          collectionName={session.evaluation_name}
          evaluationConfig={session.config}
          onClose={handleEndChat}
        />
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <ChatIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          Chat sa dokumentima
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Izaberite konfiguraciju i započnite razgovor
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <FormControl fullWidth disabled={isLoadingEvaluations || isCreatingSession}>
          <InputLabel>Konfiguracija</InputLabel>
          <Select
            value={selectedEvaluationId || ''}
            onChange={(e) => setSelectedEvaluationId(Number(e.target.value))}
            label="Konfiguracija"
          >
            {isLoadingEvaluations ? (
              <MenuItem disabled>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Učitavanje...
              </MenuItem>
            ) : evaluations.length > 0 ? (
              evaluations.map((evaluation) => (
                <MenuItem key={evaluation.id} value={evaluation.id}>
                  {evaluation.name} - {evaluation.status}
                </MenuItem>
              ))
            ) : (
              <MenuItem disabled>Nema dostupnih konfiguracija</MenuItem>
            )}
          </Select>
        </FormControl>

        <Button
          variant="contained"
          size="large"
          onClick={handleStartChat}
          disabled={!selectedEvaluationId || isCreatingSession}
          startIcon={isCreatingSession ? <CircularProgress size={20} /> : <ChatIcon />}
        >
          {isCreatingSession ? 'Kreiranje sesije...' : 'Započni chat'}
        </Button>

        {evaluations.length === 0 && !isLoadingEvaluations && (
          <Alert severity="info">
            Nemate dostupnih konfiguracija. Prvo kreirajte konfiguraciju u Evaluations sekciji.
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default ChatPage;

// Made with Bob
