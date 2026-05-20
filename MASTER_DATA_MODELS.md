# 📊 MASTER DATA MODELS - Katalog Svih Data Modela

> **🔒 VAŽNO**: Ovaj fajl je master referenca za sve data modele u projektu. Ažurira se tokom razvoja. Koristi ga za konzistentnost imenovanja i strukture.

**Poslednje ažuriranje**: 2026-05-20  
**Verzija**: 1.0

---

## 📋 Sadržaj

1. [SQLite Database Models](#sqlite-database-models)
2. [Pydantic API Models](#pydantic-api-models)
3. [Qdrant Vector Models](#qdrant-vector-models)
4. [Configuration Models](#configuration-models)

---

## 1. SQLite Database Models

### 1.1 PDF Model
**Tabela**: `pdfs`  
**Fajl**: `backend/models/pdf.py`  
**Opis**: Čuva metadata o uploadovanim PDF fajlovima

```python
class PDF(Base):
    __tablename__ = "pdfs"
    
    id: int                          # Primary key
    filename: str                    # Originalni naziv fajla
    filepath: str                    # Putanja na disku
    size_bytes: int                  # Veličina fajla
    pages: int                       # Broj stranica
    uploaded_at: datetime            # Vreme upload-a
    processed_at: datetime | None    # Vreme procesiranja
    chunks_count: int                # Broj chunk-ova
    collection_name: str             # Qdrant kolekcija
    category: str | None             # Kategorija (zakoni, procedure, etc.)
    language: str                    # Jezik (sr, en)
    status: str                      # pending, processing, completed, failed
    error_message: str | None        # Poruka greške ako failed
```

### 1.2 TestExample Model
**Tabela**: `test_examples`  
**Fajl**: `backend/models/test_example.py`  
**Opis**: Test pitanja i očekivani odgovori za evaluaciju

```python
class TestExample(Base):
    __tablename__ = "test_examples"
    
    id: int                          # Primary key
    question: str                    # Test pitanje
    expected_answer: str             # Očekivani odgovor
    category: str | None             # Kategorija (porezi, zakoni, etc.)
    difficulty: str                  # easy, medium, hard
    created_at: datetime             # Vreme kreiranja
    updated_at: datetime             # Vreme ažuriranja
    collection_name: str             # Vezana kolekcija
```

### 1.3 ChatMessage Model
**Tabela**: `chat_messages`  
**Fajl**: `backend/models/chat.py`  
**Opis**: Istorija chat poruka

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id: int                          # Primary key
    session_id: str                  # ID sesije
    role: str                        # user, assistant, system
    content: str                     # Sadržaj poruke
    timestamp: datetime              # Vreme slanja
    model_name: str | None           # LLM model korišćen
    collection_name: str             # Aktivna kolekcija
    retrieved_chunks: int | None     # Broj retrieved chunks
    response_time_ms: int | None     # Vreme odgovora
```

### 1.4 Feedback Model
**Tabela**: `feedback`  
**Fajl**: `backend/models/feedback.py`  
**Opis**: Feedback korisnika na odgovore

```python
class Feedback(Base):
    __tablename__ = "feedback"
    
    id: int                          # Primary key
    message_id: int                  # FK -> chat_messages.id
    accuracy_rating: int             # 1-5 (tačnost odgovora)
    language_rating: int             # 1-5 (kvalitet jezika)
    chunk_relevance_rating: int      # 1-5 (relevantnost chunk-ova)
    comment: str | None              # Komentar korisnika
    created_at: datetime             # Vreme feedback-a
```

### 1.5 Evaluation Model
**Tabela**: `evaluations`  
**Fajl**: `backend/models/evaluation.py`  
**Opis**: Rezultati evaluacija sistema

```python
class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id: int                          # Primary key
    version_name: str                # Naziv verzije (phase1, phase2, etc.)
    collection_name: str             # Testirana kolekcija
    timestamp: datetime              # Vreme evaluacije
    duration_seconds: int            # Trajanje evaluacije
    total_questions: int             # Ukupno pitanja
    correct_answers: int             # Tačni odgovori
    accuracy: float                  # Tačnost (0-1)
    precision: float                 # Preciznost (0-1)
    recall: float                    # Recall (0-1)
    f1_score: float                  # F1 score (0-1)
    avg_response_time_ms: int        # Prosečno vreme odgovora
    gpu_utilization_avg: float       # Prosečna GPU iskorišćenost
    config_snapshot: str             # JSON snapshot konfiguracije
```

### 1.6 Collection Model
**Tabela**: `collections`  
**Fajl**: `backend/models/collection.py`  
**Opis**: Metadata o Qdrant kolekcijama

```python
class Collection(Base):
    __tablename__ = "collections"
    
    id: int                          # Primary key
    name: str                        # Naziv kolekcije (unique)
    description: str | None          # Opis kolekcije
    created_at: datetime             # Vreme kreiranja
    updated_at: datetime             # Vreme ažuriranja
    is_active: bool                  # Da li je aktivna
    vectors_count: int               # Broj vektora
    pdfs_count: int                  # Broj PDF-ova
```

### 1.7 Settings Model
**Tabela**: `settings`  
**Fajl**: `backend/models/settings.py`  
**Opis**: Sistemske postavke

```python
class Settings(Base):
    __tablename__ = "settings"
    
    id: int                          # Primary key
    key: str                         # Ključ postavke (unique)
    value: str                       # Vrednost (JSON string)
    category: str                    # rag, llm, system
    description: str | None          # Opis postavke
    updated_at: datetime             # Vreme ažuriranja
```

### 1.8 SessionLog Model
**Tabela**: `session_logs`  
**Fajl**: `backend/models/session_log.py`  
**Opis**: Logovi sesija za analizu

```python
class SessionLog(Base):
    __tablename__ = "session_logs"
    
    id: int                          # Primary key
    session_id: str                  # ID sesije
    event_type: str                  # query, response, error, etc.
    event_data: str                  # JSON data
    timestamp: datetime              # Vreme događaja
    collection_name: str             # Aktivna kolekcija
```

---

## 2. Pydantic API Models

### 2.1 PDF API Models
**Fajl**: `backend/api/schemas/pdf.py`

```python
class PDFUploadRequest(BaseModel):
    """Request za upload PDF-a"""
    category: str | None = None
    collection_name: str

class PDFUploadResponse(BaseModel):
    """Response nakon upload-a"""
    success: bool
    pdf_id: int
    filename: str
    message: str

class PDFListItem(BaseModel):
    """Item u listi PDF-ova"""
    id: int
    filename: str
    size_bytes: int
    pages: int
    uploaded_at: datetime
    status: str
    chunks_count: int
    collection_name: str

class PDFListResponse(BaseModel):
    """Lista svih PDF-ova"""
    pdfs: list[PDFListItem]
    total: int

class PDFDeleteResponse(BaseModel):
    """Response nakon brisanja"""
    success: bool
    message: str
```

### 2.2 Training API Models
**Fajl**: `backend/api/schemas/training.py`

```python
class TrainingStartRequest(BaseModel):
    """Request za pokretanje treninga"""
    collection_name: str
    force_reprocess: bool = False

class TrainingStartResponse(BaseModel):
    """Response nakon pokretanja"""
    success: bool
    job_id: str
    message: str

class TrainingStatusResponse(BaseModel):
    """Status treninga"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0-100
    current_step: str
    total_steps: int
    completed_steps: int
    estimated_time_remaining_seconds: int | None
    error_message: str | None

class TrainingProgressUpdate(BaseModel):
    """WebSocket update za progress"""
    job_id: str
    progress: float
    current_step: str
    message: str
```

### 2.3 Chat API Models
**Fajl**: `backend/api/schemas/chat.py`

```python
class ChatMessageRequest(BaseModel):
    """Request za chat poruku"""
    message: str
    session_id: str | None = None
    model_name: str | None = None
    collection_name: str

class ChatMessageResponse(BaseModel):
    """Response sa odgovorom"""
    success: bool
    message_id: int
    response: str
    session_id: str
    retrieved_chunks: int
    response_time_ms: int
    sources: list[dict]  # Lista izvora sa metadata

class ChatHistoryResponse(BaseModel):
    """Istorija chat-a"""
    messages: list[ChatMessage]
    session_id: str
    total: int
```

### 2.4 Test Examples API Models
**Fajl**: `backend/api/schemas/test_example.py`

```python
class TestExampleCreate(BaseModel):
    """Kreiranje test primera"""
    question: str
    expected_answer: str
    category: str | None = None
    difficulty: str = "medium"
    collection_name: str

class TestExampleUpdate(BaseModel):
    """Ažuriranje test primera"""
    question: str | None = None
    expected_answer: str | None = None
    category: str | None = None
    difficulty: str | None = None

class TestExampleResponse(BaseModel):
    """Response sa test primerom"""
    id: int
    question: str
    expected_answer: str
    category: str | None
    difficulty: str
    created_at: datetime
    collection_name: str

class TestExampleListResponse(BaseModel):
    """Lista test primera"""
    examples: list[TestExampleResponse]
    total: int

class TestExampleImportRequest(BaseModel):
    """Import test primera iz JSON-a"""
    examples: list[TestExampleCreate]
    collection_name: str
```

### 2.5 Evaluation API Models
**Fajl**: `backend/api/schemas/evaluation.py`

```python
class EvaluationStartRequest(BaseModel):
    """Pokretanje evaluacije"""
    version_name: str
    collection_name: str
    test_example_ids: list[int] | None = None  # Ako None, koristi sve

class EvaluationStartResponse(BaseModel):
    """Response nakon pokretanja"""
    success: bool
    job_id: str
    message: str

class EvaluationResultResponse(BaseModel):
    """Rezultati evaluacije"""
    id: int
    version_name: str
    collection_name: str
    timestamp: datetime
    duration_seconds: int
    total_questions: int
    correct_answers: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    avg_response_time_ms: int
    gpu_utilization_avg: float
    config_snapshot: dict

class EvaluationListResponse(BaseModel):
    """Lista svih evaluacija"""
    evaluations: list[EvaluationResultResponse]
    total: int

class EvaluationComparisonRequest(BaseModel):
    """Poređenje dve evaluacije"""
    evaluation_id_1: int
    evaluation_id_2: int

class EvaluationComparisonResponse(BaseModel):
    """Rezultat poređenja"""
    evaluation_1: EvaluationResultResponse
    evaluation_2: EvaluationResultResponse
    improvements: dict  # accuracy_delta, speed_delta, etc.
```

### 2.6 Collection API Models
**Fajl**: `backend/api/schemas/collection.py`

```python
class CollectionCreateRequest(BaseModel):
    """Kreiranje nove kolekcije"""
    name: str
    description: str | None = None

class CollectionCreateResponse(BaseModel):
    """Response nakon kreiranja"""
    success: bool
    collection_name: str
    message: str

class CollectionInfo(BaseModel):
    """Info o kolekciji"""
    name: str
    vectors_count: int
    points_count: int
    status: str  # active, inactive
    created_at: datetime
    size_bytes: int
    config: dict

class CollectionListResponse(BaseModel):
    """Lista kolekcija"""
    collections: list[CollectionInfo]
    active_collection: str | None

class CollectionSwitchRequest(BaseModel):
    """Prebacivanje na drugu kolekciju"""
    collection_name: str

class CollectionSwitchResponse(BaseModel):
    """Response nakon prebacivanja"""
    success: bool
    previous_collection: str
    active_collection: str
    message: str
```

### 2.7 Settings API Models
**Fajl**: `backend/api/schemas/settings.py`

```python
class SettingsResponse(BaseModel):
    """Trenutne postavke"""
    rag_config: dict
    llm_config: dict
    system_config: dict

class SettingsUpdateRequest(BaseModel):
    """Ažuriranje postavki"""
    rag_config: dict | None = None
    llm_config: dict | None = None
    system_config: dict | None = None

class SettingsUpdateResponse(BaseModel):
    """Response nakon ažuriranja"""
    success: bool
    message: str
    restart_required: bool
```

### 2.8 Feedback API Models
**Fajl**: `backend/api/schemas/feedback.py`

```python
class FeedbackSubmitRequest(BaseModel):
    """Slanje feedback-a"""
    message_id: int
    accuracy_rating: int  # 1-5
    language_rating: int  # 1-5
    chunk_relevance_rating: int  # 1-5
    comment: str | None = None

class FeedbackSubmitResponse(BaseModel):
    """Response nakon slanja"""
    success: bool
    feedback_id: int
    message: str

class FeedbackStatsResponse(BaseModel):
    """Statistika feedback-a"""
    total_feedback: int
    avg_accuracy_rating: float
    avg_language_rating: float
    avg_chunk_relevance_rating: float
    rating_distribution: dict
```

### 2.9 Config API Models
**Fajl**: `backend/api/schemas/config.py`

```python
class ProjectConfigExportRequest(BaseModel):
    """Export projekta"""
    project_name: str
    collection_name: str
    description: str | None = None
    include_pdfs: bool = True
    include_test_examples: bool = True
    include_evaluation_history: bool = True

class ProjectConfigExportResponse(BaseModel):
    """Response nakon export-a"""
    success: bool
    config_file: str
    download_url: str

class ProjectConfigImportRequest(BaseModel):
    """Import projekta"""
    restore_pdfs: bool = True
    restore_test_examples: bool = True
    apply_model_config: bool = True
    apply_rag_config: bool = True

class ProjectConfigImportResponse(BaseModel):
    """Response nakon import-a"""
    success: bool
    project_id: int
    imported: dict  # pdfs, test_examples, evaluations counts
    warnings: list[str]
```

---

## 3. Qdrant Vector Models

### 3.1 Document Chunk
**Opis**: Struktura chunk-a u Qdrant-u

```python
class DocumentChunk:
    """Chunk dokumenta sa vektorima"""
    id: str                          # UUID chunk-a
    vector: list[float]              # Dense vektor (1024 dim)
    sparse_vector: dict | None       # Sparse vektor za BM25
    payload: dict = {
        "text": str,                 # Tekst chunk-a
        "source": str,               # Naziv PDF-a
        "page": int,                 # Broj stranice
        "chunk_index": int,          # Redni broj chunk-a
        "pdf_id": int,               # FK -> pdfs.id
        "collection_name": str,      # Naziv kolekcije
        "language": str,             # Jezik (sr, en)
        "created_at": str            # ISO timestamp
    }
```

---

## 4. Configuration Models

### 4.1 RAG Configuration
**Fajl**: `backend/config/rag_config.py`

```python
class ChunkingConfig(BaseModel):
    """Konfiguracija chunking-a"""
    strategy: str = "semantic"       # semantic, fixed, sentence
    chunk_size: int = 500            # Veličina chunk-a
    chunk_overlap: int = 50          # Preklapanje

class SearchConfig(BaseModel):
    """Konfiguracija pretrage"""
    type: str = "hybrid"             # hybrid, semantic, bm25
    semantic_weight: float = 0.7     # Težina semantic search-a
    bm25_weight: float = 0.3         # Težina BM25
    top_k: int = 10                  # Broj rezultata

class RerankingConfig(BaseModel):
    """Konfiguracija reranking-a"""
    enabled: bool = True
    top_n: int = 5                   # Broj nakon reranking-a
    model: str = "BAAI/bge-reranker-v2-m3"

class RAGConfig(BaseModel):
    """Kompletna RAG konfiguracija"""
    chunking: ChunkingConfig
    search: SearchConfig
    reranking: RerankingConfig
```

### 4.2 LLM Configuration
**Fajl**: `backend/config/llm_config.py`

```python
class LLMConfig(BaseModel):
    """Konfiguracija LLM modela"""
    name: str = "qwen2.5:14b"        # Ollama model
    temperature: float = 0.1         # Temperatura (0-1)
    top_p: float = 0.9               # Top-p sampling
    max_tokens: int = 2048           # Max output tokens
    context_window: int = 32768      # Context window
    system_prompt: str               # System prompt
```

### 4.3 Embedding Configuration
**Fajl**: `backend/config/embedding_config.py`

```python
class EmbeddingConfig(BaseModel):
    """Konfiguracija embedding modela"""
    name: str = "BAAI/bge-m3"        # Model
    dimensions: int = 1024           # Dimenzije vektora
    batch_size: int = 128            # Batch size
    device: str = "cuda"             # cuda ili cpu
    precision: str = "fp16"          # fp16, fp32
```

---

## 📝 Konvencije Imenovanja

### Database Tables
- Lowercase, plural: `pdfs`, `chat_messages`, `test_examples`
- Foreign keys: `{table}_id` (npr. `pdf_id`, `message_id`)

### Python Classes
- PascalCase: `PDFModel`, `ChatMessage`, `TestExample`
- Pydantic models: `{Entity}{Action}Request/Response`

### API Endpoints
- Lowercase, plural: `/api/pdfs`, `/api/collections`
- Actions: POST (create), GET (read), PUT (update), DELETE (delete)

### JSON Fields
- snake_case: `collection_name`, `created_at`, `response_time_ms`

---

**Status**: ✅ Aktivan  
**Ažurira se**: Tokom razvoja svake faze