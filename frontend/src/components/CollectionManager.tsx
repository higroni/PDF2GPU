/**
 * CollectionManager Component
 * Komponenta za upravljanje kolekcijama (kreiranje, editovanje, brisanje)
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { apiClient } from '../api/client';

interface CollectionManagerProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  collection?: {
    id: number;
    name: string;
    description?: string;
  };
  mode: 'create' | 'edit';
}

export const CollectionManager: React.FC<CollectionManagerProps> = ({
  open,
  onClose,
  onSuccess,
  collection,
  mode,
}) => {
  const [name, setName] = useState(collection?.name || '');
  const [description, setDescription] = useState(collection?.description || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    if (open) {
      setName(collection?.name || '');
      setDescription(collection?.description || '');
      setError(null);
    }
  }, [open, collection]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('Ime kolekcije je obavezno');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      if (mode === 'create') {
        await apiClient.post('/api/collections', {
          name: name.trim(),
          description: description.trim() || undefined,
        });
      } else {
        await apiClient.put(`/api/collections/${collection?.id}`, {
          name: name.trim(),
          description: description.trim() || undefined,
        });
      }

      if (onSuccess) {
        onSuccess();
      }
      handleClose();
    } catch (err: any) {
      console.error('Failed to save collection:', err);
      setError(err.response?.data?.detail || 'Greška pri čuvanju kolekcije');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setName('');
      setDescription('');
      setError(null);
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {mode === 'create' ? 'Kreiraj novu kolekciju' : 'Izmeni kolekciju'}
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <TextField
              label="Ime kolekcije"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              fullWidth
              autoFocus
              disabled={isSubmitting}
              helperText="Unesite jedinstveno ime za kolekciju"
            />

            <TextField
              label="Opis"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              multiline
              rows={3}
              disabled={isSubmitting}
              helperText="Opcioni opis kolekcije"
            />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Otkaži
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting || !name.trim()}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
          >
            {isSubmitting
              ? 'Čuvanje...'
              : mode === 'create'
              ? 'Kreiraj'
              : 'Sačuvaj'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CollectionManager;

// Made with Bob
