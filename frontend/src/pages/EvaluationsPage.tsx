/**
 * Evaluations Page
 * Stranica za pokretanje i praćenje evaluacija
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Tooltip,
  Stack,
  LinearProgress,
  Card,
  CardContent,
  Grid,
  Checkbox,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  Compare as CompareIcon,
} from '@mui/icons-material';
import {
  getEvaluations,
  createEvaluation,
  runEvaluation,
  deleteEvaluation,
  getEvaluation,
  getEvaluationStatistics,
  pollEvaluationStatus,
  Evaluation,
  EvaluationCreate,
  EvaluationRun,
  EvaluationStatistics,
} from '../api/evaluations';
import { getTestExamples, TestExample } from '../api/testExamples';
import { collectionsApi } from '../api/collections';
import type { Collection } from '../types/api';

const EvaluationsPage: React.FC = () => {
  const navigate = useNavigate();
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [testExamples, setTestExamples] = useState<TestExample[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [statsDialogOpen, setStatsDialogOpen] = useState(false);
  const [selectedEvaluation, setSelectedEvaluation] = useState<Evaluation | null>(null);
  const [statistics, setStatistics] = useState<EvaluationStatistics | null>(null);
  
  // Compare states
  const [selectedForCompare, setSelectedForCompare] = useState<number[]>([]);
  
  // Form states
  const [createForm, setCreateForm] = useState<EvaluationCreate>({
    name: '',
    description: '',
  });
  
  const [runForm, setRunForm] = useState<EvaluationRun>({
    test_example_ids: undefined,
    collection_id: undefined,
  });
  
  // Polling states
  const [pollingEvaluations, setPollingEvaluations] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [evaluationsData, collectionsData, examplesData] = await Promise.all([
        getEvaluations(),
        collectionsApi.getAll(),
        getTestExamples(),
      ]);
      
      setEvaluations(evaluationsData);
      setCollections(collectionsData);
      setTestExamples(examplesData);
      
      // Start polling for running evaluations
      evaluationsData.forEach(evaluation => {
        if (evaluation.status === 'running' && !pollingEvaluations.has(evaluation.id)) {
          startPolling(evaluation.id);
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const startPolling = (evaluationId: number) => {
    setPollingEvaluations(prev => new Set(prev).add(evaluationId));
    
    pollEvaluationStatus(evaluationId, (updatedEvaluation) => {
      setEvaluations(prev =>
        prev.map(e => e.id === evaluationId ? updatedEvaluation : e)
      );
      
      if (updatedEvaluation.status !== 'running') {
        setPollingEvaluations(prev => {
          const newSet = new Set(prev);
          newSet.delete(evaluationId);
          return newSet;
        });
      }
    });
  };

  const handleCreate = async () => {
    try {
      const newEvaluation = await createEvaluation(createForm);
      setEvaluations(prev => [newEvaluation, ...prev]);
      setCreateDialogOpen(false);
      resetCreateForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create evaluation');
    }
  };

  const handleRun = async () => {
    if (!selectedEvaluation) return;
    
    try {
      await runEvaluation(selectedEvaluation.id, runForm);
      setRunDialogOpen(false);
      resetRunForm();
      startPolling(selectedEvaluation.id);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run evaluation');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Da li ste sigurni da želite da obrišete ovu evaluaciju?')) {
      return;
    }
    
    try {
      await deleteEvaluation(id);
      setEvaluations(prev => prev.filter(e => e.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete evaluation');
    }
  };

  const handleViewStatistics = async (evaluation: Evaluation) => {
    try {
      const stats = await getEvaluationStatistics(evaluation.id);
      setStatistics(stats);
      setSelectedEvaluation(evaluation);
      setStatsDialogOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load statistics');
    }
  };

  const openRunDialog = (evaluation: Evaluation) => {
    setSelectedEvaluation(evaluation);
    resetRunForm();
    setRunDialogOpen(true);
  };

  const resetCreateForm = () => {
    setCreateForm({
      name: '',
      description: '',
    });
  };

  const resetRunForm = () => {
    setRunForm({
      test_example_ids: undefined,
      collection_id: undefined,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'info';
      case 'failed': return 'error';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const formatMetric = (value?: number) => {
    return value !== undefined && value !== null ? value.toFixed(3) : 'N/A';
  };

  const formatPercentage = (value?: number) => {
    return value !== undefined && value !== null ? `${value.toFixed(1)}%` : 'N/A';
  };

  const handleCompareCheckbox = (evaluationId: number) => {
    setSelectedForCompare(prev => {
      if (prev.includes(evaluationId)) {
        return prev.filter(id => id !== evaluationId);
      } else if (prev.length < 2) {
        return [...prev, evaluationId];
      } else {
        // Replace first selected with new one
        return [prev[1], evaluationId];
      }
    });
  };

  const handleCompare = () => {
    if (selectedForCompare.length === 2) {
      navigate(`/evaluations/compare/${selectedForCompare[0]}/${selectedForCompare[1]}`);
    }
  };

  const canCompare = selectedForCompare.length === 2;

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
          Evaluacije
        </Typography>
        
        <Stack direction="row" spacing={2}>
          {selectedForCompare.length > 0 && (
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => setSelectedForCompare([])}
            >
              Poništi selekciju ({selectedForCompare.length})
            </Button>
          )}
          
          <Button
            variant="contained"
            color="secondary"
            startIcon={<CompareIcon />}
            onClick={handleCompare}
            disabled={!canCompare}
          >
            Uporedi {selectedForCompare.length > 0 ? `(${selectedForCompare.length}/2)` : ''}
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadData}
          >
            Osveži
          </Button>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Nova Evaluacija
          </Button>
        </Stack>
      </Box>

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
              <TableCell padding="checkbox">
                <Tooltip title="Izaberite 2 evaluacije za poređenje">
                  <CompareIcon color="action" />
                </Tooltip>
              </TableCell>
              <TableCell>ID</TableCell>
              <TableCell>Naziv</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Primeri</TableCell>
              <TableCell>BLEU</TableCell>
              <TableCell>ROUGE-L</TableCell>
              <TableCell>BERTScore</TableCell>
              <TableCell>Exact Match</TableCell>
              <TableCell>Kreirana</TableCell>
              <TableCell align="right">Akcije</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {evaluations.map((evaluation) => (
              <TableRow
                key={evaluation.id}
                selected={selectedForCompare.includes(evaluation.id)}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedForCompare.includes(evaluation.id)}
                    onChange={() => handleCompareCheckbox(evaluation.id)}
                    disabled={
                      evaluation.status !== 'completed' ||
                      (selectedForCompare.length >= 2 && !selectedForCompare.includes(evaluation.id))
                    }
                  />
                </TableCell>
                <TableCell>{evaluation.id}</TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {evaluation.name}
                  </Typography>
                  {evaluation.description && (
                    <Typography variant="caption" color="text.secondary">
                      {evaluation.description}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={evaluation.status}
                    size="small"
                    color={getStatusColor(evaluation.status) as any}
                  />
                  {evaluation.status === 'running' && (
                    <Box sx={{ mt: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={
                          evaluation.total_examples
                            ? (evaluation.completed_examples! / evaluation.total_examples) * 100
                            : 0
                        }
                      />
                      <Typography variant="caption">
                        {evaluation.completed_examples || 0} / {evaluation.total_examples || 0}
                      </Typography>
                    </Box>
                  )}
                </TableCell>
                <TableCell>
                  {evaluation.total_examples !== undefined && evaluation.total_examples !== null
                    ? `${evaluation.completed_examples || 0} / ${evaluation.total_examples}`
                    : 'Nije pokrenuta'}
                </TableCell>
                <TableCell>{formatMetric(evaluation.avg_bleu_score)}</TableCell>
                <TableCell>{formatMetric(evaluation.avg_rouge_l)}</TableCell>
                <TableCell>{formatMetric(evaluation.avg_bert_score)}</TableCell>
                <TableCell>{formatPercentage(evaluation.exact_match_percentage)}</TableCell>
                <TableCell>
                  {new Date(evaluation.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell align="right">
                  {evaluation.status === 'pending' && (
                    <Tooltip title="Pokreni">
                      <IconButton size="small" onClick={() => openRunDialog(evaluation)}>
                        <PlayIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                  {evaluation.status === 'completed' && (
                    <Tooltip title="Statistike">
                      <IconButton size="small" onClick={() => handleViewStatistics(evaluation)}>
                        <AssessmentIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                  <Tooltip title="Obriši">
                    <IconButton size="small" onClick={() => handleDelete(evaluation.id)}>
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
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Nova Evaluacija</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Naziv"
              value={createForm.name}
              onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
              fullWidth
              required
            />
            
            <TextField
              label="Opis (opciono)"
              multiline
              rows={3}
              value={createForm.description}
              onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Otkaži</Button>
          <Button onClick={handleCreate} variant="contained" disabled={!createForm.name}>
            Kreiraj
          </Button>
        </DialogActions>
      </Dialog>

      {/* Run Dialog */}
      <Dialog open={runDialogOpen} onClose={() => setRunDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Pokreni Evaluaciju</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Alert severity="info">
              Evaluacija će biti pokrenuta u pozadini. Možete pratiti napredak u tabeli.
            </Alert>
            
            <FormControl fullWidth>
              <InputLabel>Kolekcija (opciono)</InputLabel>
              <Select
                value={runForm.collection_id || ''}
                onChange={(e) => setRunForm({ ...runForm, collection_id: e.target.value as number })}
                label="Kolekcija (opciono)"
              >
                <MenuItem value="">Sve kolekcije</MenuItem>
                {collections.map((col) => (
                  <MenuItem key={col.id} value={col.id}>
                    {col.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Typography variant="body2" color="text.secondary">
              Napomena: Ako ne izaberete test primere, koristiće se svi aktivni primeri.
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRunDialogOpen(false)}>Otkaži</Button>
          <Button onClick={handleRun} variant="contained" startIcon={<PlayIcon />}>
            Pokreni
          </Button>
        </DialogActions>
      </Dialog>

      {/* Statistics Dialog */}
      <Dialog open={statsDialogOpen} onClose={() => setStatsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Statistike Evaluacije</DialogTitle>
        <DialogContent>
          {statistics && statistics.metrics && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                {/* Overview */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Pregled
                      </Typography>
                      <Stack direction="row" spacing={4}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Ukupno primera
                          </Typography>
                          <Typography variant="h6">{statistics.total_examples}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Status
                          </Typography>
                          <Chip label={statistics.status} size="small" color="success" />
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* BLEU Score */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        BLEU Score
                      </Typography>
                      <Stack spacing={1}>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">Prosek:</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatMetric(statistics.metrics?.bleu_score?.avg)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">Min:</Typography>
                          <Typography variant="body2">
                            {formatMetric(statistics.metrics?.bleu_score?.min)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">Max:</Typography>
                          <Typography variant="body2">
                            {formatMetric(statistics.metrics?.bleu_score?.max)}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* ROUGE Scores */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        ROUGE Scores
                      </Typography>
                      <Stack spacing={1}>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">ROUGE-1:</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatMetric(statistics.metrics?.rouge_1?.avg)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">ROUGE-2:</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatMetric(statistics.metrics?.rouge_2?.avg)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">ROUGE-L:</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatMetric(statistics.metrics?.rouge_l?.avg)}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* BERTScore */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        BERTScore
                      </Typography>
                      <Stack spacing={1}>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">F1 Prosek:</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatMetric(statistics.metrics?.bert_score_f1?.avg)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">Min:</Typography>
                          <Typography variant="body2">
                            {formatMetric(statistics.metrics?.bert_score_f1?.min)}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">Max:</Typography>
                          <Typography variant="body2">
                            {formatMetric(statistics.metrics?.bert_score_f1?.max)}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Exact Match */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Exact Match
                      </Typography>
                      <Stack spacing={1}>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">Broj:</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {statistics.metrics?.exact_match?.count ?? 0}
                          </Typography>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2">Procenat:</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatPercentage(statistics.metrics?.exact_match?.percentage)}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
          {statistics && !statistics.metrics && (
            <Box sx={{ mt: 2 }}>
              <Alert severity="info">
                Evaluacija još nema rezultate. Pokrenite evaluaciju da biste videli statistike.
              </Alert>
            </Box>
          )}
          {!statistics && (
            <Box sx={{ mt: 2 }}>
              <CircularProgress />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStatsDialogOpen(false)}>Zatvori</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default EvaluationsPage;

// Made with Bob
