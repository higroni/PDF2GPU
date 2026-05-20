/**
 * Test Examples Page
 * Stranica za upravljanje test primerima
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Alert,
  Tooltip,
  Stack,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  VisibilityOff as HideIcon,
} from '@mui/icons-material';
import {
  getTestExamples,
  createTestExample,
  updateTestExample,
  deleteTestExample,
  toggleTestExampleActive,
  getTestExampleStatistics,
  bulkImportTestExamples,
  bulkExportTestExamples,
  TestExample,
  TestExampleCreate,
  TestExampleUpdate,
  TestExampleStatistics,
} from '../api/testExamples';
import { collectionsApi } from '../api/collections';
import type { Collection } from '../types/api';

const TestExamplesPage: React.FC = () => {
  const [examples, setExamples] = useState<TestExample[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [statistics, setStatistics] = useState<TestExampleStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCollection, setSelectedCollection] = useState<number | undefined>();
  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedExample, setSelectedExample] = useState<TestExample | null>(null);
  
  // Form states
  const [formData, setFormData] = useState<TestExampleCreate>({
    question: '',
    expected_answer: '',
    category: '',
    difficulty: 'medium',
    collection_id: 0,
  });

  // Load data
  useEffect(() => {
    loadData();
  }, [selectedCollection]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [examplesData, collectionsData, statsData] = await Promise.all([
        getTestExamples(selectedCollection),
        collectionsApi.getAll(),
        getTestExampleStatistics(selectedCollection),
      ]);
      
      setExamples(examplesData);
      setCollections(collectionsData);
      setStatistics(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await createTestExample(formData);
      setCreateDialogOpen(false);
      resetForm();
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create test example');
    }
  };

  const handleEdit = async () => {
    if (!selectedExample) return;
    
    try {
      const updateData: TestExampleUpdate = {
        question: formData.question,
        expected_answer: formData.expected_answer,
        category: formData.category,
        difficulty: formData.difficulty,
      };
      
      await updateTestExample(selectedExample.id, updateData);
      setEditDialogOpen(false);
      setSelectedExample(null);
      resetForm();
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update test example');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Da li ste sigurni da želite da obrišete ovaj test primer?')) {
      return;
    }
    
    try {
      await deleteTestExample(id);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete test example');
    }
  };

  const handleToggleActive = async (example: TestExample) => {
    try {
      await toggleTestExampleActive(example.id, !example.is_active);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle active status');
    }
  };

  const handleExport = async () => {
    try {
      const blob = await bulkExportTestExamples(selectedCollection);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `test-examples-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export test examples');
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      
      if (!selectedCollection) {
        setError('Molimo izaberite kolekciju pre importa');
        return;
      }
      
      const result = await bulkImportTestExamples({
        examples: data,
        collection_id: selectedCollection,
      });
      
      alert(`Importovano: ${result.created}, Neuspešno: ${result.failed}`);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import test examples');
    }
  };

  const openCreateDialog = () => {
    resetForm();
    setFormData(prev => ({
      ...prev,
      collection_id: selectedCollection || collections[0]?.id || 0,
    }));
    setCreateDialogOpen(true);
  };

  const openEditDialog = (example: TestExample) => {
    setSelectedExample(example);
    setFormData({
      question: example.question,
      expected_answer: example.expected_answer,
      category: example.category || '',
      difficulty: example.difficulty,
      collection_id: example.collection_id,
    });
    setEditDialogOpen(true);
  };

  const openViewDialog = (example: TestExample) => {
    setSelectedExample(example);
    setViewDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      question: '',
      expected_answer: '',
      category: '',
      difficulty: 'medium',
      collection_id: selectedCollection || collections[0]?.id || 0,
    });
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Test Primeri
        </Typography>
        
        <Stack direction="row" spacing={2}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Kolekcija</InputLabel>
            <Select
              value={selectedCollection || ''}
              onChange={(e) => setSelectedCollection(e.target.value as number)}
              label="Kolekcija"
            >
              <MenuItem value="">Sve kolekcije</MenuItem>
              {collections.map((col) => (
                <MenuItem key={col.id} value={col.id}>
                  {col.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
          >
            Export
          </Button>
          
          <Button
            variant="outlined"
            component="label"
            startIcon={<UploadIcon />}
          >
            Import
            <input
              type="file"
              hidden
              accept=".json"
              onChange={handleImport}
            />
          </Button>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={openCreateDialog}
          >
            Novi Test Primer
          </Button>
        </Stack>
      </Box>

      {/* Statistics */}
      {statistics && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Statistika
          </Typography>
          <Stack direction="row" spacing={4}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Ukupno
              </Typography>
              <Typography variant="h6">{statistics.total}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Aktivni
              </Typography>
              <Typography variant="h6" color="success.main">
                {statistics.active}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Neaktivni
              </Typography>
              <Typography variant="h6" color="error.main">
                {statistics.inactive}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Easy / Medium / Hard
              </Typography>
              <Typography variant="h6">
                {statistics.by_difficulty.easy} / {statistics.by_difficulty.medium} / {statistics.by_difficulty.hard}
              </Typography>
            </Box>
          </Stack>
        </Paper>
      )}

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Pitanje</TableCell>
              <TableCell>Kategorija</TableCell>
              <TableCell>Težina</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Kolekcija</TableCell>
              <TableCell align="right">Akcije</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {examples.map((example) => (
              <TableRow key={example.id}>
                <TableCell>{example.id}</TableCell>
                <TableCell>
                  <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                    {example.question}
                  </Typography>
                </TableCell>
                <TableCell>
                  {example.category && (
                    <Chip label={example.category} size="small" />
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={example.difficulty}
                    size="small"
                    color={getDifficultyColor(example.difficulty) as any}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={example.is_active ? 'Aktivan' : 'Neaktivan'}
                    size="small"
                    color={example.is_active ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell>
                  {collections.find(c => c.id === example.collection_id)?.name}
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Prikaži">
                    <IconButton size="small" onClick={() => openViewDialog(example)}>
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Izmeni">
                    <IconButton size="small" onClick={() => openEditDialog(example)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title={example.is_active ? 'Deaktiviraj' : 'Aktiviraj'}>
                    <IconButton size="small" onClick={() => handleToggleActive(example)}>
                      {example.is_active ? <HideIcon /> : <ViewIcon />}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Obriši">
                    <IconButton size="small" onClick={() => handleDelete(example.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Novi Test Primer</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Kolekcija</InputLabel>
              <Select
                value={formData.collection_id}
                onChange={(e) => setFormData({ ...formData, collection_id: e.target.value as number })}
                label="Kolekcija"
              >
                {collections.map((col) => (
                  <MenuItem key={col.id} value={col.id}>
                    {col.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              label="Pitanje"
              multiline
              rows={3}
              value={formData.question}
              onChange={(e) => setFormData({ ...formData, question: e.target.value })}
              fullWidth
            />
            
            <TextField
              label="Očekivani Odgovor"
              multiline
              rows={4}
              value={formData.expected_answer}
              onChange={(e) => setFormData({ ...formData, expected_answer: e.target.value })}
              fullWidth
            />
            
            <TextField
              label="Kategorija (opciono)"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              fullWidth
            />
            
            <FormControl fullWidth>
              <InputLabel>Težina</InputLabel>
              <Select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value as any })}
                label="Težina"
              >
                <MenuItem value="easy">Easy</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="hard">Hard</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Otkaži</Button>
          <Button onClick={handleCreate} variant="contained">Kreiraj</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Izmeni Test Primer</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Pitanje"
              multiline
              rows={3}
              value={formData.question}
              onChange={(e) => setFormData({ ...formData, question: e.target.value })}
              fullWidth
            />
            
            <TextField
              label="Očekivani Odgovor"
              multiline
              rows={4}
              value={formData.expected_answer}
              onChange={(e) => setFormData({ ...formData, expected_answer: e.target.value })}
              fullWidth
            />
            
            <TextField
              label="Kategorija (opciono)"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              fullWidth
            />
            
            <FormControl fullWidth>
              <InputLabel>Težina</InputLabel>
              <Select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value as any })}
                label="Težina"
              >
                <MenuItem value="easy">Easy</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="hard">Hard</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Otkaži</Button>
          <Button onClick={handleEdit} variant="contained">Sačuvaj</Button>
        </DialogActions>
      </Dialog>

      {/* View Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Detalji Test Primera</DialogTitle>
        <DialogContent>
          {selectedExample && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  ID
                </Typography>
                <Typography>{selectedExample.id}</Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Pitanje
                </Typography>
                <Typography>{selectedExample.question}</Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Očekivani Odgovor
                </Typography>
                <Typography>{selectedExample.expected_answer}</Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Kategorija
                </Typography>
                <Typography>{selectedExample.category || 'N/A'}</Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Težina
                </Typography>
                <Chip
                  label={selectedExample.difficulty}
                  size="small"
                  color={getDifficultyColor(selectedExample.difficulty) as any}
                />
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Status
                </Typography>
                <Chip
                  label={selectedExample.is_active ? 'Aktivan' : 'Neaktivan'}
                  size="small"
                  color={selectedExample.is_active ? 'success' : 'default'}
                />
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Kreiran
                </Typography>
                <Typography>{new Date(selectedExample.created_at).toLocaleString()}</Typography>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Zatvori</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TestExamplesPage;

// Made with Bob
