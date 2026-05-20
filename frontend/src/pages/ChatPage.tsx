/**
 * ChatPage
 * Stranica za chat funkcionalnost sa selekcijom kolekcije
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
} from '@mui/material';
import { Chat as ChatIcon } from '@mui/icons-material';
import ChatWindow from '../components/chat/ChatWindow';
import { useCollections } from '../hooks/useCollections';
import { apiClient } from '../api/client';

export const ChatPage: React.FC = () => {
  const [selectedCollectionId, setSelectedCollectionId] = useState<number | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: collections, isLoading: isLoadingCollections } = useCollections();

  // Auto-select first collection if available
  useEffect(() => {
    if (collections && collections.length > 0 && !selectedCollectionId) {
      setSelectedCollectionId(collections[0].id);
    }
  }, [collections, selectedCollectionId]);

  const handleStartChat = async () => {
    if (!selectedCollectionId) {
      setError('Molimo izaberite kolekciju');
      return;
    }

    setIsCreatingSession(true);
    setError(null);

    try {
      const response = await apiClient.post('/api/chat/sessions', {
        collection_id: selectedCollectionId,
      });

      console.log('Session response:', response.data);
      setSessionId(response.data.id?.toString() || response.data.session_id?.toString());
    } catch (err: any) {
      console.error('Failed to create chat session:', err);
      setError(err.response?.data?.detail || 'Greška pri kreiranju chat sesije');
    } finally {
      setIsCreatingSession(false);
    }
  };

  const handleEndChat = () => {
    setSessionId(null);
    setError(null);
  };

  const selectedCollection = collections?.find((c) => c.id === selectedCollectionId);

  if (sessionId) {
    return (
      <Container maxWidth="xl" sx={{ height: 'calc(100vh - 100px)', py: 3 }}>
        <ChatWindow
          sessionId={sessionId}
          collectionId={selectedCollectionId || undefined}
          collectionName={selectedCollection?.name}
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
          Izaberite kolekciju i započnite razgovor
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <FormControl fullWidth disabled={isLoadingCollections || isCreatingSession}>
          <InputLabel>Kolekcija</InputLabel>
          <Select
            value={selectedCollectionId || ''}
            onChange={(e) => setSelectedCollectionId(Number(e.target.value))}
            label="Kolekcija"
          >
            {isLoadingCollections ? (
              <MenuItem disabled>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Učitavanje...
              </MenuItem>
            ) : collections && collections.length > 0 ? (
              collections.map((collection) => (
                <MenuItem key={collection.id} value={collection.id}>
                  {collection.name} ({collection.pdf_count} dokumenata)
                </MenuItem>
              ))
            ) : (
              <MenuItem disabled>Nema dostupnih kolekcija</MenuItem>
            )}
          </Select>
        </FormControl>

        <Button
          variant="contained"
          size="large"
          onClick={handleStartChat}
          disabled={!selectedCollectionId || isCreatingSession}
          startIcon={isCreatingSession ? <CircularProgress size={20} /> : <ChatIcon />}
        >
          {isCreatingSession ? 'Kreiranje sesije...' : 'Započni chat'}
        </Button>

        {collections && collections.length === 0 && !isLoadingCollections && (
          <Alert severity="info">
            Nemate kreiranih kolekcija. Prvo kreirajte kolekciju i dodajte PDF dokumente.
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default ChatPage;

// Made with Bob
