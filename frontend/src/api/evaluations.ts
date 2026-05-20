/**
 * Evaluations API Client
 */
import { apiClient } from './client';

export interface Evaluation {
  id: number;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  total_examples?: number;
  completed_examples?: number;
  avg_bleu_score?: number;
  avg_rouge_1?: number;
  avg_rouge_2?: number;
  avg_rouge_l?: number;
  avg_bert_score?: number;
  exact_match_percentage?: number;
}

export interface EvaluationCreate {
  name: string;
  description?: string;
}

export interface EvaluationRun {
  test_example_ids?: number[];
  collection_id?: number;
}

export interface TestExampleResult {
  id: number;
  evaluation_id: number;
  test_example_id: number;
  generated_answer: string;
  bleu_score?: number;
  rouge_1?: number;
  rouge_2?: number;
  rouge_l?: number;
  bert_score_precision?: number;
  bert_score_recall?: number;
  bert_score_f1?: number;
  exact_match: boolean;
  word_overlap?: number;
  created_at: string;
}

export interface MetricStats {
  avg: number;
  min: number;
  max: number;
  count: number;
}

export interface EvaluationStatistics {
  evaluation_id: number;
  name: string;
  status: string;
  total_examples: number;
  started_at?: string;
  completed_at?: string;
  metrics: {
    bleu_score: MetricStats;
    rouge_1: MetricStats;
    rouge_2: MetricStats;
    rouge_l: MetricStats;
    bert_score_f1: MetricStats;
    exact_match: {
      count: number;
      percentage: number;
    };
    word_overlap: MetricStats;
  };
}

/**
 * Kreira novu evaluaciju
 */
export const createEvaluation = async (
  data: EvaluationCreate
): Promise<Evaluation> => {
  const response = await apiClient.post('/api/evaluations', data);
  return response.data;
};

/**
 * Pokreće evaluaciju
 */
export const runEvaluation = async (
  id: number,
  data: EvaluationRun
): Promise<Evaluation> => {
  const response = await apiClient.post(`/api/evaluations/${id}/run`, data);
  return response.data;
};

/**
 * Dohvata sve evaluacije
 */
export const getEvaluations = async (
  skip: number = 0,
  limit: number = 100,
  status?: string
): Promise<Evaluation[]> => {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  
  if (status) {
    params.append('status', status);
  }
  
  const response = await apiClient.get(`/api/evaluations?${params}`);
  return response.data;
};

/**
 * Dohvata evaluaciju po ID-ju
 */
export const getEvaluation = async (id: number): Promise<Evaluation> => {
  const response = await apiClient.get(`/api/evaluations/${id}`);
  return response.data;
};

/**
 * Dohvata rezultate evaluacije
 */
export const getEvaluationResults = async (
  id: number,
  skip: number = 0,
  limit: number = 100
): Promise<TestExampleResult[]> => {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  
  const response = await apiClient.get(`/api/evaluations/${id}/results?${params}`);
  return response.data;
};

/**
 * Dohvata statistike evaluacije
 */
export const getEvaluationStatistics = async (
  id: number
): Promise<EvaluationStatistics> => {
  const response = await apiClient.get(`/api/evaluations/${id}/statistics`);
  return response.data;
};

/**
 * Briše evaluaciju
 */
export const deleteEvaluation = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/evaluations/${id}`);
};

/**
 * Polling funkcija za praćenje statusa evaluacije
 */
export const pollEvaluationStatus = async (
  id: number,
  onUpdate: (evaluation: Evaluation) => void,
  interval: number = 2000
): Promise<() => void> => {
  let isPolling = true;
  
  const poll = async () => {
    while (isPolling) {
      try {
        const evaluation = await getEvaluation(id);
        onUpdate(evaluation);
        
        // Zaustavi polling ako je evaluacija završena
        if (evaluation.status === 'completed' || evaluation.status === 'failed') {
          isPolling = false;
          break;
        }
        
        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        console.error('Error polling evaluation status:', error);
        isPolling = false;
        break;
      }
    }
  };
  
  poll();
  
  // Vrati funkciju za zaustavljanje polling-a
  return () => {
    isPolling = false;
  };
};

/**
 * Kreira evaluaciju sa RAG konfiguracijom
 */
export interface EvaluationWithConfig {
  name: string;
  description?: string;
  collection_id: number;
  test_example_ids?: number[];
  config_snapshot: Record<string, any>;
}

export const createEvaluationWithConfig = async (
  data: EvaluationWithConfig
): Promise<Evaluation> => {
  const response = await apiClient.post('/api/evaluations/with-config', data);
  return response.data;
};

/**
 * Pokreće evaluaciju sa RAG konfiguracijom i timing tracking-om
 */
export const runEvaluationWithConfig = async (
  id: number,
  data: EvaluationRun
): Promise<Evaluation> => {
  const response = await apiClient.post(`/api/evaluations/${id}/run-with-config`, data);
  return response.data;
};

// Made with Bob
