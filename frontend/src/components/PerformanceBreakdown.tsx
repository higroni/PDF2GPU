/**
 * PerformanceBreakdown Component
 * Visualizes performance metrics breakdown by pipeline phase
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  Tooltip,
  Grid
} from '@mui/material';
import {
  Speed,
  Search,
  FilterList,
  Psychology,
  Timer
} from '@mui/icons-material';

interface PerformanceMetrics {
  avg_query_processing_ms?: number;
  avg_search_ms?: number;
  avg_reranking_ms?: number;
  avg_llm_generation_ms?: number;
  avg_total_latency_ms?: number;
  total_evaluation_time_seconds?: number;
}

interface PerformanceBreakdownProps {
  metrics: PerformanceMetrics;
  title?: string;
  showTotal?: boolean;
}

interface PhaseData {
  name: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  tooltip: string;
}

const PerformanceBreakdown: React.FC<PerformanceBreakdownProps> = ({
  metrics,
  title = 'Performance Breakdown',
  showTotal = true
}) => {
  const phases: PhaseData[] = [
    {
      name: 'Query Processing',
      value: metrics.avg_query_processing_ms || 0,
      icon: <Speed fontSize="small" />,
      color: '#2196f3',
      tooltip: 'Time spent processing and preparing the query'
    },
    {
      name: 'Vector Search',
      value: metrics.avg_search_ms || 0,
      icon: <Search fontSize="small" />,
      color: '#4caf50',
      tooltip: 'Time spent searching the vector database'
    },
    {
      name: 'Reranking',
      value: metrics.avg_reranking_ms || 0,
      icon: <FilterList fontSize="small" />,
      color: '#ff9800',
      tooltip: 'Time spent reranking search results'
    },
    {
      name: 'LLM Generation',
      value: metrics.avg_llm_generation_ms || 0,
      icon: <Psychology fontSize="small" />,
      color: '#f44336',
      tooltip: 'Time spent generating the answer with LLM'
    }
  ];

  const totalLatency = metrics.avg_total_latency_ms || 0;
  const maxValue = Math.max(...phases.map(p => p.value), totalLatency);

  const formatTime = (ms: number): string => {
    if (ms < 1000) {
      return `${ms.toFixed(0)}ms`;
    } else {
      return `${(ms / 1000).toFixed(2)}s`;
    }
  };

  const formatTotalTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    } else {
      const minutes = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${minutes}m ${secs.toFixed(0)}s`;
    }
  };

  const getPercentage = (value: number): number => {
    return maxValue > 0 ? (value / maxValue) * 100 : 0;
  };

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <Timer color="primary" />
        <Typography variant="h6">{title}</Typography>
      </Box>

      <Grid container spacing={2}>
        {phases.map((phase) => (
          <Grid item xs={12} key={phase.name}>
            <Tooltip title={phase.tooltip} arrow placement="top">
              <Box>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={0.5}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Box sx={{ color: phase.color }}>{phase.icon}</Box>
                    <Typography variant="body2" color="text.secondary">
                      {phase.name}
                    </Typography>
                  </Box>
                  <Chip
                    label={formatTime(phase.value)}
                    size="small"
                    sx={{
                      bgcolor: `${phase.color}20`,
                      color: phase.color,
                      fontWeight: 'bold'
                    }}
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={getPercentage(phase.value)}
                  sx={{
                    height: 8,
                    borderRadius: 1,
                    bgcolor: `${phase.color}20`,
                    '& .MuiLinearProgress-bar': {
                      bgcolor: phase.color,
                      borderRadius: 1
                    }
                  }}
                />
              </Box>
            </Tooltip>
          </Grid>
        ))}

        {showTotal && totalLatency > 0 && (
          <Grid item xs={12}>
            <Box sx={{ mt: 1, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body1" fontWeight="bold">
                  Average Total Latency
                </Typography>
                <Chip
                  label={formatTime(totalLatency)}
                  color="primary"
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
            </Box>
          </Grid>
        )}

        {showTotal && metrics.total_evaluation_time_seconds && (
          <Grid item xs={12}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Total Evaluation Time
              </Typography>
              <Chip
                label={formatTotalTime(metrics.total_evaluation_time_seconds)}
                size="small"
                variant="outlined"
              />
            </Box>
          </Grid>
        )}
      </Grid>

      {maxValue === 0 && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            No performance data available
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default PerformanceBreakdown;

// Made with Bob