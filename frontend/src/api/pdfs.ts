/**
 * PDFs API Service
 * Servisi za rad sa PDF dokumentima
 */
import { apiClient } from './client';
import type { PDF, PDFUploadResponse } from '@/types/api';

const BASE_PATH = '/api/pdfs';

export const pdfsApi = {
  /**
   * Dohvati sve PDF-ove
   */
  getAll: async (collectionId?: number): Promise<PDF[]> => {
    const params = collectionId ? { collection_id: collectionId } : {};
    const response = await apiClient.get<PDF[]>(BASE_PATH, { params });
    return response.data;
  },

  /**
   * Dohvati PDF po ID-u
   */
  getById: async (id: number): Promise<PDF> => {
    const response = await apiClient.get<PDF>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  /**
   * Upload PDF fajla
   */
  upload: async (
    file: File,
    collectionId: number,
    onProgress?: (progress: number) => void
  ): Promise<PDFUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('collection_id', collectionId.toString());

    const response = await apiClient.post<PDFUploadResponse>(
      `${BASE_PATH}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      }
    );
    return response.data;
  },

  /**
   * Obriši PDF
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },

  /**
   * Reprocesiraj PDF
   */
  reprocess: async (id: number): Promise<PDF> => {
    const response = await apiClient.post<PDF>(`${BASE_PATH}/${id}/reprocess`);
    return response.data;
  },

  /**
   * Dohvati PDF-ove po kolekciji
   */
  getByCollection: async (collectionId: number): Promise<PDF[]> => {
    const response = await apiClient.get<PDF[]>(`${BASE_PATH}/collection/${collectionId}`);
    return response.data;
  },
};

export default pdfsApi;

// Made with Bob
