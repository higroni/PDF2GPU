/**
 * Collections API Service
 * Servisi za rad sa kolekcijama
 */
import { apiClient } from './client';
import type {
  Collection,
  CollectionCreate,
  CollectionUpdate,
  CollectionStats,
} from '@/types/api';

const BASE_PATH = '/api/collections';

export const collectionsApi = {
  /**
   * Dohvati sve kolekcije
   */
  getAll: async (): Promise<Collection[]> => {
    const response = await apiClient.get<Collection[]>(BASE_PATH);
    return response.data;
  },

  /**
   * Dohvati kolekciju po ID-u
   */
  getById: async (id: number): Promise<Collection> => {
    const response = await apiClient.get<Collection>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  /**
   * Kreiraj novu kolekciju
   */
  create: async (data: CollectionCreate): Promise<Collection> => {
    const response = await apiClient.post<Collection>(BASE_PATH, data);
    return response.data;
  },

  /**
   * Ažuriraj kolekciju
   */
  update: async (id: number, data: CollectionUpdate): Promise<Collection> => {
    const response = await apiClient.put<Collection>(`${BASE_PATH}/${id}`, data);
    return response.data;
  },

  /**
   * Obriši kolekciju
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },

  /**
   * Postavi aktivnu kolekciju
   */
  setActive: async (id: number): Promise<Collection> => {
    const response = await apiClient.post<Collection>(`${BASE_PATH}/${id}/set-active`);
    return response.data;
  },

  /**
   * Dohvati aktivnu kolekciju
   */
  getActive: async (): Promise<Collection | null> => {
    const response = await apiClient.get<Collection | null>(`${BASE_PATH}/active`);
    return response.data;
  },

  /**
   * Dohvati statistiku kolekcije
   */
  getStats: async (id: number): Promise<CollectionStats> => {
    const response = await apiClient.get<CollectionStats>(`${BASE_PATH}/${id}/stats`);
    return response.data;
  },

  /**
   * Reprocesiraj sve PDF-ove u kolekciji
   */
  reprocessAll: async (id: number): Promise<{ message: string; count: number }> => {
    const response = await apiClient.post<{ message: string; count: number }>(
      `${BASE_PATH}/${id}/reprocess-all`
    );
    return response.data;
  },
};

export default collectionsApi;

// Made with Bob
