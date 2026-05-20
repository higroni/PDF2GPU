# 📚 MASTER REFERENCE INDEX - Centralni Indeks Svih Master Fajlova

> **🎯 SVRHA**: Ovaj fajl je centralna tačka pristupa svim master referentnim dokumentima projekta. Koristi ga kao početnu tačku za navigaciju kroz dokumentaciju.

**Poslednje ažuriranje**: 2026-05-20  
**Verzija**: 1.0

---

## 🗂️ Master Fajlovi

### 1. [MASTER_DATA_MODELS.md](MASTER_DATA_MODELS.md)
**Opis**: Katalog svih data modela u projektu  
**Sadržaj**:
- SQLite Database Models (PDF, TestExample, ChatMessage, Feedback, Evaluation, Collection, Settings, SessionLog)
- Pydantic API Models (Request/Response schemas za sve endpoints)
- Qdrant Vector Models (DocumentChunk struktura)
- Configuration Models (RAG, LLM, Embedding configs)

**Koristi za**:
- Kreiranje novih database tabela
- Definisanje API request/response struktura
- Razumevanje data flow-a kroz sistem
- Konzistentnost imenovanja polja

---

### 2. [MASTER_API_ENDPOINTS.md](MASTER_API_ENDPOINTS.md)
**Opis**: Katalog svih API endpoints sa detaljima  
**Sadržaj**:
- 12 kategorija endpoints (PDF, Training, Chat, Models, Test Examples, Evaluation, Collections, Settings, Feedback, Sessions, Config, WebSocket)
- Request/Response primeri za svaki endpoint
- Query parametri i status kodovi
- WebSocket komunikacija

**Koristi za**:
- Implementaciju API endpoints
- Frontend integraciju
- API dokumentaciju
- Testiranje endpoints

---

### 3. [MASTER_CLASSES.md](MASTER_CLASSES.md)
**Opis**: Katalog svih klasa, servisa i njihovih relacija  
**Sadržaj**:
- Backend Services (10 servisa: PDF, Training, Chat, Embedding, LLM, Collection, Evaluation, TestExample, Feedback, Config)
- RAG Engine Classes (RAGEngine, PDFProcessor, Reranker, CyrillicToLatin, SpellChecker)
- Database Models (8 SQLAlchemy modela)
- API Routers (12 routera)
- Utility Classes (WebSocketManager, JobManager, FileManager)
- Frontend Components (6 React komponenti)
- Class Relationships (dependency graph)

**Koristi za**:
- Razumevanje arhitekture sistema
- Implementaciju novih servisa
- Dependency injection
- Refactoring

---

### 4. [COLLECTION_MANAGEMENT.md](COLLECTION_MANAGEMENT.md)
**Opis**: Specifikacija za upravljanje Qdrant kolekcijama  
**Sadržaj**:
- Funkcionalnosti (kreiranje, brisanje, prebacivanje kolekcija)
- API endpoints za kolekcije
- UI komponente
- Backend implementacija (CollectionService)
- Database schema
- Workflow primeri

**Koristi za**:
- Implementaciju multi-collection podrške
- Razumevanje kako se organizuju različiti skupovi PDF-ova
- UI dizajn za collection management

---

### 5. [PROJECT_CONFIG_SPEC.md](PROJECT_CONFIG_SPEC.md)
**Opis**: Specifikacija za export/import projekata  
**Sadržaj**:
- JSON format projekta
- API endpoints za config management
- UI komponente
- Workflow za export/import
- Poređenje konfiguracija

**Koristi za**:
- Implementaciju save/load funkcionalnosti
- Backup i restore projekata
- Poređenje različitih verzija

---

## 📋 Dodatni Dokumenti

### Planski Dokumenti

#### [PLAN.md](PLAN.md)
- Kompletna arhitektura sistema
- 8 faza razvoja
- API endpoints pregled
- Struktura foldera
- UI mockups

#### [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
- Strategija testiranja po fazama
- Test struktura
- Minimum coverage requirements
- Automated test runner

#### [README.md](README.md)
- Pregled projekta
- Instalacija
- Korišćenje
- Tehnološki stack

