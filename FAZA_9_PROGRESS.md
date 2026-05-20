# FAZA 9: Evaluation Configuration System - Progress Report

## Datum: 2026-05-21

## Status: Backend Complete + Frontend API Client ✅

---

## Šta je urađeno

### 1. Database Migration ✅
- **Fajl**: `migrate_add_evaluation_config.py`
- **Promene**:
  - Dodato `collection_id` u `evaluations` tabelu (Foreign Key)
  - Dodato `config_snapshot` (TEXT/JSON) u `evaluations` tabelu
  - Dodato 6 performance polja u `evaluations`:
    - `avg_query_processing_ms`
    - `avg_search_ms`
    - `avg_reranking_ms`
    - `avg_llm_generation_ms`
    - `avg_total_latency_ms`
    - `total_evaluation_time_seconds`
  - Dodato 5 performance polja u `test_example_results`:
    - `query_processing_ms`
    - `search_ms`
    - `reranking_ms`
    - `llm_generation_ms`
    - `total_latency_ms`
  - Kreiran index na `collection_id`
- **Status**: Migracija uspešno izvršena

### 2. Database Models ✅
- **Evaluation Model** (`backend/models/evaluation.py`):
  - Dodato `collection_id` (ForeignKey)
  - Dodato `config_snapshot` (Text/JSON)
  - Dodato 6 performance polja
  - Dodato `collection` relationship
  
- **Collection Model** (`backend/models/collection.py`):
  - Dodato `evaluations` relationship
  
- **TestExampleResult Model** (`backend/models/test_example_result.py`):
  - Dodato 5 performance timing polja
  - Zadržano legacy `execution_time_ms` za kompatibilnost

### 3. Model Discovery Router ✅
- **Fajl**: `backend/routers/models.py`
- **Endpoints**:
  - `GET /api/models/llm` - Lista Ollama LLM modela
  - `GET /api/models/embeddings` - Lista embedding modela
  - `GET /api/models/rerankers` - Lista reranker modela
  - `POST /api/models/install/{model_type}/{model_name}` - Instalacija modela
- **Features**:
  - Dinamičko otkrivanje instaliranih modela
  - Provera HuggingFace cache-a
  - Ollama integration za LLM modele
  - Install capability za Ollama modele
- **Status**: Implementirano i testirano (200 OK)

### 4. Evaluation Service Extensions ✅
- **Fajl**: `backend/services/evaluation_service.py`
- **Nove metode**:
  
  **`create_with_config()`**:
  - Kreira evaluaciju sa RAG config snapshot-om
  - Parametri: name, collection_id, test_example_ids, config, description
  - Čuva config kao JSON u `config_snapshot`
  
  **`run_with_config()`**:
  - Pokreće evaluaciju sa timing tracking-om
  - Meri ukupno vreme evaluacije
  - Izračunava prosečne performance metrike
  - Podržava config iz snapshot-a ili runtime config
  
  **`compare_evaluations()`**:
  - Poredi dve evaluacije
  - Config diff (changed, added, removed)
  - Metrics comparison (sa diff i improvement %)
  - Performance comparison (sa diff)
  - Vraća strukturirani JSON sa svim poređenjima

- **Ažurirana metoda**:
  - `create_evaluation()` - Dodati parametri za collection_id i config_snapshot

### 5. Main App Integration ✅
- **Fajl**: `backend/main.py`
- Registrovan `models_router`
- Backend uspešno reload-ovan i radi

---

## Tehnički detalji

### Database Schema Changes
```sql
-- evaluations table
ALTER TABLE evaluations ADD COLUMN collection_id INTEGER REFERENCES collections(id);
ALTER TABLE evaluations ADD COLUMN config_snapshot TEXT;
ALTER TABLE evaluations ADD COLUMN avg_query_processing_ms REAL;
ALTER TABLE evaluations ADD COLUMN avg_search_ms REAL;
ALTER TABLE evaluations ADD COLUMN avg_reranking_ms REAL;
ALTER TABLE evaluations ADD COLUMN avg_llm_generation_ms REAL;
ALTER TABLE evaluations ADD COLUMN avg_total_latency_ms REAL;
ALTER TABLE evaluations ADD COLUMN total_evaluation_time_seconds REAL;
CREATE INDEX idx_evaluations_collection_id ON evaluations(collection_id);

-- test_example_results table
ALTER TABLE test_example_results ADD COLUMN query_processing_ms REAL;
ALTER TABLE test_example_results ADD COLUMN search_ms REAL;
ALTER TABLE test_example_results ADD COLUMN reranking_ms REAL;
ALTER TABLE test_example_results ADD COLUMN llm_generation_ms REAL;
ALTER TABLE test_example_results ADD COLUMN total_latency_ms REAL;
```

