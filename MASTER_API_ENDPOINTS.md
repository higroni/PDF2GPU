# 🌐 MASTER API ENDPOINTS - Katalog Svih API Endpointa

> **🔒 VAŽNO**: Ovaj fajl je master referenca za sve API endpoints u projektu. Ažurira se tokom razvoja. Koristi ga za konzistentnost API dizajna.

**Poslednje ažuriranje**: 2026-05-20  
**Verzija**: 1.0  
**Base URL**: `http://localhost:8000`

---

## 📋 Sadržaj

1. [PDF Management](#1-pdf-management)
2. [Training & Processing](#2-training--processing)
3. [Chat Interface](#3-chat-interface)
4. [Models Management](#4-models-management)
5. [Test Examples](#5-test-examples)
6. [Evaluation](#6-evaluation)
7. [Collections](#7-collections)
8. [Settings](#8-settings)
9. [Feedback](#9-feedback)
10. [Sessions](#10-sessions)
11. [Project Configuration](#11-project-configuration)
12. [WebSocket Endpoints](#12-websocket-endpoints)

---

## 1. PDF Management

### 1.1 Upload PDF
**Endpoint**: `POST /api/pdfs`  
**Fajl**: `backend/api/pdfs.py::upload_pdf()`  
**Opis**: Upload novog PDF fajla

**Request**:
```http
POST /api/pdfs
Content-Type: multipart/form-data

file: [PDF file]
category: "zakoni" (optional)
collection_name: "poreski_propisi_test_1"
```

**Response**:
```json
{
  "success": true,
  "pdf_id": 123,
  "filename": "Godisnji_porez_na_dohodak_gradjana.pdf",
  "message": "PDF uploaded successfully"
}
```

**Status Codes**:
- 200: Success
- 400: Invalid file format
- 413: File too large
- 500: Server error

---

### 1.2 List PDFs
**Endpoint**: `GET /api/pdfs`  
**Fajl**: `backend/api/pdfs.py::list_pdfs()`  
**Opis**: Lista svih uploadovanih PDF-ova

**Request**:
```http
GET /api/pdfs?collection_name=poreski_propisi_test_1&status=completed
```

**Query Parameters**:
- `collection_name` (optional): Filter po kolekciji
- `status` (optional): Filter po statusu (pending, processing, completed, failed)
- `category` (optional): Filter po kategoriji
- `limit` (optional): Broj rezultata (default: 100)
- `offset` (optional): Offset za paginaciju (default: 0)

**Response**:
```json
{
  "pdfs": [
    {
      "id": 123,
      "filename": "Godisnji_porez_na_dohodak_gradjana.pdf",
      "size_bytes": 1234567,
      "pages": 45,
      "uploaded_at": "2026-05-20T12:00:00Z",
      "status": "completed",
      "chunks_count": 234,
      "collection_name": "poreski_propisi_test_1"
    }
  ],
  "total": 1
}
```

---

### 1.3 Get PDF Details
**Endpoint**: `GET /api/pdfs/{pdf_id}`  
**Fajl**: `backend/api/pdfs.py::get_pdf()`  
**Opis**: Detalji o specifičnom PDF-u

**Request**:
```http
GET /api/pdfs/123
```

**Response**:
```json
{
  "id": 123,
  "filename": "Godisnji_porez_na_dohodak_gradjana.pdf",
  "filepath": "data/pdfs/Godisnji_porez_na_dohodak_gradjana.pdf",
  "size_bytes": 1234567,
  "pages": 45,
  "uploaded_at": "2026-05-20T12:00:00Z",
  "processed_at": "2026-05-20T12:05:00Z",
  "chunks_count": 234,
  "collection_name": "poreski_propisi_test_1",
  "category": "zakoni",
  "language": "sr",
  "status": "completed"
}
```

---

### 1.4 Delete PDF
**Endpoint**: `DELETE /api/pdfs/{pdf_id}`  
**Fajl**: `backend/api/pdfs.py::delete_pdf()`  
**Opis**: Briše PDF i sve povezane chunk-ove

**Request**:
```http
DELETE /api/pdfs/123
```

**Response**:
```json
{
  "success": true,
  "message": "PDF deleted successfully",
  "deleted_chunks": 234
}
```

---

## 2. Training & Processing

### 2.1 Start Training
**Endpoint**: `POST /api/training/start`  
**Fajl**: `backend/api/training.py::start_training()`  
**Opis**: Pokreće procesiranje PDF-ova i kreiranje embeddings-a

**Request**:
```json
{
  "collection_name": "poreski_propisi_test_1",
  "force_reprocess": false
}
```

**Response**:
```json
{
  "success": true,
  "job_id": "train_abc123",
  "message": "Training started"
}
```

---

### 2.2 Get Training Status
**Endpoint**: `GET /api/training/status/{job_id}`  
**Fajl**: `backend/api/training.py::get_training_status()`  
**Opis**: Status trenutnog treninga

**Request**:
```http
GET /api/training/status/train_abc123
```

**Response**:
```json
{
  "job_id": "train_abc123",
  "status": "processing",
  "progress": 45.5,
  "current_step": "Creating embeddings",
  "total_steps": 5,
  "completed_steps": 2,
  "estimated_time_remaining_seconds": 120,
  "error_message": null
}
```

**Status Values**:
- `pending`: Čeka na početak
- `processing`: U toku
- `completed`: Završeno
- `failed`: Greška

---

### 2.3 Cancel Training
**Endpoint**: `POST /api/training/cancel/{job_id}`  
**Fajl**: `backend/api/training.py::cancel_training()`  
**Opis**: Otkazuje trening u toku

**Request**:
```http
POST /api/training/cancel/train_abc123
```

**Response**:
```json
{
  "success": true,
  "message": "Training cancelled"
}
```

---

## 3. Chat Interface

### 3.1 Send Message
**Endpoint**: `POST /api/chat/message`  
**Fajl**: `backend/api/chat.py::send_message()`  
**Opis**: Šalje poruku i dobija odgovor

**Request**:
```json
{
  "message": "Kolika je stopa poreza na dohodak?",
  "session_id": "session_xyz789",
  "model_name": "qwen2.5:14b",
  "collection_name": "poreski_propisi_test_1"
}
```

**Response**:
```json
{
  "success": true,
  "message_id": 456,
  "response": "Stopa poreza na dohodak za prihode do 3 miliona dinara godišnje iznosi 10%.",
  "session_id": "session_xyz789",
  "retrieved_chunks": 5,
  "response_time_ms": 1250,
  "sources": [
    {
      "text": "Chunk teksta...",
      "source": "Godisnji_porez_na_dohodak_gradjana.pdf",
      "page": 12,
      "score": 0.89
    }
  ]
}
```

---

### 3.2 Get Chat History
**Endpoint**: `GET /api/chat/history`  
**Fajl**: `backend/api/chat.py::get_chat_history()`  
**Opis**: Istorija chat poruka

**Request**:
```http
GET /api/chat/history?session_id=session_xyz789&limit=50
```

**Query Parameters**:
- `session_id` (optional): Filter po sesiji
- `limit` (optional): Broj poruka (default: 50)
- `offset` (optional): Offset (default: 0)

**Response**:
```json
{
  "messages": [
    {
      "id": 456,
      "session_id": "session_xyz789",
      "role": "user",
      "content": "Kolika je stopa poreza?",
      "timestamp": "2026-05-20T13:00:00Z"
    },
    {
      "id": 457,
      "session_id": "session_xyz789",
      "role": "assistant",
      "content": "Stopa poreza iznosi 10%.",
      "timestamp": "2026-05-20T13:00:02Z",
      "model_name": "qwen2.5:14b",
      "retrieved_chunks": 5,
      "response_time_ms": 1250
    }
  ],
  "session_id": "session_xyz789",
  "total": 2
}
```

---

### 3.3 Clear Chat History
**Endpoint**: `DELETE /api/chat/history/{session_id}`  
**Fajl**: `backend/api/chat.py::clear_chat_history()`  
**Opis**: Briše istoriju chat-a

**Request**:
```http
DELETE /api/chat/history/session_xyz789
```

**Response**:
```json
{
  "success": true,
  "message": "Chat history cleared",
  "deleted_messages": 10
}
```

---

## 4. Models Management

### 4.1 List Available Models
**Endpoint**: `GET /api/models`  
**Fajl**: `backend/api/models.py::list_models()`  
**Opis**: Lista dostupnih Ollama modela

**Request**:
```http
GET /api/models
```

**Response**:
```json
{
  "models": [
    {
      "name": "qwen2.5:14b",
      "size": "8.5GB",
      "modified_at": "2026-05-15T10:00:00Z",
      "details": {
        "format": "gguf",
        "family": "qwen2",
        "parameter_size": "14B",
        "quantization_level": "Q4_K_M"
      }
    },
    {
      "name": "llama3.1:8b",
      "size": "4.7GB",
      "modified_at": "2026-05-10T08:00:00Z"
    }
  ]
}
```

---

### 4.2 Get Model Info
**Endpoint**: `GET /api/models/{model_name}`  
**Fajl**: `backend/api/models.py::get_model_info()`  
**Opis**: Detalji o specifičnom modelu

**Request**:
```http
GET /api/models/qwen2.5:14b
```

**Response**:
```json
{
  "name": "qwen2.5:14b",
  "size": "8.5GB",
  "modified_at": "2026-05-15T10:00:00Z",
  "details": {
    "format": "gguf",
    "family": "qwen2",
    "parameter_size": "14B",
    "quantization_level": "Q4_K_M"
  },
  "modelfile": "FROM qwen2.5:14b\nPARAMETER temperature 0.1"
}
```

---

## 5. Test Examples

### 5.1 List Test Examples
**Endpoint**: `GET /api/test-examples`  
**Fajl**: `backend/api/test_examples.py::list_test_examples()`  
**Opis**: Lista svih test primera

**Request**:
```http
GET /api/test-examples?collection_name=poreski_propisi_test_1&category=porezi
```

**Query Parameters**:
- `collection_name` (optional): Filter po kolekciji
- `category` (optional): Filter po kategoriji
- `difficulty` (optional): Filter po težini (easy, medium, hard)

**Response**:
```json
{
  "examples": [
    {
      "id": 1,
      "question": "Kolika je stopa poreza?",
      "expected_answer": "Stopa poreza iznosi 10%.",
      "category": "porezi",
      "difficulty": "easy",
      "created_at": "2026-05-20T12:00:00Z",
      "collection_name": "poreski_propisi_test_1"
    }
  ],
  "total": 1
}
```

---

### 5.2 Create Test Example
**Endpoint**: `POST /api/test-examples`  
**Fajl**: `backend/api/test_examples.py::create_test_example()`  
**Opis**: Kreira novi test primer

**Request**:
```json
{
  "question": "Kolika je stopa poreza?",
  "expected_answer": "Stopa poreza iznosi 10%.",
  "category": "porezi",
  "difficulty": "easy",
  "collection_name": "poreski_propisi_test_1"
}
```

**Response**:
```json
{
  "id": 1,
  "question": "Kolika je stopa poreza?",
  "expected_answer": "Stopa poreza iznosi 10%.",
  "category": "porezi",
  "difficulty": "easy",
  "created_at": "2026-05-20T12:00:00Z",
  "collection_name": "poreski_propisi_test_1"
}
```

---

### 5.3 Update Test Example
**Endpoint**: `PUT /api/test-examples/{example_id}`  
**Fajl**: `backend/api/test_examples.py::update_test_example()`  
**Opis**: Ažurira test primer

**Request**:
```json
{
  "question": "Kolika je stopa poreza na dohodak?",
  "expected_answer": "Stopa poreza na dohodak iznosi 10%.",
  "difficulty": "medium"
}
```

**Response**:
```json
{
  "id": 1,
  "question": "Kolika je stopa poreza na dohodak?",
  "expected_answer": "Stopa poreza na dohodak iznosi 10%.",
  "category": "porezi",
  "difficulty": "medium",
  "created_at": "2026-05-20T12:00:00Z",
  "updated_at": "2026-05-20T13:00:00Z",
  "collection_name": "poreski_propisi_test_1"
}
```

---

### 5.4 Delete Test Example
**Endpoint**: `DELETE /api/test-examples/{example_id}`  
**Fajl**: `backend/api/test_examples.py::delete_test_example()`  
**Opis**: Briše test primer

**Request**:
```http
DELETE /api/test-examples/1
```

**Response**:
```json
{
  "success": true,
  "message": "Test example deleted"
}
```

---

### 5.5 Import Test Examples
**Endpoint**: `POST /api/test-examples/import`  
**Fajl**: `backend/api/test_examples.py::import_test_examples()`  
**Opis**: Import test primera iz JSON-a

**Request**:
```json
{
  "examples": [
    {
      "question": "Pitanje 1?",
      "expected_answer": "Odgovor 1",
      "category": "porezi",
      "difficulty": "easy",
      "collection_name": "poreski_propisi_test_1"
    }
  ],
  "collection_name": "poreski_propisi_test_1"
}
```

**Response**:
```json
{
  "success": true,
  "imported_count": 1,
  "message": "Test examples imported successfully"
}
```

---

### 5.6 Export Test Examples
**Endpoint**: `GET /api/test-examples/export`  
**Fajl**: `backend/api/test_examples.py::export_test_examples()`  
**Opis**: Export test primera u JSON

**Request**:
```http
GET /api/test-examples/export?collection_name=poreski_propisi_test_1
```

**Response**: JSON file download

---

## 6. Evaluation

### 6.1 Start Evaluation
**Endpoint**: `POST /api/evaluation/start`  
**Fajl**: `backend/api/evaluation.py::start_evaluation()`  
**Opis**: Pokreće evaluaciju sistema

**Request**:
```json
{
  "version_name": "phase1_baseline",
  "collection_name": "poreski_propisi_test_1",
  "test_example_ids": [1, 2, 3]
}
```

**Response**:
```json
{
  "success": true,
  "job_id": "eval_def456",
  "message": "Evaluation started"
}
```

---

### 6.2 Get Evaluation Status
**Endpoint**: `GET /api/evaluation/status/{job_id}`  
**Fajl**: `backend/api/evaluation.py::get_evaluation_status()`  
**Opis**: Status evaluacije

**Request**:
```http
GET /api/evaluation/status/eval_def456
```

**Response**:
```json
{
  "job_id": "eval_def456",
  "status": "processing",
  "progress": 60.0,
  "current_question": 30,
  "total_questions": 50,
  "estimated_time_remaining_seconds": 45
}
```

---

### 6.3 Get Evaluation Results
**Endpoint**: `GET /api/evaluation/results/{evaluation_id}`  
**Fajl**: `backend/api/evaluation.py::get_evaluation_results()`  
**Opis**: Rezultati evaluacije

**Request**:
```http
GET /api/evaluation/results/123
```

**Response**:
```json
{
  "id": 123,
  "version_name": "phase1_baseline",
  "collection_name": "poreski_propisi_test_1",
  "timestamp": "2026-05-20T14:00:00Z",
  "duration_seconds": 120,
  "total_questions": 50,
  "correct_answers": 42,
  "accuracy": 0.84,
  "precision": 0.86,
  "recall": 0.82,
  "f1_score": 0.84,
  "avg_response_time_ms": 1500,
  "gpu_utilization_avg": 0.75,
  "config_snapshot": {
    "llm_temperature": 0.1,
    "chunk_size": 500,
    "top_k": 10
  }
}
```

---

### 6.4 List All Evaluations
**Endpoint**: `GET /api/evaluation/list`  
**Fajl**: `backend/api/evaluation.py::list_evaluations()`  
**Opis**: Lista svih evaluacija

**Request**:
```http
GET /api/evaluation/list?collection_name=poreski_propisi_test_1
```

**Response**:
```json
{
  "evaluations": [
    {
      "id": 123,
      "version_name": "phase1_baseline",
      "collection_name": "poreski_propisi_test_1",
      "timestamp": "2026-05-20T14:00:00Z",
      "accuracy": 0.84
    }
  ],
  "total": 1
}
```

---

### 6.5 Compare Evaluations
**Endpoint**: `POST /api/evaluation/compare`  
**Fajl**: `backend/api/evaluation.py::compare_evaluations()`  
**Opis**: Poredi dve evaluacije

**Request**:
```json
{
  "evaluation_id_1": 123,
  "evaluation_id_2": 124
}
```

**Response**:
```json
{
  "evaluation_1": { /* full evaluation data */ },
  "evaluation_2": { /* full evaluation data */ },
  "improvements": {
    "accuracy_delta": 0.10,
    "speed_delta": -300,
    "gpu_delta": 0.10
  }
}
```

---

## 7. Collections

### 7.1 List Collections
**Endpoint**: `GET /api/collections`  
**Fajl**: `backend/api/collections.py::list_collections()`  
**Opis**: Lista svih Qdrant kolekcija

**Request**:
```http
GET /api/collections
```

**Response**:
```json
{
  "collections": [
    {
      "name": "poreski_propisi_test_1",
      "vectors_count": 234,
      "points_count": 234,
      "status": "active",
      "created_at": "2026-05-20T12:00:00Z",
      "size_bytes": 12345678,
      "config": {
        "vector_size": 1024,
        "distance": "Cosine"
      }
    }
  ],
  "active_collection": "poreski_propisi_test_1"
}
```

---

### 7.2 Create Collection
**Endpoint**: `POST /api/collections`  
**Fajl**: `backend/api/collections.py::create_collection()`  
**Opis**: Kreira novu kolekciju

**Request**:
```json
{
  "name": "novi_propisi",
  "description": "Novi skup poreskih propisa"
}
```

**Response**:
```json
{
  "success": true,
  "collection_name": "novi_propisi",
  "message": "Collection created successfully",
  "config": {
    "vector_size": 1024,
    "distance": "Cosine"
  }
}
```

---

### 7.3 Switch Active Collection
**Endpoint**: `PUT /api/collections/active`  
**Fajl**: `backend/api/collections.py::switch_collection()`  
**Opis**: Prebacuje na drugu kolekciju

**Request**:
```json
{
  "collection_name": "radni_zakoni"
}
```

**Response**:
```json
{
  "success": true,
  "previous_collection": "poreski_propisi_test_1",
  "active_collection": "radni_zakoni",
  "message": "Switched to collection: radni_zakoni"
}
```

---

### 7.4 Delete Collection
**Endpoint**: `DELETE /api/collections/{collection_name}`  
**Fajl**: `backend/api/collections.py::delete_collection()`  
**Opis**: Briše kolekciju

**Request**:
```http
DELETE /api/collections/radni_zakoni
```

**Response**:
```json
{
  "success": true,
  "message": "Collection deleted successfully",
  "deleted_vectors": 456
}
```

---

### 7.5 Get Collection Info
**Endpoint**: `GET /api/collections/{collection_name}`  
**Fajl**: `backend/api/collections.py::get_collection_info()`  
**Opis**: Detalji o kolekciji

**Request**:
```http
GET /api/collections/poreski_propisi_test_1
```

**Response**:
```json
{
  "name": "poreski_propisi_test_1",
  "vectors_count": 234,
  "points_count": 234,
  "indexed_vectors_count": 234,
  "status": "active",
  "optimizer_status": "ok",
  "config": {
    "params": {
      "vectors": {
        "size": 1024,
        "distance": "Cosine"
      }
    }
  }
}
```

---

## 8. Settings

### 8.1 Get Settings
**Endpoint**: `GET /api/settings`  
**Fajl**: `backend/api/settings.py::get_settings()`  
**Opis**: Trenutne postavke sistema

**Request**:
```http
GET /api/settings
```

**Response**:
```json
{
  "rag_config": {
    "chunking": {
      "strategy": "semantic",
      "chunk_size": 500,
      "chunk_overlap": 50
    },
    "search": {
      "type": "hybrid",
      "semantic_weight": 0.7,
      "bm25_weight": 0.3,
      "top_k": 10
    },
    "reranking": {
      "enabled": true,
      "top_n": 5
    }
  },
  "llm_config": {
    "name": "qwen2.5:14b",
    "temperature": 0.1,
    "top_p": 0.9,
    "max_tokens": 2048
  },
  "system_config": {
    "device": "cuda",
    "batch_size": 128
  }
}
```

---

### 8.2 Update Settings
**Endpoint**: `PUT /api/settings`  
**Fajl**: `backend/api/settings.py::update_settings()`  
**Opis**: Ažurira postavke

**Request**:
```json
{
  "rag_config": {
    "chunking": {
      "chunk_size": 600
    }
  },
  "llm_config": {
    "temperature": 0.05
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Settings updated successfully",
  "restart_required": true
}
```

---

### 8.3 Restart System
**Endpoint**: `POST /api/settings/restart`  
**Fajl**: `backend/api/settings.py::restart_system()`  
**Opis**: Restartuje sistem sa novim postavkama

**Request**:
```http
POST /api/settings/restart
```

**Response**:
```json
{
  "success": true,
  "message": "System restarting with new settings"
}
```

---

## 9. Feedback

### 9.1 Submit Feedback
**Endpoint**: `POST /api/feedback`  
**Fajl**: `backend/api/feedback.py::submit_feedback()`  
**Opis**: Šalje feedback za odgovor

**Request**:
```json
{
  "message_id": 456,
  "accuracy_rating": 5,
  "language_rating": 4,
  "chunk_relevance_rating": 5,
  "comment": "Odličan odgovor!"
}
```

**Response**:
```json
{
  "success": true,
  "feedback_id": 789,
  "message": "Feedback submitted successfully"
}
```

---

### 9.2 Get Feedback Stats
**Endpoint**: `GET /api/feedback/stats`  
**Fajl**: `backend/api/feedback.py::get_feedback_stats()`  
**Opis**: Statistika feedback-a

**Request**:
```http
GET /api/feedback/stats?collection_name=poreski_propisi_test_1
```

**Response**:
```json
{
  "total_feedback": 100,
  "avg_accuracy_rating": 4.5,
  "avg_language_rating": 4.2,
  "avg_chunk_relevance_rating": 4.7,
  "rating_distribution": {
    "5": 60,
    "4": 30,
    "3": 8,
    "2": 2,
    "1": 0
  }
}
```

---

## 10. Sessions

### 10.1 Start Session Logging
**Endpoint**: `POST /api/sessions/start`  
**Fajl**: `backend/api/sessions.py::start_session_logging()`  
**Opis**: Pokreće logovanje sesije

**Request**:
```json
{
  "session_id": "session_xyz789",
  "collection_name": "poreski_propisi_test_1"
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "session_xyz789",
  "message": "Session logging started"
}
```

---

### 10.2 Stop Session Logging
**Endpoint**: `POST /api/sessions/stop`  
**Fajl**: `backend/api/sessions.py::stop_session_logging()`  
**Opis**: Zaustavlja logovanje sesije

**Request**:
```json
{
  "session_id": "session_xyz789"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Session logging stopped",
  "total_events": 25
}
```

---

### 10.3 Download Session Log
**Endpoint**: `GET /api/sessions/download/{session_id}`  
**Fajl**: `backend/api/sessions.py::download_session_log()`  
**Opis**: Download log fajla sesije

**Request**:
```http
GET /api/sessions/download/session_xyz789
```

**Response**: JSON file download

---

## 11. Project Configuration

### 11.1 Export Configuration
**Endpoint**: `POST /api/config/export`  
**Fajl**: `backend/api/config.py::export_config()`  
**Opis**: Export projekta u JSON

**Request**:
```json
{
  "project_name": "Poreski Propisi Test 1",
  "collection_name": "poreski_propisi_test_1",
  "description": "Test obrade poreskih propisa",
  "include_pdfs": true,
  "include_test_examples": true,
  "include_evaluation_history": true
}
```

**Response**:
```json
{
  "success": true,
  "config_file": "project_configs/poreski_propisi_test_1_20260520.json",
  "download_url": "/api/config/download/poreski_propisi_test_1_20260520.json"
}
```

---

### 11.2 Import Configuration
**Endpoint**: `POST /api/config/import`  
**Fajl**: `backend/api/config.py::import_config()`  
**Opis**: Import projekta iz JSON-a

**Request**:
```http
POST /api/config/import
Content-Type: multipart/form-data

file: project_config.json
options: {
  "restore_pdfs": true,
  "restore_test_examples": true,
  "apply_model_config": true,
  "apply_rag_config": true
}
```

**Response**:
```json
{
  "success": true,
  "project_id": 1,
  "imported": {
    "pdfs": 1,
    "test_examples": 50,
    "evaluations": 2
  },
  "warnings": []
}
```

---

### 11.3 List Saved Configurations
**Endpoint**: `GET /api/config/list`  
**Fajl**: `backend/api/config.py::list_configs()`  
**Opis**: Lista sačuvanih konfiguracija

**Request**:
```http
GET /api/config/list
```

**Response**:
```json
{
  "configs": [
    {
      "filename": "poreski_propisi_test_1_20260520.json",
      "project_name": "Poreski Propisi Test 1",
      "created_at": "2026-05-20T12:00:00Z",
      "pdfs_count": 1,
      "test_examples_count": 50,
      "evaluations_count": 2,
      "best_accuracy": 0.94
    }
  ]
}
```

---

### 11.4 Compare Configurations
**Endpoint**: `POST /api/config/compare`  
**Fajl**: `backend/api/config.py::compare_configs()`  
**Opis**: Poredi dve konfiguracije

**Request**:
```json
{
  "config1": "poreski_propisi_test_1_20260520.json",
  "config2": "poreski_propisi_test_2_20260521.json"
}
```

**Response**:
```json
{
  "comparison": {
    "pdfs": {
      "added": 2,
      "removed": 0,
      "modified": 1
    },
    "test_examples": {
      "added": 10,
      "removed": 0,
      "modified": 5
    },
    "model_config": {
      "changes": [
        {
          "parameter": "llm_temperature",
          "old_value": 0.1,
          "new_value": 0.05
        }
      ]
    },
    "results": {
      "accuracy_improvement": 0.10,
      "speed_improvement": -300,
      "best_config": "config2"
    }
  }
}
```

---

### 11.5 Delete Configuration
**Endpoint**: `DELETE /api/config/{filename}`  
**Fajl**: `backend/api/config.py::delete_config()`  
**Opis**: Briše sačuvanu konfiguraciju

**Request**:
```http
DELETE /api/config/poreski_propisi_test_1_20260520.json
```

**Response**:
```json
{
  "success": true,
  "message": "Configuration deleted successfully"
}
```

---

## 12. WebSocket Endpoints

### 12.1 Training Progress
**Endpoint**: `WS /api/ws/training/{job_id}`  
**Fajl**: `backend/api/websockets.py::training_progress()`  
**Opis**: Real-time progress updates za trening

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/training/train_abc123');
```

**Messages**:
```json
{
  "job_id": "train_abc123",
  "progress": 45.5,
  "current_step": "Creating embeddings",
  "message": "Processing PDF 2 of 5"
}
```

---

### 12.2 Evaluation Progress
**Endpoint**: `WS /api/ws/evaluation/{job_id}`  
**Fajl**: `backend/api/websockets.py::evaluation_progress()`  
**Opis**: Real-time progress updates za evaluaciju

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/evaluation/eval_def456');
```

**Messages**:
```json
{
  "job_id": "eval_def456",
  "progress": 60.0,
  "current_question": 30,
  "total_questions": 50,
  "message": "Evaluating question 30 of 50"
}
```

---

### 12.3 Chat Streaming
**Endpoint**: `WS /api/ws/chat`  
**Fajl**: `backend/api/websockets.py::chat_stream()`  
**Opis**: Streaming odgovora u real-time

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/chat');
```

**Send**:
```json
{
  "message": "Kolika je stopa poreza?",
  "session_id": "session_xyz789",
  "collection_name": "poreski_propisi_test_1"
}
```

**Receive** (streaming):
```json
{
  "type": "token",
  "content": "Stopa"
}
{
  "type": "token",
  "content": " poreza"
}
{
  "type": "complete",
  "message_id": 456,
  "response_time_ms": 1250
}
```

---

## 📝 Konvencije

### HTTP Methods
- `GET`: Čitanje podataka
- `POST`: Kreiranje novih resursa
- `PUT`: Ažuriranje postojećih resursa
- `DELETE`: Brisanje resursa

### Response Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Server Error

### Naming
- Endpoints: lowercase, plural (`/api/pdfs`, `/api/collections`)
- Parameters: snake_case (`collection_name`, `pdf_id`)
- JSON fields: snake_case

---

**Status**: ✅ Aktivan  
**Ažurira se**: Tokom razvoja svake faze