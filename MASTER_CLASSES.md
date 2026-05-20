# 🏗️ MASTER CLASSES - Katalog Svih Klasa i Servisa

> **🔒 VAŽNO**: Ovaj fajl je master referenca za sve klase, servise i njihove relacije u projektu. Ažurira se tokom razvoja. Koristi ga za konzistentnost arhitekture.

**Poslednje ažuriranje**: 2026-05-20  
**Verzija**: 1.0

---

## 📋 Sadržaj

1. [Backend Services](#1-backend-services)
2. [RAG Engine Classes](#2-rag-engine-classes)
3. [Database Models](#3-database-models)
4. [API Routers](#4-api-routers)
5. [Utility Classes](#5-utility-classes)
6. [Frontend Components](#6-frontend-components)
7. [Class Relationships](#7-class-relationships)

---

## 1. Backend Services

### 1.1 PDFService
**Fajl**: `backend/services/pdf_service.py`  
**Opis**: Upravlja PDF fajlovima - upload, procesiranje, brisanje

**Metode**:
```python
class PDFService:
    def __init__(self, db: Session, qdrant_client: QdrantClient):
        """Inicijalizacija servisa"""
        
    async def upload_pdf(
        self, 
        file: UploadFile, 
        collection_name: str,
        category: str | None = None
    ) -> PDF:
        """Upload i čuvanje PDF-a"""
        
    async def process_pdf(self, pdf_id: int) -> bool:
        """Procesiranje PDF-a (parsing, chunking, embeddings)"""
        
    def list_pdfs(
        self, 
        collection_name: str | None = None,
        status: str | None = None
    ) -> list[PDF]:
        """Lista PDF-ova sa filterima"""
        
    def get_pdf(self, pdf_id: int) -> PDF | None:
        """Vraća specifičan PDF"""
        
    async def delete_pdf(self, pdf_id: int) -> bool:
        """Briše PDF i sve chunk-ove"""
```

**Zavisnosti**:
- `Database Session`: Za SQLite operacije
- `QdrantClient`: Za brisanje vektora
- `PDFProcessor`: Za procesiranje PDF-ova
- `EmbeddingService`: Za kreiranje embeddings-a

---

### 1.2 TrainingService
**Fajl**: `backend/services/training_service.py`  
**Opis**: Upravlja procesom treninga (procesiranje PDF-ova i kreiranje embeddings-a)

**Metode**:
```python
class TrainingService:
    def __init__(
        self, 
        db: Session, 
        pdf_service: PDFService,
        embedding_service: EmbeddingService
    ):
        """Inicijalizacija servisa"""
        
    async def start_training(
        self, 
        collection_name: str,
        force_reprocess: bool = False
    ) -> str:
        """Pokreće trening job i vraća job_id"""
        
    async def get_training_status(self, job_id: str) -> dict:
        """Vraća status treninga"""
        
    async def cancel_training(self, job_id: str) -> bool:
        """Otkazuje trening u toku"""
        
    async def _training_worker(
        self, 
        job_id: str, 
        collection_name: str
    ):
        """Background worker za trening"""
```

**Zavisnosti**:
- `PDFService`: Za pristup PDF-ovima
- `EmbeddingService`: Za kreiranje embeddings-a
- `WebSocketManager`: Za slanje progress updates

---

### 1.3 ChatService
**Fajl**: `backend/services/chat_service.py`  
**Opis**: Upravlja chat funkcionalnostima - slanje poruka, istorija

**Metode**:
```python
class ChatService:
    def __init__(
        self, 
        db: Session,
        rag_engine: RAGEngine,
        llm_service: LLMService
    ):
        """Inicijalizacija servisa"""
        
    async def send_message(
        self,
        message: str,
        session_id: str,
        collection_name: str,
        model_name: str | None = None
    ) -> dict:
        """Šalje poruku i vraća odgovor"""
        
    def get_chat_history(
        self,
        session_id: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[ChatMessage]:
        """Vraća istoriju chat-a"""
        
    def clear_chat_history(self, session_id: str) -> int:
        """Briše istoriju chat-a"""
        
    async def _retrieve_context(
        self, 
        query: str, 
        collection_name: str
    ) -> list[dict]:
        """Preuzima relevantne chunk-ove"""
        
    async def _generate_response(
        self,
        query: str,
        context: list[dict],
        model_name: str
    ) -> str:
        """Generiše odgovor pomoću LLM-a"""
```

**Zavisnosti**:
- `RAGEngine`: Za pretragu i reranking
- `LLMService`: Za generisanje odgovora
- `Database Session`: Za čuvanje poruka

---

### 1.4 EmbeddingService
**Fajl**: `backend/services/embedding_service.py`  
**Opis**: Kreira embeddings za tekst koristeći BGE-M3 model

**Metode**:
```python
class EmbeddingService:
    def __init__(self, config: EmbeddingConfig):
        """Inicijalizacija modela"""
        
    def create_embeddings(
        self, 
        texts: list[str],
        batch_size: int | None = None
    ) -> list[list[float]]:
        """Kreira embeddings za listu tekstova"""
        
    def create_embedding(self, text: str) -> list[float]:
        """Kreira embedding za jedan tekst"""
        
    def get_model_info(self) -> dict:
        """Vraća informacije o modelu"""
        
    def _batch_encode(
        self, 
        texts: list[str], 
        batch_size: int
    ) -> list[list[float]]:
        """Batch encoding sa GPU optimizacijom"""
```

**Zavisnosti**:
- `sentence-transformers`: Za BGE-M3 model
- `torch`: Za GPU operacije
- `EmbeddingConfig`: Za konfiguraciju

---

### 1.5 LLMService
**Fajl**: `backend/services/llm_service.py`  
**Opis**: Komunicira sa Ollama API-jem za generisanje odgovora

**Metode**:
```python
class LLMService:
    def __init__(self, config: LLMConfig):
        """Inicijalizacija servisa"""
        
    async def generate(
        self,
        prompt: str,
        model_name: str | None = None,
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Generiše odgovor (sa ili bez streaming-a)"""
        
    async def list_models(self) -> list[dict]:
        """Lista dostupnih Ollama modela"""
        
    async def get_model_info(self, model_name: str) -> dict:
        """Informacije o specifičnom modelu"""
        
    def _build_prompt(
        self, 
        query: str, 
        context: list[dict]
    ) -> str:
        """Kreira prompt sa kontekstom"""
```

**Zavisnosti**:
- `httpx`: Za Ollama API komunikaciju
- `LLMConfig`: Za konfiguraciju

---

### 1.6 CollectionService
**Fajl**: `backend/services/collection_service.py`  
**Opis**: Upravlja Qdrant kolekcijama

**Metode**:
```python
class CollectionService:
    def __init__(self, qdrant_client: QdrantClient):
        """Inicijalizacija servisa"""
        
    def list_collections(self) -> list[dict]:
        """Lista svih kolekcija sa metapodacima"""
        
    def create_collection(
        self, 
        name: str, 
        vector_size: int = 1024
    ) -> bool:
        """Kreira novu kolekciju"""
        
    def delete_collection(self, name: str) -> bool:
        """Briše kolekciju"""
        
    def switch_collection(self, name: str) -> bool:
        """Prebacuje na drugu kolekciju"""
        
    def get_collection_info(self, name: str) -> dict | None:
        """Vraća informacije o kolekciji"""
        
    @property
    def active_collection(self) -> str | None:
        """Trenutno aktivna kolekcija"""
```

**Zavisnosti**:
- `QdrantClient`: Za Qdrant operacije
- `Database Session`: Za čuvanje metadata

---

### 1.7 EvaluationService
**Fajl**: `backend/services/evaluation_service.py`  
**Opis**: Izvršava evaluaciju sistema na test setovima

**Metode**:
```python
class EvaluationService:
    def __init__(
        self,
        db: Session,
        chat_service: ChatService,
        test_example_service: TestExampleService
    ):
        """Inicijalizacija servisa"""
        
    async def start_evaluation(
        self,
        version_name: str,
        collection_name: str,
        test_example_ids: list[int] | None = None
    ) -> str:
        """Pokreće evaluaciju i vraća job_id"""
        
    async def get_evaluation_status(self, job_id: str) -> dict:
        """Status evaluacije"""
        
    def get_evaluation_results(
        self, 
        evaluation_id: int
    ) -> Evaluation | None:
        """Rezultati evaluacije"""
        
    def list_evaluations(
        self,
        collection_name: str | None = None
    ) -> list[Evaluation]:
        """Lista svih evaluacija"""
        
    def compare_evaluations(
        self,
        evaluation_id_1: int,
        evaluation_id_2: int
    ) -> dict:
        """Poredi dve evaluacije"""
        
    async def _evaluation_worker(
        self,
        job_id: str,
        version_name: str,
        collection_name: str,
        test_examples: list[TestExample]
    ):
        """Background worker za evaluaciju"""
        
    def _calculate_metrics(
        self,
        results: list[dict]
    ) -> dict:
        """Računa metrike (accuracy, precision, recall, F1)"""
```

**Zavisnosti**:
- `ChatService`: Za slanje test pitanja
- `TestExampleService`: Za pristup test primerima
- `WebSocketManager`: Za progress updates

---

### 1.8 TestExampleService
**Fajl**: `backend/services/test_example_service.py`  
**Opis**: Upravlja test primerima

**Metode**:
```python
class TestExampleService:
    def __init__(self, db: Session):
        """Inicijalizacija servisa"""
        
    def list_test_examples(
        self,
        collection_name: str | None = None,
        category: str | None = None,
        difficulty: str | None = None
    ) -> list[TestExample]:
        """Lista test primera sa filterima"""
        
    def create_test_example(
        self, 
        data: TestExampleCreate
    ) -> TestExample:
        """Kreira novi test primer"""
        
    def update_test_example(
        self,
        example_id: int,
        data: TestExampleUpdate
    ) -> TestExample | None:
        """Ažurira test primer"""
        
    def delete_test_example(self, example_id: int) -> bool:
        """Briše test primer"""
        
    def import_test_examples(
        self,
        examples: list[TestExampleCreate]
    ) -> int:
        """Import test primera iz liste"""
        
    def export_test_examples(
        self,
        collection_name: str | None = None
    ) -> list[dict]:
        """Export test primera u JSON format"""
```

**Zavisnosti**:
- `Database Session`: Za CRUD operacije

---

### 1.9 FeedbackService
**Fajl**: `backend/services/feedback_service.py`  
**Opis**: Upravlja feedback-om korisnika

**Metode**:
```python
class FeedbackService:
    def __init__(self, db: Session):
        """Inicijalizacija servisa"""
        
    def submit_feedback(
        self, 
        data: FeedbackSubmitRequest
    ) -> Feedback:
        """Čuva feedback"""
        
    def get_feedback_stats(
        self,
        collection_name: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> dict:
        """Statistika feedback-a"""
        
    def get_message_feedback(
        self, 
        message_id: int
    ) -> Feedback | None:
        """Feedback za specifičnu poruku"""
```

**Zavisnosti**:
- `Database Session`: Za CRUD operacije

---

### 1.10 ConfigService
**Fajl**: `backend/services/config_service.py`  
**Opis**: Upravlja export/import projekata

**Metode**:
```python
class ConfigService:
    def __init__(
        self,
        db: Session,
        pdf_service: PDFService,
        test_example_service: TestExampleService,
        evaluation_service: EvaluationService
    ):
        """Inicijalizacija servisa"""
        
    async def export_config(
        self, 
        data: ProjectConfigExportRequest
    ) -> str:
        """Export projekta u JSON fajl"""
        
    async def import_config(
        self,
        config_file: UploadFile,
        options: ProjectConfigImportRequest
    ) -> dict:
        """Import projekta iz JSON fajla"""
        
    def list_configs(self) -> list[dict]:
        """Lista sačuvanih konfiguracija"""
        
    def compare_configs(
        self,
        config1: str,
        config2: str
    ) -> dict:
        """Poredi dve konfiguracije"""
        
    def delete_config(self, filename: str) -> bool:
        """Briše konfiguraciju"""
```

**Zavisnosti**:
- `PDFService`: Za PDF podatke
- `TestExampleService`: Za test primere
- `EvaluationService`: Za evaluacije

---

## 2. RAG Engine Classes

### 2.1 RAGEngine
**Fajl**: `backend/rag/rag_engine.py`  
**Opis**: Glavni RAG engine - koordinira sve RAG komponente

**Metode**:
```python
class RAGEngine:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_service: EmbeddingService,
        reranker: Reranker,
        config: RAGConfig
    ):
        """Inicijalizacija RAG engine-a"""
        
    async def search(
        self,
        query: str,
        collection_name: str,
        top_k: int | None = None
    ) -> list[dict]:
        """Hybrid search sa reranking-om"""
        
    async def _semantic_search(
        self,
        query: str,
        collection_name: str,
        top_k: int
    ) -> list[dict]:
        """Semantic search koristeći embeddings"""
        
    async def _bm25_search(
        self,
        query: str,
        collection_name: str,
        top_k: int
    ) -> list[dict]:
        """BM25 keyword search"""
        
    async def _hybrid_search(
        self,
        query: str,
        collection_name: str,
        top_k: int
    ) -> list[dict]:
        """Kombinuje semantic i BM25 search"""
        
    async def _rerank_results(
        self,
        query: str,
        results: list[dict],
        top_n: int
    ) -> list[dict]:
        """Reranking rezultata"""
```

**Zavisnosti**:
- `QdrantClient`: Za vector search
- `EmbeddingService`: Za query embeddings
- `Reranker`: Za reranking
- `RAGConfig`: Za konfiguraciju

---

### 2.2 PDFProcessor
**Fajl**: `backend/rag/pdf_processor.py`  
**Opis**: Procesira PDF fajlove - parsing, transliteracija, chunking

**Metode**:
```python
class PDFProcessor:
    def __init__(self, config: ChunkingConfig):
        """Inicijalizacija procesora"""
        
    def process_pdf(self, pdf_path: str) -> list[dict]:
        """Procesira PDF i vraća chunk-ove"""
        
    def _extract_text(self, pdf_path: str) -> str:
        """Ekstraktuje tekst iz PDF-a"""
        
    def _transliterate(self, text: str) -> str:
        """Konvertuje ćirilicu u latinicu"""
        
    def _chunk_text(self, text: str) -> list[str]:
        """Deli tekst na chunk-ove"""
        
    def _semantic_chunking(self, text: str) -> list[str]:
        """Semantičko chunking"""
        
    def _fixed_chunking(self, text: str) -> list[str]:
        """Fixed-size chunking"""
```

**Zavisnosti**:
- `PyMuPDF (fitz)`: Za PDF parsing
- `CyrillicToLatin`: Za transliteraciju
- `ChunkingConfig`: Za konfiguraciju

---

### 2.3 Reranker
**Fajl**: `backend/rag/reranker.py`  
**Opis**: Reranking rezultata pretrage

**Metode**:
```python
class Reranker:
    def __init__(self, config: RerankingConfig):
        """Inicijalizacija reranker modela"""
        
    def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int | None = None
    ) -> list[tuple[int, float]]:
        """Reranking dokumenata"""
        
    def _batch_rerank(
        self,
        query: str,
        documents: list[str],
        batch_size: int
    ) -> list[float]:
        """Batch reranking sa GPU optimizacijom"""
```

**Zavisnosti**:
- `sentence-transformers`: Za BGE-reranker model
- `torch`: Za GPU operacije
- `RerankingConfig`: Za konfiguraciju

---

### 2.4 CyrillicToLatin
**Fajl**: `backend/rag/cyrillic_to_latin.py`  
**Opis**: Konverzija ćirilice u latinicu

**Metode**:
```python
class CyrillicToLatin:
    def __init__(self):
        """Inicijalizacija mapping tabele"""
        
    def convert(self, text: str) -> str:
        """Konvertuje tekst"""
        
    def _build_mapping(self) -> dict:
        """Kreira mapping tabelu"""
```

**Zavisnosti**: Nema

---

### 2.5 SpellChecker
**Fajl**: `backend/rag/spell_checker.py`  
**Opis**: Provera i korekcija pravopisa

**Metode**:
```python
class SpellChecker:
    def __init__(self, dictionary_path: str):
        """Inicijalizacija rečnika"""
        
    def check(self, text: str) -> list[str]:
        """Pronalazi greške"""
        
    def correct(self, text: str) -> str:
        """Koriguje greške"""
        
    def add_word(self, word: str):
        """Dodaje reč u rečnik"""
```

**Zavisnosti**:
- Custom dictionary file

---

## 3. Database Models

### 3.1 PDF
**Fajl**: `backend/models/pdf.py`  
**Opis**: SQLAlchemy model za PDF fajlove

**Relacije**:
- `collection`: Many-to-One sa `Collection`
- `chat_messages`: One-to-Many sa `ChatMessage` (preko collection)

---

### 3.2 TestExample
**Fajl**: `backend/models/test_example.py`  
**Opis**: SQLAlchemy model za test primere

**Relacije**:
- `collection`: Many-to-One sa `Collection`

---

### 3.3 ChatMessage
**Fajl**: `backend/models/chat.py`  
**Opis**: SQLAlchemy model za chat poruke

**Relacije**:
- `feedback`: One-to-One sa `Feedback`
- `collection`: Many-to-One sa `Collection`

---

### 3.4 Feedback
**Fajl**: `backend/models/feedback.py`  
**Opis**: SQLAlchemy model za feedback

**Relacije**:
- `message`: One-to-One sa `ChatMessage`

---

### 3.5 Evaluation
**Fajl**: `backend/models/evaluation.py`  
**Opis**: SQLAlchemy model za evaluacije

**Relacije**:
- `collection`: Many-to-One sa `Collection`

---

### 3.6 Collection
**Fajl**: `backend/models/collection.py`  
**Opis**: SQLAlchemy model za kolekcije

**Relacije**:
- `pdfs`: One-to-Many sa `PDF`
- `test_examples`: One-to-Many sa `TestExample`
- `evaluations`: One-to-Many sa `Evaluation`
- `chat_messages`: One-to-Many sa `ChatMessage`

---

### 3.7 Settings
**Fajl**: `backend/models/settings.py`  
**Opis**: SQLAlchemy model za postavke

**Relacije**: Nema

---

### 3.8 SessionLog
**Fajl**: `backend/models/session_log.py`  
**Opis**: SQLAlchemy model za session logove

**Relacije**:
- `collection`: Many-to-One sa `Collection`

---

## 4. API Routers

### 4.1 PDFRouter
**Fajl**: `backend/api/pdfs.py`  
**Opis**: API endpoints za PDF management

**Endpoints**:
- `POST /api/pdfs` - Upload PDF
- `GET /api/pdfs` - List PDFs
- `GET /api/pdfs/{pdf_id}` - Get PDF
- `DELETE /api/pdfs/{pdf_id}` - Delete PDF

**Zavisnosti**:
- `PDFService`

---

### 4.2 TrainingRouter
**Fajl**: `backend/api/training.py`  
**Opis**: API endpoints za training

**Endpoints**:
- `POST /api/training/start` - Start training
- `GET /api/training/status/{job_id}` - Get status
- `POST /api/training/cancel/{job_id}` - Cancel training

**Zavisnosti**:
- `TrainingService`

---

### 4.3 ChatRouter
**Fajl**: `backend/api/chat.py`  
**Opis**: API endpoints za chat

**Endpoints**:
- `POST /api/chat/message` - Send message
- `GET /api/chat/history` - Get history
- `DELETE /api/chat/history/{session_id}` - Clear history

**Zavisnosti**:
- `ChatService`

---

### 4.4 ModelsRouter
**Fajl**: `backend/api/models.py`  
**Opis**: API endpoints za Ollama models

**Endpoints**:
- `GET /api/models` - List models
- `GET /api/models/{model_name}` - Get model info

**Zavisnosti**:
- `LLMService`

---

### 4.5 TestExamplesRouter
**Fajl**: `backend/api/test_examples.py`  
**Opis**: API endpoints za test examples

**Endpoints**:
- `GET /api/test-examples` - List examples
- `POST /api/test-examples` - Create example
- `PUT /api/test-examples/{example_id}` - Update example
- `DELETE /api/test-examples/{example_id}` - Delete example
- `POST /api/test-examples/import` - Import examples
- `GET /api/test-examples/export` - Export examples

**Zavisnosti**:
- `TestExampleService`

---

### 4.6 EvaluationRouter
**Fajl**: `backend/api/evaluation.py`  
**Opis**: API endpoints za evaluation

**Endpoints**:
- `POST /api/evaluation/start` - Start evaluation
- `GET /api/evaluation/status/{job_id}` - Get status
- `GET /api/evaluation/results/{evaluation_id}` - Get results
- `GET /api/evaluation/list` - List evaluations
- `POST /api/evaluation/compare` - Compare evaluations

**Zavisnosti**:
- `EvaluationService`

---

### 4.7 CollectionsRouter
**Fajl**: `backend/api/collections.py`  
**Opis**: API endpoints za collections

**Endpoints**:
- `GET /api/collections` - List collections
- `POST /api/collections` - Create collection
- `PUT /api/collections/active` - Switch collection
- `DELETE /api/collections/{collection_name}` - Delete collection
- `GET /api/collections/{collection_name}` - Get collection info

**Zavisnosti**:
- `CollectionService`

---

### 4.8 SettingsRouter
**Fajl**: `backend/api/settings.py`  
**Opis**: API endpoints za settings

**Endpoints**:
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings
- `POST /api/settings/restart` - Restart system

**Zavisnosti**:
- `SettingsService`

---

### 4.9 FeedbackRouter
**Fajl**: `backend/api/feedback.py`  
**Opis**: API endpoints za feedback

**Endpoints**:
- `POST /api/feedback` - Submit feedback
- `GET /api/feedback/stats` - Get stats

**Zavisnosti**:
- `FeedbackService`

---

### 4.10 SessionsRouter
**Fajl**: `backend/api/sessions.py`  
**Opis**: API endpoints za sessions

**Endpoints**:
- `POST /api/sessions/start` - Start logging
- `POST /api/sessions/stop` - Stop logging
- `GET /api/sessions/download/{session_id}` - Download log

**Zavisnosti**:
- `SessionService`

---

### 4.11 ConfigRouter
**Fajl**: `backend/api/config.py`  
**Opis**: API endpoints za project config

**Endpoints**:
- `POST /api/config/export` - Export config
- `POST /api/config/import` - Import config
- `GET /api/config/list` - List configs
- `POST /api/config/compare` - Compare configs
- `DELETE /api/config/{filename}` - Delete config

**Zavisnosti**:
- `ConfigService`

---

### 4.12 WebSocketRouter
**Fajl**: `backend/api/websockets.py`  
**Opis**: WebSocket endpoints

**Endpoints**:
- `WS /api/ws/training/{job_id}` - Training progress
- `WS /api/ws/evaluation/{job_id}` - Evaluation progress
- `WS /api/ws/chat` - Chat streaming

**Zavisnosti**:
- `WebSocketManager`

---

## 5. Utility Classes

### 5.1 WebSocketManager
**Fajl**: `backend/utils/websocket_manager.py`  
**Opis**: Upravlja WebSocket konekcijama

**Metode**:
```python
class WebSocketManager:
    def __init__(self):
        """Inicijalizacija managera"""
        
    async def connect(
        self, 
        websocket: WebSocket, 
        client_id: str
    ):
        """Dodaje novu konekciju"""
        
    def disconnect(self, client_id: str):
        """Uklanja konekciju"""
        
    async def send_message(
        self, 
        client_id: str, 
        message: dict
    ):
        """Šalje poruku klijentu"""
        
    async def broadcast(self, message: dict):
        """Broadcast svim klijentima"""
```

---

### 5.2 JobManager
**Fajl**: `backend/utils/job_manager.py`  
**Opis**: Upravlja background job-ovima

**Metode**:
```python
class JobManager:
    def __init__(self):
        """Inicijalizacija managera"""
        
    def create_job(self, job_type: str) -> str:
        """Kreira novi job i vraća job_id"""
        
    def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        progress: float
    ):
        """Ažurira status job-a"""
        
    def get_job_status(self, job_id: str) -> dict:
        """Vraća status job-a"""
        
    def cancel_job(self, job_id: str) -> bool:
        """Otkazuje job"""
```

---

### 5.3 FileManager
**Fajl**: `backend/utils/file_manager.py`  
**Opis**: Upravlja fajlovima na disku

**Metode**:
```python
class FileManager:
    def __init__(self, base_path: str):
        """Inicijalizacija managera"""
        
    async def save_file(
        self, 
        file: UploadFile, 
        directory: str
    ) -> str:
        """Čuva fajl na disk"""
        
    def delete_file(self, filepath: str) -> bool:
        """Briše fajl"""
        
    def get_file_info(self, filepath: str) -> dict:
        """Vraća informacije o fajlu"""
```

---

## 6. Frontend Components

### 6.1 PDFManagement
**Fajl**: `frontend/src/components/PDFManagement.tsx`  
**Opis**: Komponenta za upravljanje PDF-ovima

**Props**: Nema  
**State**:
- `pdfs`: Lista PDF-ova
- `uploading`: Upload status
- `selectedCollection`: Aktivna kolekcija

---

### 6.2 ChatInterface
**Fajl**: `frontend/src/components/ChatInterface.tsx`  
**Opis**: Chat interfejs

**Props**:
- `collectionName`: Aktivna kolekcija

**State**:
- `messages`: Lista poruka
- `inputMessage`: Trenutna poruka
- `isLoading`: Loading status

---

### 6.3 TestExamplesManager
**Fajl**: `frontend/src/components/TestExamplesManager.tsx`  
**Opis**: Upravljanje test primerima

**Props**:
- `collectionName`: Aktivna kolekcija

**State**:
- `examples`: Lista primera
- `editingExample`: Primer u editovanju

---

### 6.4 EvaluationPanel
**Fajl**: `frontend/src/components/EvaluationPanel.tsx`  
**Opis**: Panel za evaluaciju

**Props**:
- `collectionName`: Aktivna kolekcija

**State**:
- `evaluations`: Lista evaluacija
- `runningEvaluation`: Trenutna evaluacija
- `progress`: Progress evaluacije

---

### 6.5 SettingsPanel
**Fajl**: `frontend/src/components/SettingsPanel.tsx`  
**Opis**: Panel za postavke

**Props**: Nema  
**State**:
- `ragConfig`: RAG konfiguracija
- `llmConfig`: LLM konfiguracija
- `systemConfig`: System konfiguracija

---

### 6.6 CollectionSelector
**Fajl**: `frontend/src/components/CollectionSelector.tsx`  
**Opis**: Selector za kolekcije

**Props**:
- `onCollectionChange`: Callback za promenu

**State**:
- `collections`: Lista kolekcija
- `activeCollection`: Aktivna kolekcija

---

## 7. Class Relationships

### 7.1 Service Dependencies

```
PDFService
├── Database Session
├── QdrantClient
├── PDFProcessor
└── EmbeddingService

TrainingService
├── PDFService
├── EmbeddingService
└── WebSocketManager

ChatService
├── Database Session
├── RAGEngine
└── LLMService

RAGEngine
├── QdrantClient
├── EmbeddingService
├── Reranker
└── RAGConfig

EvaluationService
├── Database Session
├── ChatService
├── TestExampleService
└── WebSocketManager

ConfigService
├── Database Session
├── PDFService
├── TestExampleService
└── EvaluationService
```

### 7.2 Model Relationships

```
Collection (1) ──< (N) PDF
Collection (1) ──< (N) TestExample
Collection (1) ──< (N) Evaluation
Collection (1) ──< (N) ChatMessage
Collection (1) ──< (N) SessionLog

ChatMessage (1) ──< (1) Feedback
```

### 7.3 API Router Dependencies

```
All Routers
└── Corresponding Service

WebSocketRouter
└── WebSocketManager
```

---

## 📝 Konvencije

### Class Naming
- Services: `{Entity}Service` (npr. `PDFService`, `ChatService`)
- Models: `{Entity}` (npr. `PDF`, `ChatMessage`)
- Routers: `{Entity}Router` (npr. `PDFRouter`, `ChatRouter`)
- Utilities: `{Purpose}Manager` (npr. `WebSocketManager`, `JobManager`)

### Method Naming
- CRUD: `create_`, `get_`, `list_`, `update_`, `delete_`
- Async: `async def` za I/O operacije
- Private: `_method_name` za interne metode

### File Organization
- Services: `backend/services/`
- Models: `backend/models/`
- API: `backend/api/`
- RAG: `backend/rag/`
- Utils: `backend/utils/`

---

**Status**: ✅ Aktivan  
**Ažurira se**: Tokom razvoja svake faze