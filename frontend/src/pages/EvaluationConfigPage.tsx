/**
 * EvaluationConfigPage
 * Page for creating evaluations with RAG pipeline configuration
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Save, PlayArrow, Close } from '@mui/icons-material';
import ConfigSection, { ConfigParam } from '../components/ConfigSection';
import { collectionsApi } from '../api/collections';
import type { Collection } from '../types/api';

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
    use_lemmatization: boolean;
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
    system_prompt: string;
  };
}

const EvaluationConfigPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [collectionId, setCollectionId] = useState<number | null>(null);
  const [testExampleIds, setTestExampleIds] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loadingCollections, setLoadingCollections] = useState(true);

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      setLoadingCollections(true);
      const data = await collectionsApi.getAll();
      setCollections(data);
    } catch (err) {
      setError('Greška pri učitavanju kolekcija');
    } finally {
      setLoadingCollections(false);
    }
  };
  
  const [config, setConfig] = useState<RAGConfig>({
    pdf_processing: {
      use_transliteration: true,
      use_spell_check: true
    },
    chunking: {
      strategy: 'semantic',  // Default from backend/config.py
      chunk_size: 500,       // Default from backend/config.py
      chunk_overlap: 50      // Default from backend/config.py
    },
    embeddings: {
      model: 'BAAI/bge-m3',  // Default from backend/config.py
      dimensions: 1024
    },
    vector_storage: {
      collection_name: '',
      distance_metric: 'cosine'
    },
    query_processing: {
      use_transliteration: true,
      use_spell_check: true,
      use_lemmatization: false
    },
    search: {
      top_k: 10,             // Default from backend/config.py
      score_threshold: 0.5
    },
    reranking: {
      enabled: true,         // Default from backend/config.py
      model: 'BAAI/bge-reranker-v2-m3',  // Default from backend/config.py
      top_n: 5               // Default from backend/config.py
    },
    llm: {
      model: 'qwen2.5:14b',  // Default from backend/config.py
      temperature: 0.1,      // Default from backend/config.py
      max_tokens: 2048,
      system_prompt: 'Ti si AI asistent specijalizovan za odgovaranje na pitanja na osnovu dostavljenih dokumenata. Odgovaraj precizno, jasno i na srpskom jeziku.'
    }
  });

  const steps = [
    'Osnovne Informacije',
    'Obrada PDF-a',
    'Segmentacija',
    'Embeddings',
    'Vektorska Baza',
    'Obrada Upita',
    'Pretraga',
    'Rerankiranje',
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
    setActiveStep(prev => {
      const nextStep = Math.min(prev + 1, steps.length - 1);
      
      // Kada prelazimo sa koraka 0 na korak 1, postavi collection_name na evaluation name
      if (prev === 0 && nextStep === 1 && name.trim()) {
        setConfig(prevConfig => ({
          ...prevConfig,
          vector_storage: {
            ...prevConfig.vector_storage,
            collection_name: name.trim()
          }
        }));
      }
      
      return nextStep;
    });
  };

  const handleBack = () => {
    setActiveStep(prev => Math.max(prev - 1, 0));
  };

  const handleSave = async (runImmediately: boolean = false) => {
    try {
      setLoading(true);
      setError(null);

      // Validacija
      if (!name.trim()) {
        setError('Naziv evaluacije je obavezan');
        return;
      }
      if (!collectionId) {
        setError('Kolekcija je obavezna');
        return;
      }

      // Kreiraj evaluaciju sa konfiguracijom
      const { createEvaluationWithConfig, runEvaluationWithConfig } = await import('../api/evaluations');
      
      const evaluation = await createEvaluationWithConfig({
        name: name.trim(),
        description: description?.trim(),
        collection_id: collectionId,
        test_example_ids: testExampleIds.length > 0 ? testExampleIds : [],
        config: config
      });

      // Ako je "Create & Run", pokreni odmah
      if (runImmediately) {
        await runEvaluationWithConfig(evaluation.id, {
          test_example_ids: testExampleIds.length > 0 ? testExampleIds : undefined,
          collection_id: collectionId
        });
      }

      // Navigiraj nazad na evaluations page
      navigate('/evaluations');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Greška pri čuvanju evaluacije');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <Box>
            <TextField
              fullWidth
              label="Naziv Evaluacije"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              sx={{ mb: 2 }}
              helperText="Unesite jedinstveni naziv za ovu evaluaciju"
            />
            <TextField
              fullWidth
              label="Opis"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={3}
              sx={{ mb: 2 }}
              helperText="Opcioni opis evaluacije"
            />
          </Box>
        );

      case 1: // PDF Processing
        return (
          <Box>
            <FormControl fullWidth required sx={{ mb: 3 }}>
              <InputLabel>PDF Kolekcija</InputLabel>
              <Select
                value={collectionId || ''}
                onChange={(e) => setCollectionId(e.target.value as number)}
                label="PDF Kolekcija"
                disabled={loadingCollections}
              >
                {loadingCollections ? (
                  <MenuItem disabled>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Učitavanje...
                  </MenuItem>
                ) : collections.length === 0 ? (
                  <MenuItem disabled>Nema dostupnih kolekcija</MenuItem>
                ) : (
                  collections.map((collection) => (
                    <MenuItem key={collection.id} value={collection.id}>
                      {collection.name} ({collection.pdf_count} PDF-ova)
                    </MenuItem>
                  ))
                )}
              </Select>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                Izaberite kolekciju PDF dokumenata koja će biti corpus znanja za evaluaciju
              </Typography>
            </FormControl>
            <ConfigSection
              title="Obrada PDF-a"
              description="Konfigurišite kako se PDF dokumenti obrađuju"
              params={[
                {
                  name: 'use_transliteration',
                  label: 'Koristi Transliteraciju',
                  type: 'checkbox',
                  value: config.pdf_processing.use_transliteration,
                  tooltip: 'Konvertuj ćirilicu u latinicu'
                },
                {
                  name: 'use_spell_check',
                  label: 'Koristi Proveru Pravopisa',
                  type: 'checkbox',
                  value: config.pdf_processing.use_spell_check,
                  tooltip: 'Omogući proveru pravopisa tokom obrade'
                }
              ]}
              onChange={(param, value) => handleConfigChange('pdf_processing', param, value)}
              collapsible={false}
            />
          </Box>
        );

      case 2: // Chunking
        return (
          <Box>
            <ConfigSection
              title="Chunking Strategy"
              description="Konfigurišite kako se dokumenti dele na chunk-ove"
              params={[
                {
                  name: 'chunk_size',
                  label: 'Veličina Chunk-a',
                  type: 'slider',
                  value: config.chunking.chunk_size,
                  min: 128,
                  max: 2048,
                  step: 128,
                  tooltip: 'Maksimalna veličina svakog chunk-a u karakterima'
                },
                {
                  name: 'chunk_overlap',
                  label: 'Preklapanje Chunk-ova',
                  type: 'slider',
                  value: config.chunking.chunk_overlap,
                  min: 0,
                  max: 200,
                  step: 10,
                  tooltip: 'Broj karaktera koji se preklapaju između chunk-ova'
                }
              ]}
              onChange={(param, value) => handleConfigChange('chunking', param, value)}
              collapsible={false}
            />
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Strategija Segmentacije</InputLabel>
              <Select
                value={config.chunking.strategy}
                onChange={(e) => handleConfigChange('chunking', 'strategy', e.target.value)}
                label="Strategija Segmentacije"
              >
                <MenuItem value="semantic">Semantic - Semantička segmentacija (preporučeno)</MenuItem>
                <MenuItem value="fixed">Fixed - Fiksna veličina</MenuItem>
                <MenuItem value="sentence">Sentence - Po rečenicama</MenuItem>
              </Select>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                Semantic: Deli tekst na osnovu semantičkog značenja (najbolje za RAG)
                <br />
                Fixed: Deli tekst na fiksne delove određene veličine
                <br />
                Sentence: Deli tekst po granicama rečenica
              </Typography>
            </FormControl>
          </Box>
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
                type: 'select',
                value: config.vector_storage.distance_metric,
                options: [
                  { value: 'cosine', label: 'Cosine' },
                  { value: 'euclidean', label: 'Euclidean' },
                  { value: 'dot', label: 'Dot Product' }
                ],
                tooltip: 'Distance metric for vector similarity'
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
              },
              {
                name: 'use_lemmatization',
                label: 'Use Lemmatization',
                type: 'checkbox',
                value: config.query_processing.use_lemmatization,
                tooltip: 'Normalize Serbian words to base form (e.g., "obveznika" → "obveznik")'
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
            title="LLM Konfiguracija"
            description="Konfigurišite podešavanja jezičkog modela"
            params={[
              {
                name: 'model',
                label: 'LLM Model',
                type: 'model',
                modelType: 'llm',
                value: config.llm.model,
                tooltip: 'Jezički model za generisanje odgovora',
                required: true
              },
              {
                name: 'temperature',
                label: 'Temperatura',
                type: 'slider',
                value: config.llm.temperature,
                min: 0,
                max: 2,
                step: 0.1,
                tooltip: 'Temperatura uzorkovanja (veća = kreativniji odgovori)'
              },
              {
                name: 'max_tokens',
                label: 'Maksimalan Broj Tokena',
                type: 'slider',
                value: config.llm.max_tokens,
                min: 256,
                max: 4096,
                step: 256,
                tooltip: 'Maksimalan broj tokena za generisanje'
              },
              {
                name: 'system_prompt',
                label: 'Sistemski Prompt',
                type: 'text',
                value: config.llm.system_prompt,
                multiline: true,
                rows: 4,
                tooltip: 'Uputstvo koje će biti poslato modelu kao sistemska poruka'
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
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h4" gutterBottom>
              Kreiraj Evaluaciju sa Konfiguracijom
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Konfigurišite parametre RAG pipeline-a za ovu evaluaciju
            </Typography>
          </Box>
          <Button
            variant="outlined"
            startIcon={<Close />}
            onClick={() => navigate('/evaluations')}
          >
            Zatvori
          </Button>
        </Box>

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

        <Box sx={{ minHeight: 250 }}>
          {renderStepContent()}
        </Box>

        <Box display="flex" justifyContent="space-between" sx={{ mt: 2 }}>
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
              onClick={() => handleSave(false)}
              disabled={loading}
            >
              Save Draft
            </Button>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={() => handleSave(true)}
                disabled={loading}
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