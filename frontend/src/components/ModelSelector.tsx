/**
 * ModelSelector Component
 * Dropdown for selecting models with dynamic discovery and install capability
 */
import React, { useState, useEffect } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Box,
  Chip,
  Button,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import { Download, CheckCircle, Info } from '@mui/icons-material';
import { ModelInfo, getLLMModels, getEmbeddingModels, getRerankerModels, installModel } from '../api/models';

interface ModelSelectorProps {
  modelType: 'llm' | 'embeddings' | 'rerankers';
  value: string;
  onChange: (value: string) => void;
  label: string;
  disabled?: boolean;
  required?: boolean;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  modelType,
  value,
  onChange,
  label,
  disabled = false,
  required = false
}) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [installing, setInstalling] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadModels();
  }, [modelType]);

  const loadModels = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let data: ModelInfo[];
      switch (modelType) {
        case 'llm':
          data = await getLLMModels();
          break;
        case 'embeddings':
          data = await getEmbeddingModels();
          break;
        case 'rerankers':
          data = await getRerankerModels();
          break;
        default:
          data = [];
      }
      
      setModels(data);
    } catch (err) {
      console.error('Error loading models:', err);
      setError('Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = async (modelName: string) => {
    try {
      setInstalling(modelName);
      await installModel(modelType, modelName);
      // Reload models to update installed status
      await loadModels();
    } catch (err) {
      console.error('Error installing model:', err);
      setError(`Failed to install ${modelName}`);
    } finally {
      setInstalling(null);
    }
  };

  const handleChange = (event: SelectChangeEvent<string>) => {
    onChange(event.target.value);
  };

  if (loading) {
    return (
      <FormControl fullWidth disabled>
        <InputLabel>{label}</InputLabel>
        <Select value="" label={label}>
          <MenuItem value="">
            <Box display="flex" alignItems="center" gap={1}>
              <CircularProgress size={20} />
              <span>Loading models...</span>
            </Box>
          </MenuItem>
        </Select>
      </FormControl>
    );
  }

  if (error) {
    return (
      <FormControl fullWidth error>
        <InputLabel>{label}</InputLabel>
        <Select value="" label={label}>
          <MenuItem value="">
            <Box display="flex" alignItems="center" gap={1}>
              <span>{error}</span>
              <Button size="small" onClick={loadModels}>Retry</Button>
            </Box>
          </MenuItem>
        </Select>
      </FormControl>
    );
  }

  return (
    <FormControl fullWidth disabled={disabled} required={required}>
      <InputLabel>{label}</InputLabel>
      <Select
        value={value}
        onChange={handleChange}
        label={label}
        renderValue={(selected) => {
          const model = models.find(m => m.name === selected);
          return (
            <Box display="flex" alignItems="center" gap={1}>
              <span>{selected}</span>
              {model?.installed && (
                <Chip
                  icon={<CheckCircle />}
                  label="Installed"
                  size="small"
                  color="success"
                  sx={{ height: 20 }}
                />
              )}
            </Box>
          );
        }}
      >
        {models.length === 0 ? (
          <MenuItem value="" disabled>
            No models available
          </MenuItem>
        ) : (
          models.map((model) => (
            <MenuItem key={model.name} value={model.name}>
              <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
                <Box display="flex" alignItems="center" gap={1} flex={1}>
                  <span>{model.name}</span>
                  {model.size && (
                    <Chip label={model.size} size="small" variant="outlined" sx={{ height: 20 }} />
                  )}
                  {model.dimensions && (
                    <Chip label={`${model.dimensions}d`} size="small" variant="outlined" sx={{ height: 20 }} />
                  )}
                  {model.installed && (
                    <Chip
                      icon={<CheckCircle />}
                      label="Installed"
                      size="small"
                      color="success"
                      sx={{ height: 20 }}
                    />
                  )}
                  {model.description && (
                    <Tooltip title={model.description}>
                      <Info fontSize="small" color="action" />
                    </Tooltip>
                  )}
                </Box>
                {!model.installed && modelType === 'llm' && (
                  <Button
                    size="small"
                    startIcon={installing === model.name ? <CircularProgress size={16} /> : <Download />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleInstall(model.name);
                    }}
                    disabled={installing === model.name}
                  >
                    Install
                  </Button>
                )}
              </Box>
            </MenuItem>
          ))
        )}
      </Select>
    </FormControl>
  );
};

export default ModelSelector;

// Made with Bob