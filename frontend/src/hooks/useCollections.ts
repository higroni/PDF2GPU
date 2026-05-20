/**
 * Collections React Query Hooks
 * Custom hooks za rad sa kolekcijama
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { collectionsApi } from '@/api';
import type { CollectionCreate, CollectionUpdate } from '@/types/api';

const QUERY_KEY = 'collections';

/**
 * Hook za dohvatanje svih kolekcija
 */
export const useCollections = () => {
  return useQuery({
    queryKey: [QUERY_KEY],
    queryFn: collectionsApi.getAll,
  });
};

/**
 * Hook za dohvatanje jedne kolekcije
 */
export const useCollection = (id: number) => {
  return useQuery({
    queryKey: [QUERY_KEY, id],
    queryFn: () => collectionsApi.getById(id),
    enabled: !!id,
  });
};

/**
 * Hook za dohvatanje aktivne kolekcije
 */
export const useActiveCollection = () => {
  return useQuery({
    queryKey: [QUERY_KEY, 'active'],
    queryFn: collectionsApi.getActive,
  });
};

/**
 * Hook za dohvatanje statistike kolekcije
 */
export const useCollectionStats = (id: number) => {
  return useQuery({
    queryKey: [QUERY_KEY, id, 'stats'],
    queryFn: () => collectionsApi.getStats(id),
    enabled: !!id,
  });
};

/**
 * Hook za kreiranje kolekcije
 */
export const useCreateCollection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CollectionCreate) => collectionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
};

/**
 * Hook za ažuriranje kolekcije
 */
export const useUpdateCollection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CollectionUpdate }) =>
      collectionsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, variables.id] });
    },
  });
};

/**
 * Hook za brisanje kolekcije
 */
export const useDeleteCollection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => collectionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
};

/**
 * Hook za postavljanje aktivne kolekcije
 */
export const useSetActiveCollection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => collectionsApi.setActive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, 'active'] });
    },
  });
};

/**
 * Hook za reprocesiranje svih PDF-ova u kolekciji
 */
export const useReprocessAllPDFs = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => collectionsApi.reprocessAll(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: ['pdfs'] });
    },
  });
};

// Made with Bob
