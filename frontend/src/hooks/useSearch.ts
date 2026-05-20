/**
 * Search React Query Hooks
 * Custom hooks za pretragu
 */
import { useMutation } from '@tanstack/react-query';
import { searchApi } from '@/api';
import type { SearchRequest, ContextRequest } from '@/types/api';

/**
 * Hook za pretragu dokumenata
 */
export const useSearch = () => {
  return useMutation({
    mutationFn: (request: SearchRequest) => searchApi.search(request),
  });
};

/**
 * Hook za dohvatanje konteksta
 */
export const useGetContext = () => {
  return useMutation({
    mutationFn: (request: ContextRequest) => searchApi.getContext(request),
  });
};

/**
 * Hook za multi-collection pretragu
 */
export const useMultiCollectionSearch = () => {
  return useMutation({
    mutationFn: ({
      query,
      collectionIds,
      topK = 5,
      useReranking = true,
    }: {
      query: string;
      collectionIds: number[];
      topK?: number;
      useReranking?: boolean;
    }) => searchApi.multiCollectionSearch(query, collectionIds, topK, useReranking),
  });
};

/**
 * Hook za pronalaženje sličnih dokumenata
 */
export const useFindSimilar = () => {
  return useMutation({
    mutationFn: ({
      pdfId,
      topK = 5,
      collectionId,
    }: {
      pdfId: number;
      topK?: number;
      collectionId?: number;
    }) => searchApi.findSimilar(pdfId, topK, collectionId),
  });
};

// Made with Bob
