/**
 * Search API Service
 * Servisi za pretragu i RAG
 */
import { apiClient } from './client';
import type {
  SearchRequest,
  SearchResponse,
  ContextRequest,
  ContextResponse,
  SearchResult,
} from '@/types/api';

const BASE_PATH = '/api/search';

export const searchApi = {
  /**
   * Pretraži dokumente
   */
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>(`${BASE_PATH}/search`, request);
    return response.data;
  },

  /**
   * Dohvati kontekst za query
   */
  getContext: async (request: ContextRequest): Promise<ContextResponse> => {
    const response = await apiClient.post<ContextResponse>(`${BASE_PATH}/context`, request);
    return response.data;
  },

  /**
   * Pretraži kroz više kolekcija
   */
  multiCollectionSearch: async (
    query: string,
    collectionIds: number[],
    topK: number = 5,
    useReranking: boolean = true
  ): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>(`${BASE_PATH}/multi-collection`, {
      query,
      collection_ids: collectionIds,
      top_k: topK,
      use_reranking: useReranking,
    });
    return response.data;
  },

  /**
   * Pronađi slične dokumente
   */
  findSimilar: async (
    pdfId: number,
    topK: number = 5,
    collectionId?: number
  ): Promise<SearchResult[]> => {
    const params: Record<string, string | number> = {
      pdf_id: pdfId,
      top_k: topK,
    };
    if (collectionId) {
      params.collection_id = collectionId;
    }
    const response = await apiClient.get<SearchResult[]>(`${BASE_PATH}/similar`, { params });
    return response.data;
  },
};

export default searchApi;

// Made with Bob
