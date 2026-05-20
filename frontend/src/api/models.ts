/**
 * Models API Client
 * API calls for model discovery and management
 */
import apiClient from './client';

export interface ModelInfo {
  name: string;
  size?: string;
  modified?: string;
  source?: string;
  dimensions?: number;
  description?: string;
  installed?: boolean;
}

export interface InstallResponse {
  status: string;
  message: string;
  output?: string;
  instructions?: string;
}

/**
 * Get available LLM models from Ollama
 */
export const getLLMModels = async (): Promise<ModelInfo[]> => {
  const response = await apiClient.get<ModelInfo[]>('/models/llm');
  return response.data;
};

/**
 * Get available embedding models
 */
export const getEmbeddingModels = async (): Promise<ModelInfo[]> => {
  const response = await apiClient.get<ModelInfo[]>('/models/embeddings');
  return response.data;
};

/**
 * Get available reranker models
 */
export const getRerankerModels = async (): Promise<ModelInfo[]> => {
  const response = await apiClient.get<ModelInfo[]>('/models/rerankers');
  return response.data;
};

/**
 * Install a model
 */
export const installModel = async (
  modelType: 'llm' | 'embeddings' | 'rerankers',
  modelName: string
): Promise<InstallResponse> => {
  const response = await apiClient.post<InstallResponse>(
    `/models/install/${modelType}/${encodeURIComponent(modelName)}`
  );
  return response.data;
};

// Made with Bob