/**
 * Test Examples API Client
 */
import { apiClient } from './client';

export interface TestExample {
  id: number;
  question: string;
  expected_answer: string;
  category?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  collection_id: number;
}

export interface TestExampleCreate {
  question: string;
  expected_answer: string;
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  collection_id: number;
}

export interface TestExampleUpdate {
  question?: string;
  expected_answer?: string;
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  is_active?: boolean;
}

export interface TestExampleBulkImport {
  examples: Array<{
    question: string;
    expected_answer: string;
    category?: string;
    difficulty?: 'easy' | 'medium' | 'hard';
  }>;
  collection_id: number;
}

export interface TestExampleStatistics {
  total: number;
  by_difficulty: {
    easy: number;
    medium: number;
    hard: number;
  };
  by_category: Record<string, number>;
  active: number;
  inactive: number;
}

/**
 * Dohvata sve test primere
 */
export const getTestExamples = async (
  collectionId?: number,
  skip: number = 0,
  limit: number = 100
): Promise<TestExample[]> => {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  
  if (collectionId) {
    params.append('collection_id', collectionId.toString());
  }
  
  const response = await apiClient.get(`/api/test-examples?${params}`);
  return response.data;
};

/**
 * Dohvata test primer po ID-ju
 */
export const getTestExample = async (id: number): Promise<TestExample> => {
  const response = await apiClient.get(`/api/test-examples/${id}`);
  return response.data;
};

/**
 * Kreira novi test primer
 */
export const createTestExample = async (
  data: TestExampleCreate
): Promise<TestExample> => {
  const response = await apiClient.post('/api/test-examples', data);
  return response.data;
};

/**
 * Ažurira test primer
 */
export const updateTestExample = async (
  id: number,
  data: TestExampleUpdate
): Promise<TestExample> => {
  const response = await apiClient.put(`/api/test-examples/${id}`, data);
  return response.data;
};

/**
 * Briše test primer
 */
export const deleteTestExample = async (id: number): Promise<void> => {
  await apiClient.delete(`/api/test-examples/${id}`);
};

/**
 * Bulk import test primera
 */
export const bulkImportTestExamples = async (
  data: TestExampleBulkImport
): Promise<{ created: number; failed: number }> => {
  const response = await apiClient.post('/api/test-examples/bulk-import', data);
  return response.data;
};

/**
 * Bulk export test primera
 */
export const bulkExportTestExamples = async (
  collectionId?: number
): Promise<Blob> => {
  const params = collectionId
    ? `?collection_id=${collectionId}`
    : '';
  
  const response = await apiClient.get(`/api/test-examples/export/json${params}`, {
    responseType: 'blob',
  });
  return response.data;
};

/**
 * Dohvata statistike test primera
 */
export const getTestExampleStatistics = async (
  collectionId?: number
): Promise<TestExampleStatistics> => {
  const params = collectionId
    ? `?collection_id=${collectionId}`
    : '';
  
  const response = await apiClient.get(`/api/test-examples/stats/summary${params}`);
  return response.data;
};

/**
 * Aktivira/deaktivira test primer
 */
export const toggleTestExampleActive = async (
  id: number,
  isActive: boolean
): Promise<TestExample> => {
  return updateTestExample(id, { is_active: isActive });
};

// Made with Bob
