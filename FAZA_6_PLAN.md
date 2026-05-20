# PDF2GPU - FAZA 6: Evaluacija i Testiranje - Plan

## 🎯 Cilj Faze

Implementirati sveobuhvatno testiranje sistema sa fokusom na:
- Unit testove za sve servise
- Integration testove za API endpoints
- WebSocket testove
- E2E testove
- Performance testove
- Error handling testove

---

## 📋 Struktura Testova

```
PDF2GPU/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── phase1_backend_core/           # ✅ Već postoji
│   │   ├── __init__.py
│   │   └── test_database_models.py
│   ├── phase2_rag_engine/             # 🆕 Novi
│   │   ├── __init__.py
│   │   ├── test_pdf_processor.py
│   │   ├── test_chunking.py
│   │   ├── test_embeddings.py
│   │   └── test_reranker.py
│   ├── phase3_api_endpoints/          # 🆕 Novi
│   │   ├── __init__.py
│   │   ├── test_collections_api.py
│   │   ├── test_pdfs_api.py
│   │   └── test_search_api.py
│   ├── phase5_chat_websocket/         # 🆕 Novi
│   │   ├── __init__.py
│   │   ├── test_websocket_manager.py
│   │   ├── test_chat_service.py
│   │   └── test_chat_api.py
│   └── integration/                   # 🆕 Novi
│       ├── __init__.py
│       ├── test_full_rag_pipeline.py
│       └── test_chat_flow.py
```

---

## 🔧 Test Framework Setup

### Dependencies
```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
websockets==12.0
faker==20.1.0
```

### Pytest Configuration (pytest.ini)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    websocket: WebSocket tests
```

---

## 📝 Test Plan po Fazama

### FAZA 6.1: Setup i Fixtures (30 min)
- [x] Kreirati `conftest.py` sa zajedničkim fixtures
- [x] Setup test database
- [x] Mock Ollama API
- [x] Mock Qdrant client
- [x] Test data generators

### FAZA 6.2: RAG Engine Tests (1h)
- [ ] `test_pdf_processor.py` - PDF parsing i text extraction
- [ ] `test_chunking.py` - Chunking strategije
- [ ] `test_embeddings.py` - Embedding generation
- [ ] `test_reranker.py` - Reranking funkcionalnost

### FAZA 6.3: API Endpoint Tests (1h)
- [ ] `test_collections_api.py` - Collections CRUD
- [ ] `test_pdfs_api.py` - PDF upload i management
- [ ] `test_search_api.py` - Search funkcionalnost

### FAZA 6.4: Chat & WebSocket Tests (1h)
- [ ] `test_websocket_manager.py` - WebSocket connection management
- [ ] `test_chat_service.py` - Chat service logic
- [ ] `test_chat_api.py` - Chat API endpoints

### FAZA 6.5: Integration Tests (45 min)
- [ ] `test_full_rag_pipeline.py` - End-to-end RAG flow
- [ ] `test_chat_flow.py` - Complete chat flow

### FAZA 6.6: Coverage Report (15 min)
- [ ] Generate coverage report
- [ ] Identify untested code
- [ ] Document test results

---

## 🎯 Test Coverage Goals

- **Overall**: > 80%
- **Services**: > 90%
- **API Endpoints**: > 85%
- **Models**: > 95%
- **Utils**: > 80%

---

## 🚀 Execution Plan

### Korak 1: Install Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov httpx websockets faker
```

### Korak 2: Create Test Structure
```bash
mkdir -p tests/phase2_rag_engine
mkdir -p tests/phase3_api_endpoints
mkdir -p tests/phase5_chat_websocket
mkdir -p tests/integration
```

### Korak 3: Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test file
pytest tests/phase2_rag_engine/test_pdf_processor.py

# With markers
pytest -m unit
pytest -m integration
```

---

## 📊 Success Criteria

✅ Svi testovi prolaze
✅ Coverage > 80%
✅ Nema kritičnih bug-ova
✅ Performance testovi zadovoljavaju
✅ WebSocket testovi stabilni
✅ Integration testovi pokrivaju glavne flow-ove

---

**Status**: 🚧 U PRIPREMI
**Procenjeno vreme**: 4-5 sati
**Prioritet**: VISOK