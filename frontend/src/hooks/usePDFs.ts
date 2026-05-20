/**
 * PDFs React Query Hooks
 * Custom hooks za rad sa PDF dokumentima
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pdfsApi } from '@/api';

const QUERY_KEY = 'pdfs';

/**
 * Hook za dohvatanje svih PDF-ova
 */
export const usePDFs = (collectionId?: number) => {
  return useQuery({
    queryKey: [QUERY_KEY, { collectionId }],
    queryFn: () => pdfsApi.getAll(collectionId),
  });
};

/**
 * Hook za dohvatanje jednog PDF-a
 */
export const usePDF = (id: number) => {
  return useQuery({
    queryKey: [QUERY_KEY, id],
    queryFn: () => pdfsApi.getById(id),
    enabled: !!id,
  });
};

/**
 * Hook za dohvatanje PDF-ova po kolekciji
 */
export const usePDFsByCollection = (collectionId: number) => {
  return useQuery({
    queryKey: [QUERY_KEY, 'collection', collectionId],
    queryFn: () => pdfsApi.getByCollection(collectionId),
    enabled: !!collectionId,
  });
};

/**
 * Hook za upload PDF-a
 */
export const useUploadPDF = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      file,
      collectionId,
      onProgress,
    }: {
      file: File;
      collectionId: number;
      onProgress?: (progress: number) => void;
    }) => pdfsApi.upload(file, collectionId, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['collections'] });
    },
  });
};

/**
 * Hook za brisanje PDF-a
 */
export const useDeletePDF = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => pdfsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['collections'] });
    },
  });
};

/**
 * Hook za reprocesiranje PDF-a
 */
export const useReprocessPDF = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => pdfsApi.reprocess(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, data.id] });
    },
  });
};

// Made with Bob
