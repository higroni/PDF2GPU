/**
 * EvaluationComparePage
 * Side-by-side comparison of two evaluations
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button
} from '@mui/material';
import {
  ExpandMore,
  TrendingUp,
  TrendingDown,
  Remove,
  CheckCircle,
  Error as ErrorIcon,
  ArrowBack
} from '@mui/icons-material';
import PerformanceBreakdown from '../components/PerformanceBreakdown';

interface ComparisonData {
  evaluation_1: {
    id: number;
    name: string;
    status: string;
    collection_id: number;
  };
  evaluation_2: {
    id: number;
    name: string;
    status: string;
    collection_id: number;
  };
  config_1: Record<string, any>;
  config_2: Record<string, any>;
  config_diff: {
    changed: Record<string, any>;
    added_in_2: Record<string, any>;
    removed_from_1: Record<string, any>;
  };
  metrics_comparison: Record<string, {
    eval1: number | null;
    eval2: number | null;
    diff: number | null;
    improvement_pct: number | null;
  }>;
  performance_comparison: Record<string, {
    eval1: number | null;
    eval2: number | null;
    diff: number | null;
  }>;
}

const EvaluationComparePage: React.FC = () => {
  const { id1, id2 } = useParams<{ id1: string; id2: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [comparison, setComparison] = useState<ComparisonData | null>(null);

  useEffect(() => {
    loadComparison();
  }, [id1, id2]);

  const loadComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/evaluations/compare/${id1}/${id2}`);
      if (!response.ok) {
        throw new Error('Failed to load comparison');
      }
      const data = await response.json();
      setComparison(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Greška pri učitavanju poređenja');
    } finally {
      setLoading(false);
    }
  };

  // Flatten nested config object to dot notation
  const flattenConfig = (obj: Record<string, any>, prefix = ''): Record<string, any> => {
    const result: Record<string, any> = {};
    
    for (const key in obj) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      
      if (obj[key] !== null && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
        Object.assign(result, flattenConfig(obj[key], fullKey));
      } else {
        result[fullKey] = obj[key];
      }
    }
    
    return result;
  };

  // Get all config parameters with comparison
  const getAllConfigParams = () => {
    if (!comparison) return [];
    
    const flat1 = flattenConfig(comparison.config_1);
    const flat2 = flattenConfig(comparison.config_2);
    
    // Get all unique keys
    const allKeys = new Set([...Object.keys(flat1), ...Object.keys(flat2)]);
    
    return Array.from(allKeys).sort().map(key => ({
      key,
      value1: flat1[key] !== undefined ? flat1[key] : '-',
      value2: flat2[key] !== undefined ? flat2[key] : '-',
      isDifferent: JSON.stringify(flat1[key]) !== JSON.stringify(flat2[key])
    }));
  };

  const renderTrendIcon = (diff: number | null | undefined) => {
    if (diff === null || diff === undefined || diff === 0) return <Remove color="disabled" />;
    if (diff > 0) return <TrendingUp color="success" />;
    return <TrendingDown color="error" />;
  };

  const renderImprovementChip = (improvement: number | null | undefined) => {
    if (improvement === null || improvement === undefined) return null;
    const color = improvement > 0 ? 'success' : improvement < 0 ? 'error' : 'default';
    const icon = improvement > 0 ? <TrendingUp /> : improvement < 0 ? <TrendingDown /> : <Remove />;
    return (
      <Chip
        icon={icon}
        label={`${improvement > 0 ? '+' : ''}${improvement.toFixed(2)}%`}
        color={color}
        size="small"
      />
    );
  };

  const formatValue = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return 'N/A';
    if (value < 1) return value.toFixed(3);
    if (value < 100) return value.toFixed(2);
    return value.toFixed(0);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Učitavanje poređenja...
        </Typography>
      </Container>
    );
  }

  if (error || !comparison) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Greška pri učitavanju poređenja'}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/evaluations')}
          variant="outlined"
        >
          Nazad na Evaluacije
        </Button>
        <Box>
          <Typography variant="h4">
            Poređenje Evaluacija
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Poređenje konfiguracija, metrika i performansi
          </Typography>
        </Box>
      </Box>

      {/* Evaluation Headers */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6}>
          <Paper elevation={2} sx={{ p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
            <Typography variant="h6">{comparison.evaluation_1.name}</Typography>
            <Chip
              label={comparison.evaluation_1.status}
              size="small"
              sx={{ mt: 1, bgcolor: 'white', color: 'primary.main' }}
            />
          </Paper>
        </Grid>
        <Grid item xs={6}>
          <Paper elevation={2} sx={{ p: 2, bgcolor: 'secondary.light', color: 'secondary.contrastText' }}>
            <Typography variant="h6">{comparison.evaluation_2.name}</Typography>
            <Chip
              label={comparison.evaluation_2.status}
              size="small"
              sx={{ mt: 1, bgcolor: 'white', color: 'secondary.main' }}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* Config Comparison - Show ALL parameters */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">Poređenje Konfiguracije</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Parametar</TableCell>
                  <TableCell>{comparison.evaluation_1.name}</TableCell>
                  <TableCell>{comparison.evaluation_2.name}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {getAllConfigParams().map(({ key, value1, value2, isDifferent }) => (
                  <TableRow
                    key={key}
                    sx={{
                      bgcolor: isDifferent ? 'warning.light' : 'inherit',
                      '&:hover': {
                        bgcolor: isDifferent ? 'warning.main' : 'action.hover'
                      }
                    }}
                  >
                    <TableCell>
                      <strong>{key}</strong>
                      {isDifferent && (
                        <Chip
                          label="Različito"
                          color="warning"
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      {typeof value1 === 'object' ? JSON.stringify(value1) : String(value1)}
                    </TableCell>
                    <TableCell>
                      {typeof value2 === 'object' ? JSON.stringify(value2) : String(value2)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* Metrics Comparison */}
      <Accordion defaultExpanded sx={{ mt: 2 }}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">Poređenje Metrika</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Metrika</TableCell>
                  <TableCell align="right">{comparison.evaluation_1.name}</TableCell>
                  <TableCell align="right">{comparison.evaluation_2.name}</TableCell>
                  <TableCell align="right">Razlika</TableCell>
                  <TableCell align="right">Poboljšanje</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(comparison.metrics_comparison).map(([metric, data]) => (
                  <TableRow key={metric}>
                    <TableCell><strong>{metric.replace(/_/g, ' ').toUpperCase()}</strong></TableCell>
                    <TableCell align="right">{formatValue(data.eval1)}</TableCell>
                    <TableCell align="right">{formatValue(data.eval2)}</TableCell>
                    <TableCell align="right">
                      <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                        {renderTrendIcon(data.diff)}
                        {formatValue(data.diff)}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      {renderImprovementChip(data.improvement_pct)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* Performance Comparison */}
      <Accordion defaultExpanded sx={{ mt: 2 }}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">Poređenje Performansi</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                {comparison.evaluation_1.name}
              </Typography>
              <PerformanceBreakdown
                metrics={{
                  avg_query_processing_ms: comparison.performance_comparison.query_processing_ms?.eval1 ?? undefined,
                  avg_search_ms: comparison.performance_comparison.search_ms?.eval1 ?? undefined,
                  avg_reranking_ms: comparison.performance_comparison.reranking_ms?.eval1 ?? undefined,
                  avg_llm_generation_ms: comparison.performance_comparison.llm_generation_ms?.eval1 ?? undefined,
                  avg_total_latency_ms: comparison.performance_comparison.total_latency_ms?.eval1 ?? undefined
                }}
                title=""
                showTotal={false}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                {comparison.evaluation_2.name}
              </Typography>
              <PerformanceBreakdown
                metrics={{
                  avg_query_processing_ms: comparison.performance_comparison.query_processing_ms?.eval2 ?? undefined,
                  avg_search_ms: comparison.performance_comparison.search_ms?.eval2 ?? undefined,
                  avg_reranking_ms: comparison.performance_comparison.reranking_ms?.eval2 ?? undefined,
                  avg_llm_generation_ms: comparison.performance_comparison.llm_generation_ms?.eval2 ?? undefined,
                  avg_total_latency_ms: comparison.performance_comparison.total_latency_ms?.eval2 ?? undefined
                }}
                title=""
                showTotal={false}
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="subtitle2" gutterBottom>
            Razlike u Performansama
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Faza</TableCell>
                  <TableCell align="right">Razlika (ms)</TableCell>
                  <TableCell align="right">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(comparison.performance_comparison).map(([phase, data]) => {
                  const isFaster = (data.diff || 0) < 0;
                  return (
                    <TableRow key={phase}>
                      <TableCell>{phase.replace(/_/g, ' ')}</TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                          {renderTrendIcon(data.diff)}
                          {formatValue(Math.abs(data.diff || 0))}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        {data.diff !== null && data.diff !== 0 && (
                          <Chip
                            icon={isFaster ? <CheckCircle /> : <ErrorIcon />}
                            label={isFaster ? 'Brže' : 'Sporije'}
                            color={isFaster ? 'success' : 'error'}
                            size="small"
                          />
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>
    </Container>
  );
};

export default EvaluationComparePage;

// Made with Bob