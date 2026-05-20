/**
 * ConfigSection Component
 * Reusable component for RAG pipeline configuration sections
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControlLabel,
  Checkbox,
  Slider,
  TextField,
  Tooltip,
  IconButton,
  Collapse,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { Info, ExpandMore, ExpandLess } from '@mui/icons-material';
import ModelSelector from './ModelSelector';

export interface ConfigParam {
  name: string;
  label: string;
  type: 'checkbox' | 'slider' | 'text' | 'number' | 'model' | 'select';
  value: any;
  tooltip?: string;
  min?: number;
  max?: number;
  step?: number;
  modelType?: 'llm' | 'embeddings' | 'rerankers';
  options?: Array<{ value: string; label: string }>;
  disabled?: boolean;
  required?: boolean;
  multiline?: boolean;
  rows?: number;
}

interface ConfigSectionProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  params: ConfigParam[];
  onChange: (paramName: string, value: any) => void;
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

const ConfigSection: React.FC<ConfigSectionProps> = ({
  title,
  description,
  icon,
  params,
  onChange,
  collapsible = true,
  defaultExpanded = true
}) => {
  const [expanded, setExpanded] = React.useState(defaultExpanded);

  const handleToggle = () => {
    if (collapsible) {
      setExpanded(!expanded);
    }
  };

  const renderParam = (param: ConfigParam) => {
    const paramBox = (
      <Box key={param.name} sx={{ mb: 2 }}>
        {param.type === 'checkbox' && (
          <FormControlLabel
            control={
              <Checkbox
                checked={param.value}
                onChange={(e) => onChange(param.name, e.target.checked)}
                disabled={param.disabled}
              />
            }
            label={
              <Box display="flex" alignItems="center" gap={0.5}>
                <span>{param.label}</span>
                {param.tooltip && (
                  <Tooltip title={param.tooltip} arrow>
                    <Info fontSize="small" color="action" />
                  </Tooltip>
                )}
              </Box>
            }
          />
        )}

        {param.type === 'slider' && (
          <Box>
            <Box display="flex" alignItems="center" gap={0.5} mb={1}>
              <Typography variant="body2" color="text.secondary">
                {param.label}: {param.value}
              </Typography>
              {param.tooltip && (
                <Tooltip title={param.tooltip} arrow>
                  <Info fontSize="small" color="action" />
                </Tooltip>
              )}
            </Box>
            <Slider
              value={param.value}
              onChange={(_, value) => onChange(param.name, value)}
              min={param.min || 0}
              max={param.max || 100}
              step={param.step || 1}
              disabled={param.disabled}
              valueLabelDisplay="auto"
              marks={[
                { value: param.min || 0, label: String(param.min || 0) },
                { value: param.max || 100, label: String(param.max || 100) }
              ]}
            />
          </Box>
        )}

        {(param.type === 'text' || param.type === 'number') && (
          <TextField
            fullWidth
            label={param.label}
            type={param.type}
            value={param.value}
            onChange={(e) => onChange(param.name, param.type === 'number' ? Number(e.target.value) : e.target.value)}
            disabled={param.disabled}
            required={param.required}
            multiline={param.multiline}
            rows={param.rows}
            InputProps={{
              endAdornment: param.tooltip && (
                <Tooltip title={param.tooltip} arrow>
                  <IconButton size="small" edge="end">
                    <Info fontSize="small" />
                  </IconButton>
                </Tooltip>
              )
            }}
          />
        )}

        {param.type === 'select' && param.options && (
          <FormControl fullWidth>
            <InputLabel>{param.label}</InputLabel>
            <Select
              value={param.value}
              onChange={(e) => onChange(param.name, e.target.value)}
              label={param.label}
              disabled={param.disabled}
              required={param.required}
            >
              {param.options.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {param.tooltip && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                {param.tooltip}
              </Typography>
            )}
          </FormControl>
        )}

        {param.type === 'model' && param.modelType && (
          <ModelSelector
            modelType={param.modelType}
            value={param.value}
            onChange={(value) => onChange(param.name, value)}
            label={param.label}
            disabled={param.disabled}
            required={param.required}
          />
        )}
      </Box>
    );

    return paramBox;
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Box
        display="flex"
        alignItems="center"
        justifyContent="space-between"
        sx={{ cursor: collapsible ? 'pointer' : 'default' }}
        onClick={handleToggle}
      >
        <Box display="flex" alignItems="center" gap={1}>
          {icon}
          <Box>
            <Typography variant="h6">{title}</Typography>
            {description && (
              <Typography variant="body2" color="text.secondary">
                {description}
              </Typography>
            )}
          </Box>
        </Box>
        {collapsible && (
          <IconButton size="small">
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        )}
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ mt: 2 }}>
          {params.map(renderParam)}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default ConfigSection;

// Made with Bob