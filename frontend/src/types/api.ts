/**
 * API Type Definitions
 * TypeScript tipovi za API modele
 */

// Collection types
export interface Collection {
  id: number;
  name: string;
  description: string | null;
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
  chunking_strategy: 'semantic' | 'fixed' | 'sentence';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  pdf_count?: number;
}

export interface CollectionCreate {
  name: string;
  description?: string;
  embedding_model?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  chunking_strategy?: 'semantic' | 'fixed' | 'sentence';
}

export interface CollectionUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface CollectionStats {
  total_pdfs: number;
  total_chunks: number;
  total_size_bytes: number;
  avg_chunks_per_pdf: number;
}

// PDF types
export interface PDF {
  id: number;
  collection_id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  page_count: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message: string | null;
  chunk_count: number;
  uploaded_at: string;
  processed_at: string | null;
}

export interface PDFUploadResponse {
  pdf: PDF;
  message: string;
}

// Search types
export interface SearchRequest {
  query: string;
  collection_id?: number;
  top_k?: number;
  use_reranking?: boolean;
  search_type?: 'semantic' | 'hybrid';
}

export interface SearchResult {
  chunk_id: string;
  score: number;
  text: string;
  metadata: {
    pdf_id: number;
    filename: string;
    page_number: number;
    chunk_index: number;
  };
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total_results: number;
  search_time: number;
}

export interface ContextRequest {
  query: string;
  collection_id?: number;
  top_k?: number;
  use_reranking?: boolean;
}

export interface ContextResponse {
  context: string;
  sources: SearchResult[];
  query: string;
}

// Error types
export interface APIError {
  detail: string;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Made with Bob