---

## 🎯 Kako Koristiti Master Fajlove

### Tokom Razvoja

1. **Pre implementacije nove funkcionalnosti**:
   - Proveri [`MASTER_API_ENDPOINTS.md`](MASTER_API_ENDPOINTS.md) za API dizajn
   - Proveri [`MASTER_DATA_MODELS.md`](MASTER_DATA_MODELS.md) za data strukture
   - Proveri [`MASTER_CLASSES.md`](MASTER_CLASSES.md) za postojeće servise

2. **Tokom implementacije**:
   - Koristi tačna imena iz master fajlova
   - Prati konvencije imenovanja
   - Ažuriraj master fajlove ako dodaješ nove komponente

3. **Nakon implementacije**:
   - Ažuriraj relevantne master fajlove
   - Dodaj nove endpoints/modele/klase
   - Dokumentuj promene

---

## 🔄 Ažuriranje Master Fajlova

### Kada Ažurirati

- ✅ Dodavanje novog API endpointa
- ✅ Kreiranje novog data modela
- ✅ Implementacija novog servisa
- ✅ Dodavanje nove klase
- ✅ Promena strukture podataka
- ✅ Refactoring postojećih komponenti

### Kako Ažurirati

1. Otvori relevantni master fajl
2. Pronađi odgovarajuću sekciju
3. Dodaj/ažuriraj informacije
4. Ažuriraj "Poslednje ažuriranje" datum
5. Commit sa jasnom porukom

---

## 📊 Quick Reference

### Najčešće Korišćeni Modeli