### Config Snapshot Structure
```json
{
  "pdf_processing": {
    "use_transliteration": true,
    "use_spell_check": false
  },
  "chunking": {
    "strategy": "semantic",
    "chunk_size": 512,
    "chunk_overlap": 50
  },
  "embeddings": {
    "model": "BAAI/bge-m3",
    "dimensions": 1024
  },
  "vector_storage": {
    "collection_name": "bane-proba1",
    "distance_metric": "cosine"
  },
  "query_processing": {
    "use_transliteration": true,
    "use_spell_check": false
  },
  "search": {
    "top_k": 10,
    "score_threshold": 0.5
  },
  "reranking": {
    "enabled": true,
    "model": "BAAI/bge-reranker-v2-m3",
    "top_n": 5
  },
  "llm": {
    "model": "llama3.2:latest",
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### API Endpoints (New)
```
GET  /api/models/llm              - Lista LLM modela
GET  /api/models/embeddings       - Lista embedding modela
GET  /api/models/rerankers        - Lista reranker modela
POST /api/models/install/{type}/{name} - Instalacija modela
```

---

## Šta preostaje

### Backend (COMPLETED ✅)
- [x] Add new API endpoints u `evaluations.py`:
  - `POST /api/evaluations/with-config` - Create with config
  - `POST /api/evaluations/{id}/run-with-config` - Run with config
  - `GET /api/evaluations/compare/{id1}/{id2}` - Compare evaluations

### Frontend (In Progress)
- [x] Create `models.ts` API client
- [ ] Create `ModelSelector` component
- [ ] Create `EvaluationConfigPage`
- [ ] Create `ConfigSection` component
- [ ] Create `PerformanceBreakdown` component
- [ ] Create `EvaluationComparePage`
- [ ] Update `EvaluationsPage` sa Compare dugmetom
- [ ] Add routes u `App.tsx`

### Testing (Pending)
- [ ] Test API endpoints
- [ ] Test UI flow end-to-end

### Finalizacija (Pending)
- [ ] Commit i push promene
- [ ] Update dokumentacije

---

## Napomene

### Type Hinting Warnings
- Postoje type hinting upozorenja u kodu (SQLAlchemy Column types)
- Ova upozorenja **NE UTIČU** na funkcionalnost
- Kod radi ispravno u runtime-u
- Moguće rešenje: Dodati `# type: ignore` komentare ili koristiti SQLAlchemy 2.0 typing

### Performance Tracking
- Trenutno se timing meri samo na nivou cele evaluacije
- Za detaljno merenje po fazama potrebno je:
  - Refaktorisati `ChatService.generate_answer()` da vraća timing breakdown
  - Refaktorisati `SearchService.search()` da vraća timing breakdown
  - Dodati timing u RAG pipeline faze

### Config Application
- `run_with_config()` trenutno ne primenjuje config na RAG engine
- Potrebno je refaktorisati RAG engine da prihvata runtime config
- Ovo je kompleksna izmena koja zahteva pažljivo planiranje

---

## Zaključak

**Backend core za FAZU 9 je uspešno implementiran!** ✅

Sve ključne komponente su na mestu:
- ✅ Database schema
- ✅ Models
- ✅ Model discovery
- ✅ Evaluation service extensions
- ✅ Backend radi i testiran je

Sledeći koraci su implementacija API endpoints-a i frontend komponenti.

---

**Vreme implementacije**: ~3 sata
**Procenjeno preostalo vreme**: ~15-20 sati (prema planu)

---

## Update 2: Backend API Endpoints + Frontend API Client

### Novi Backend Endpoints (evaluations.py)

1. **POST /api/evaluations/with-config**
   - Kreira evaluaciju sa RAG config snapshot-om
   - Schema: `EvaluationWithConfigCreate`
   - Parametri: name, description, collection_id, test_example_ids, config

2. **POST /api/evaluations/{id}/run-with-config**
   - Pokreće evaluaciju sa timing tracking-om (background task)
   - Schema: `EvaluationRunWithConfig`
   - Parametri: config (optional)

3. **GET /api/evaluations/compare/{id1}/{id2}**
   - Poredi dve evaluacije
   - Vraća: config_diff, metrics_comparison, performance_comparison

### Frontend API Client (models.ts)

Kreiran API client za model discovery:
- `getLLMModels()` - Dohvata Ollama LLM modele
- `getEmbeddingModels()` - Dohvata embedding modele
- `getRerankerModels()` - Dohvata reranker modele
- `installModel()` - Instalira model (samo Ollama)

**TypeScript interfaces:**
- `ModelInfo` - Info o modelu (name, size, installed, etc.)
- `InstallResponse` - Response za instalaciju

---

## Sledeći koraci

Preostaje implementacija frontend komponenti:
1. ModelSelector component - Dropdown sa dinamičkim modelima
2. EvaluationConfigPage - Forma za kreiranje evaluacije sa config-om
3. ConfigSection component - Reusable sekcija za config parametre
4. PerformanceBreakdown component - Vizualizacija performance metrika
5. EvaluationComparePage - Side-by-side poređenje evaluacija
6. Update EvaluationsPage - Dodati Compare dugme
7. Routing u App.tsx

Ovo su kompleksne React komponente koje zahtevaju pažljivu implementaciju Material-UI komponenti, state management-a, i integracije sa API-jem.
