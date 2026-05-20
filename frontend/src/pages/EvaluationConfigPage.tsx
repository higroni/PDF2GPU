/**
 * EvaluationConfigPage
 * Page for creating evaluations with RAG pipeline configuration
 */
import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Alert
} from '@mui/material';
import { Save, PlayArrow } from '@mui/icons-material';
import ConfigSection, { ConfigParam } from '../components/ConfigSection';

interface RAGConfig {
  pdf_processing: {
    use_transliteration: boolean;
    use_spell_check: boolean;
  };
  chunking: {
    strategy: string;
    chunk_size: number;
    chunk_overlap: number;
  };
  embeddings: {
    model: string;
    dimensions: number;
  };
  vector_storage: {
    collection_name: string;
    distance_metric: string;
  };
  query_processing: {
    use_transliteration: boolean;
    use_spell_check: boolean;
  };
  search: {
    top_k: number;
    score_threshold: number;
  };
  reranking: {
    enabled: boolean;
    model: string;
    top_n: number;
  };
  llm: {
    model: string;
    temperature: number;
    max_tokens: number;
  };
}

const EvaluationConfigPage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [collectionId, setCollectionId] = useState<number | null>(null);
  const [testExampleIds, setTestExampleIds] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const [config, setConfig] = useState<RAGConfig>({
    pdf_processing: {
      use_transliteration: true,
      use_spell_check: false
    },
    chunking: {
      strategy: 'semantic',
      chunk_size: 512,
      chunk_overlap: 50
    },
    embeddings: {
      model: 'BAAI/bge-m3',
      dimensions: 1024
    },
    vector_storage: {
      collection_name: '',
      distance_metric: 'cosine'
    },
    query_processing: {
      use_transliteration: true,
      use_spell_check: false
    },
    search: {
      top_k: 10,
      score_threshold: 0.5
    },
    reranking: {
      enabled: true,
      model: 'BAAI/bge-reranker-v2-m3',
      top_n: 5
    },
    llm: {
      model: 'llama3.2:latest',
      temperature: 0.7,
      max_tokens: 2048
    }
  });

  const steps = [
    'Basic Info',
    'PDF Processing',
    'Chunking',
    'Embeddings',
    'Vector Storage',
    'Query Processing',
    'Search',
    'Reranking',
    'LLM'
  ];

  const handleConfigChange = (section: keyof RAGConfig, param: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [param]: value
      }
    }));
  };

  const handleNext = () => {
    setActiveStep(prev => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setActiveStep(prev => Math.max(prev - 1, 0));
  };

  const handleSave = async () => {
    try {
      // TODO: Implement API call to create evaluation with config
      console.log('Saving evaluation:', { name, description, collectionId, testExampleIds, config });
    } catch (err) {
      setError('Failed to save evaluation');
    }
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <Box>
            <TextField
              fullWidth
              label="Evaluation Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />
            {/* TODO: Add Collection selector */}
            {/* TODO: Add Test Examples selector */}
          </Box>
        );

      case 1: // PDF Processing
        return (
          <ConfigSection
            title="PDF Processing"
            description="Configure how PDFs are processed"
            params={[
              {
                name: 'use_transliteration',
                label: 'Use Transliteration',
                type: 'checkbox',
                value: config.pdf_processing.use_transliteration,
                tooltip: 'Convert Cyrillic to Latin characters'
              },
              {
                name: 'use_spell_check',
                label: 'Use Spell Check',
                type: 'checkbox',
                value: config.pdf_processing.use_spell_check,
                tooltip: 'Enable spell checking during processing'
              }
            ]}
            onChange={(param, value) => handleConfigChange('pdf_processing', param, value)}
            collapsible={false}
          />
        );

      case 2: // Chunking
        return (
          <ConfigSection
            title="Chunking Strategy"
            description="Configure how documents are split into chunks"
            params={[
              {
                name: 'strategy',
                label: 'Strategy',
                type: 'text',
                value: config.chunking.strategy,
                tooltip: 'Chunking strategy (semantic, fixed, etc.)'
              },
              {
                name: 'chunk_size',
                label: 'Chunk Size',
                type: 'slider',
                value: config.chunking.chunk_size,
                min: 128,
                max: 2048,
                step: 128,
                tooltip: 'Maximum size of each chunk in tokens'
              },
              {
                name: 'chunk_overlap',
                label: 'Chunk Overlap',
                type: 'slider',
                value: config.chunking.chunk_overlap,
                min: 0,
                max: 200,
                step: 10,
                tooltip: 'Number of overlapping tokens between chunks'
              }
            ]}
            onChange={(param, value) => handleConfigChange('chunking', param, value)}
            collapsible={false}
          />
        );

      case 3: // Embeddings
        return (
          <ConfigSection
            title="Embeddings"
            description="Configure embedding model"
            params={[
              {
                name: 'model',
                label: 'Embedding Model',
                type: 'model',
                modelType: 'embeddings',
                value: config.embeddings.model,
                tooltip: 'Model used for generating embeddings',
                required: true
              },
              {
                name: 'dimensions',
                label: 'Dimensions',
                type: 'number',
                value: config.embeddings.dimensions,
                tooltip: 'Embedding vector dimensions'
              }
            ]}
            onChange={(param, value) => handleConfigChange('embeddings', param, value)}
            collapsible={false}
          />
        );

      case 4: // Vector Storage
        return (
          <ConfigSection
            title="Vector Storage"
            description="Configure vector database settings"
            params={[
              {
                name: 'collection_name',
                label: 'Collection Name',
                type: 'text',
                value: config.vector_storage.collection_name,
                tooltip: 'Name of the Qdrant collection',
                required: true
              },
              {
                name: 'distance_metric',
                label: 'Distance Metric',
                type: 'text',
                value: config.vector_storage.distance_metric,
                tooltip: 'Distance metric (cosine, euclidean, dot)'
              }
            ]}
            onChange={(param, value) => handleConfigChange('vector_storage', param, value)}
            collapsible={false}
          />
        );

      case 5: // Query Processing
        return (
          <ConfigSection
            title="Query Processing"
            description="Configure how queries are processed"
            params={[
              {
                name: 'use_transliteration',
                label: 'Use Transliteration',
                type: 'checkbox',
                value: config.query_processing.use_transliteration,
                tooltip: 'Convert Cyrillic to Latin in queries'
              },
              {
                name: 'use_spell_check',
                label: 'Use Spell Check',
                type: 'checkbox',
                value: config.query_processing.use_spell_check,
                tooltip: 'Enable spell checking for queries'
              }
            ]}
            onChange={(param, value) => handleConfigChange('query_processing', param, value)}
            collapsible={false}
          />
        );

      case 6: // Search
        return (
          <ConfigSection
            title="Search Configuration"
            description="Configure vector search parameters"
            params={[
              {
                name: 'top_k',
                label: 'Top K Results',
                type: 'slider',
                value: config.search.top_k,
                min: 1,
                max: 50,
                step: 1,
                tooltip: 'Number of top results to retrieve'
              },
              {
                name: 'score_threshold',
                label: 'Score Threshold',
                type: 'slider',
                value: config.search.score_threshold,
                min: 0,
                max: 1,
                step: 0.05,
                tooltip: 'Minimum similarity score threshold'
              }
            ]}
            onChange={(param, value) => handleConfigChange('search', param, value)}
            collapsible={false}
          />
        );

      case 7: // Reranking
        return (
          <ConfigSection
            title="Reranking"
            description="Configure result reranking"
            params={[
              {
                name: 'enabled',
                label: 'Enable Reranking',
                type: 'checkbox',
                value: config.reranking.enabled,
                tooltip: 'Enable reranking of search results'
              },
              {
                name: 'model',
                label: 'Reranker Model',
                type: 'model',
                modelType: 'rerankers',
                value: config.reranking.model,
                tooltip: 'Model used for reranking',
                disabled: !config.reranking.enabled
              },
              {
                name: 'top_n',
                label: 'Top N After Reranking',
                type: 'slider',
                value: config.reranking.top_n,
                min: 1,
                max: 20,
                step: 1,
                tooltip: 'Number of results to keep after reranking',
                disabled: !config.reranking.enabled
              }
            ]}
            onChange={(param, value) => handleConfigChange('reranking', param, value)}
            collapsible={false}
          />
        );

      case 8: // LLM
        return (
          <ConfigSection
            title="LLM Configuration"
            description="Configure language model settings"
            params={[
              {
                name: 'model',
                label: 'LLM Model',
                type: 'model',
                modelType: 'llm',
                value: config.llm.model,
                tooltip: 'Language model for answer generation',
                required: true
              },
              {
                name: 'temperature',
                label: 'Temperature',
                type: 'slider',
                value: config.llm.temperature,
                min: 0,
                max: 2,
                step: 0.1,
                tooltip: 'Sampling temperature (higher = more creative)'
              },
              {
                name: 'max_tokens',
                label: 'Max Tokens',
                type: 'slider',
                value: config.llm.max_tokens,
                min: 256,
                max: 4096,
                step: 256,
                tooltip: 'Maximum number of tokens to generate'
              }
            ]}
            onChange={(param, value) => handleConfigChange('llm', param, value)}
            collapsible={false}
          />
        );

      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Create Evaluation with Configuration
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Configure RAG pipeline parameters for this evaluation
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ minHeight: 400 }}>
          {renderStepContent()}
        </Box>

        <Box display="flex" justifyContent="space-between" sx={{ mt: 3 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<Save />}
              onClick={handleSave}
            >
              Save Draft
            </Button>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={handleSave}
              >
                Create & Run
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default EvaluationConfigPage;

// Made with Bob