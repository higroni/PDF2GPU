/**
 * EvaluationComparePage
 * Side-by-side comparison of two evaluations
 */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
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
  AccordionDetails
} from '@mui/material';
import {
  ExpandMore,
  TrendingUp,
  TrendingDown,
  Remove,
  CheckCircle,
  Error as ErrorIcon
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
      // TODO: Implement API call
      // const response = await fetch(`/api/evaluations/compare/${id1}/${id2}`);
      // const data = await response.json();
      // setComparison(data);
      
      // Mock data for now
      setComparison({
        evaluation_1: {
          id: parseInt(id1 || '1'),
          name: 'Evaluation 1',
          status: 'completed',
          collection_id: 1
        },
        evaluation_2: {
          id: parseInt(id2 || '2'),
          name: 'Evaluation 2',
          status: 'completed',
          collection_id: 1
        },
        config_diff: {
          changed: {
            'llm.temperature': { from: 0.7, to: 0.5 },
            'search.top_k': { from: 10, to: 15 }
          },
          added_in_2: {},
          removed_from_1: {}
        },
        metrics_comparison: {
          bleu_score: { eval1: 0.24, eval2: 0.28, diff: 0.04, improvement_pct: 16.67 },
          rouge_l: { eval1: 0.45, eval2: 0.52, diff: 0.07, improvement_pct: 15.56 },
          bert_score: { eval1: 0.89, eval2: 0.91, diff: 0.02, improvement_pct: 2.25 },
          exact_match: { eval1: 4.1, eval2: 6.2, diff: 2.1, improvement_pct: null }
        },
        performance_comparison: {
          query_processing_ms: { eval1: 50, eval2: 45, diff: -5 },
          search_ms: { eval1: 120, eval2: 110, diff: -10 },
          reranking_ms: { eval1: 80, eval2: 85, diff: 5 },
          llm_generation_ms: { eval1: 2000, eval2: 1800, diff: -200 },
          total_latency_ms: { eval1: 2250, eval2: 2040, diff: -210 }
        }
      });
    } catch (err) {
      setError('Failed to load comparison');
    } finally {
      setLoading(false);
    }
  };

  const renderTrendIcon = (diff: number | null) => {
    if (diff === null || diff === 0) return <Remove color="disabled" />;
    if (diff > 0) return <TrendingUp color="success" />;
    return <TrendingDown color="error" />;
  };

  const renderImprovementChip = (improvement: number | null) => {
    if (improvement === null) return null;
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

  const formatValue = (value: number | null): string => {
    if (value === null) return 'N/A';
    if (value < 1) return value.toFixed(3);
    if (value < 100) return value.toFixed(2);
    return value.toFixed(0);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading comparison...
        </Typography>
      </Container>
    );
  }

  if (error || !comparison) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Failed to load comparison'}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Evaluation Comparison
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Comparing configurations, metrics, and performance
      </Typography>

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

      {/* Config Diff */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">Configuration Differences</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {Object.keys(comparison.config_diff.changed).length === 0 &&
           Object.keys(comparison.config_diff.added_in_2).length === 0 &&
           Object.keys(comparison.config_diff.removed_from_1).length === 0 ? (
            <Alert severity="info">No configuration differences</Alert>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Parameter</TableCell>
                    <TableCell>Evaluation 1</TableCell>
                    <TableCell>Evaluation 2</TableCell>
                    <TableCell>Change</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(comparison.config_diff.changed).map(([key, value]: [string, any]) => (
                    <TableRow key={key}>
                      <TableCell><strong>{key}</strong></TableCell>
                      <TableCell>{JSON.stringify(value.from)}</TableCell>
                      <TableCell>{JSON.stringify(value.to)}</TableCell>
                      <TableCell>
                        <Chip label="Changed" color="warning" size="small" />
                      </TableCell>
                    </TableRow>
                  ))}
                  {Object.entries(comparison.config_diff.added_in_2).map(([key, value]) => (
                    <TableRow key={key}>
                      <TableCell><strong>{key}</strong></TableCell>
                      <TableCell>-</TableCell>
                      <TableCell>{JSON.stringify(value)}</TableCell>
                      <TableCell>
                        <Chip label="Added" color="success" size="small" />
                      </TableCell>
                    </TableRow>
                  ))}
                  {Object.entries(comparison.config_diff.removed_from_1).map(([key, value]) => (
                    <TableRow key={key}>
                      <TableCell><strong>{key}</strong></TableCell>
                      <TableCell>{JSON.stringify(value)}</TableCell>
                      <TableCell>-</TableCell>
                      <TableCell>
                        <Chip label="Removed" color="error" size="small" />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Metrics Comparison */}
      <Accordion defaultExpanded sx={{ mt: 2 }}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">Metrics Comparison</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell align="right">Evaluation 1</TableCell>
                  <TableCell align="right">Evaluation 2</TableCell>
                  <TableCell align="right">Difference</TableCell>
                  <TableCell align="right">Improvement</TableCell>
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
          <Typography variant="h6">Performance Comparison</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Evaluation 1
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
                Evaluation 2
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
            Performance Differences
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Phase</TableCell>
                  <TableCell align="right">Difference (ms)</TableCell>
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
                            label={isFaster ? 'Faster' : 'Slower'}
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