| Model | Fajl | Master Referenca |
|-------|------|------------------|
| PDF | `backend/models/pdf.py` | [MASTER_DATA_MODELS.md](MASTER_DATA_MODELS.md#11-pdf-model) |
| ChatMessage | `backend/models/chat.py` | [MASTER_DATA_MODELS.md](MASTER_DATA_MODELS.md#13-chatmessage-model) |
| TestExample | `backend/models/test_example.py` | [MASTER_DATA_MODELS.md](MASTER_DATA_MODELS.md#12-testexample-model) |
| Evaluation | `backend/models/evaluation.py` | [MASTER_DATA_MODELS.md](MASTER_DATA_MODELS.md#15-evaluation-model) |

### Najčešće Korišćeni Servisi

| Servis | Fajl | Master Referenca |
|--------|------|------------------|
| PDFService | `backend/services/pdf_service.py` | [MASTER_CLASSES.md](MASTER_CLASSES.md#11-pdfservice) |
| ChatService | `backend/services/chat_service.py` | [MASTER_CLASSES.md](MASTER_CLASSES.md#13-chatservice) |
| RAGEngine | `backend/rag/rag_engine.py` | [MASTER_CLASSES.md](MASTER_CLASSES.md#21-ragengine) |
| EvaluationService | `backend/services/evaluation_service.py` | [MASTER_CLASSES.md](MASTER_CLASSES.md#17-evaluationservice) |

### Najčešće Korišćeni Endpoints

| Endpoint | Metoda | Master Referenca |
|----------|--------|------------------|
| `/api/pdfs` | POST | [MASTER_API_ENDPOINTS.md](MASTER_API_ENDPOINTS.md#11-upload-pdf) |
| `/api/chat/message` | POST | [MASTER_API_ENDPOINTS.md](MASTER_API_ENDPOINTS.md#31-send-message) |
| `/api/training/start` | POST | [MASTER_API_ENDPOINTS.md](MASTER_API_ENDPOINTS.md#21-start-training) |
| `/api/evaluation/start` | POST | [MASTER_API_ENDPOINTS.md](MASTER_API_ENDPOINTS.md#61-start-evaluation) |
| `/api/collections` | GET | [MASTER_API_ENDPOINTS.md](MASTER_API_ENDPOINTS.md#71-list-collections) |

---

## 🔍 Pretraga po Kategorijama

### Data Models
- **SQLite Models**: [`MASTER_DATA_MODELS.md#1`](MASTER_DATA_MODELS.md#1-sqlite-database-models)
- **API Models**: [`MASTER_DATA_MODELS.md#2`](MASTER_DATA_MODELS.md#2-pydantic-api-models)
- **Vector Models**: [`MASTER_DATA_MODELS.md#3`](MASTER_DATA_MODELS.md#3-qdrant-vector-models)
- **Config Models**: [`MASTER_DATA_MODELS.md#4`](MASTER_DATA_MODELS.md#4-configuration-models)

### API Endpoints
- **PDF Management**: [`MASTER_API_ENDPOINTS.md#1`](MASTER_API_ENDPOINTS.md#1-pdf-management)
- **Chat**: [`MASTER_API_ENDPOINTS.md#3`](MASTER_API_ENDPOINTS.md#3-chat-interface)
- **Evaluation**: [`MASTER_API_ENDPOINTS.md#6`](MASTER_API_ENDPOINTS.md#6-evaluation)
- **Collections**: [`MASTER_API_ENDPOINTS.md#7`](MASTER_API_ENDPOINTS.md#7-collections)
- **WebSocket**: [`MASTER_API_ENDPOINTS.md#12`](MASTER_API_ENDPOINTS.md#12-websocket-endpoints)

### Classes & Services
- **Backend Services**: [`MASTER_CLASSES.md#1`](MASTER_CLASSES.md#1-backend-services)
- **RAG Engine**: [`MASTER_CLASSES.md#2`](MASTER_CLASSES.md#2-rag-engine-classes)
- **Database Models**: [`MASTER_CLASSES.md#3`](MASTER_CLASSES.md#3-database-models)
- **API Routers**: [`MASTER_CLASSES.md#4`](MASTER_CLASSES.md#4-api-routers)
- **Utilities**: [`MASTER_CLASSES.md#5`](MASTER_CLASSES.md#5-utility-classes)
- **Frontend**: [`MASTER_CLASSES.md#6`](MASTER_CLASSES.md#6-frontend-components)
- **Relationships**: [`MASTER_CLASSES.md#7`](MASTER_CLASSES.md#7-class-relationships)

---

## 📝 Konvencije Imenovanja (Brzi Pregled)

### Database
- Tabele: `lowercase_plural` (npr. `pdfs`, `chat_messages`)
- Foreign keys: `{table}_id` (npr. `pdf_id`, `collection_id`)

### Python
- Classes: `PascalCase` (npr. `PDFService`, `ChatMessage`)
- Functions: `snake_case` (npr. `create_pdf`, `get_chat_history`)
- Private: `_snake_case` (npr. `_process_chunk`)

### API
- Endpoints: `lowercase-plural` (npr. `/api/pdfs`, `/api/test-examples`)
- Parameters: `snake_case` (npr. `collection_name`, `pdf_id`)

### JSON
- Fields: `snake_case` (npr. `collection_name`, `created_at`)

---

## 🚀 Brzi Start za Nove Developere

1. **Pročitaj**:
   - [`README.md`](README.md) - Pregled projekta
   - [`PLAN.md`](PLAN.md) - Arhitektura i faze

2. **Prouči Master Fajlove**:
   - [`MASTER_DATA_MODELS.md`](MASTER_DATA_MODELS.md) - Data strukture
   - [`MASTER_API_ENDPOINTS.md`](MASTER_API_ENDPOINTS.md) - API dizajn
   - [`MASTER_CLASSES.md`](MASTER_CLASSES.md) - Klase i servisi

3. **Počni sa Razvojem**:
   - Koristi master fajlove kao referencu
   - Prati konvencije imenovanja
   - Ažuriraj master fajlove kada dodaješ nove komponente

---

## 📞 Kontakt i Podrška

Za pitanja o master fajlovima ili dokumentaciji, konsultuj:
- [`PLAN.md`](PLAN.md) za arhitekturalna pitanja
- [`TESTING_STRATEGY.md`](TESTING_STRATEGY.md) za pitanja o testiranju
- Master fajlove za specifične implementacione detalje

---

**Status**: ✅ Aktivan  
**Održava se**: Kontinuirano tokom razvoja  
**Verzija**: 1.0