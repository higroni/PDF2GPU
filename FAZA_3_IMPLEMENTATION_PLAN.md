# FAZA 3: Test Examples & Evaluation - Plan Implementacije

## Status: 🚀 IN PROGRESS
**Datum početka**: 2026-05-20

---

## 🎯 Cilj

Implementirati kompletnu funkcionalnost za kreiranje test pitanja, automatsku evaluaciju odgovora i generisanje metrika kvaliteta RAG sistema.

---

## 📋 Šta Već Postoji

### Backend Models ✅
- [`backend/models/test_example.py`](backend/models/test_example.py) - Model za test pitanja
- [`backend/models/evaluation.py`](backend/models/evaluation.py) - Model za evaluaciju

### Database Schema ✅
```python
TestExample:
  - id, collection_id, question, expected_answer
  - metadata, created_at

Evaluation:
  - id, test_example_id, generated_answer
  - bleu_score, rouge_score, bert_score
  - execution_time, created_at
```

---

## 🔨 Šta Treba Implementirati

### 1. Backend API Endpoints (2-3h)

#### 1.1 Test Examples CRUD
```python
POST   /api/test-examples          # Create test example
GET    /api/test-examples          # List all test examples
GET    /api/test-examples/{id}     # Get single test example
PUT    /api/test-examples/{id}     # Update test example
DELETE /api/test-examples/{id}     # Delete test example
POST   /api/test-examples/bulk     # Bulk import from JSON
GET    /api/test-examples/export   # Export to JSON
```

#### 1.2 Evaluation Endpoints
```python
POST   /api/evaluations/run/{test_example_id}  # Run single evaluation
POST   /api/evaluations/run-all                # Run all evaluations
GET    /api/evaluations                        # List evaluations
GET    /api/evaluations/{id}                   # Get evaluation details
GET    /api/evaluations/stats                  # Get statistics
DELETE /api/evaluations/{id}                   # Delete evaluation
```

### 2. Backend Services (3-4h)

#### 2.1 TestExampleService
```python
class TestExampleService:
    - create_test_example()
    - get_test_examples()
    - update_test_example()
    - delete_test_example()
    - bulk_import()
    - export_to_json()
```

#### 2.2 EvaluationService
```python
class EvaluationService:
    - run_evaluation()           # Single test
    - run_bulk_evaluation()      # All tests
    - calculate_bleu_score()
    - calculate_rouge_score()
    - calculate_bert_score()
    - get_evaluation_stats()
```

### 3. Metrics Implementation (2-3h)

#### 3.1 BLEU Score
- N-gram precision
- Brevity penalty
- Library: `nltk.translate.bleu_score`

#### 3.2 ROUGE Score
- ROUGE-1, ROUGE-2, ROUGE-L
- Library: `rouge-score`

#### 3.3 BERTScore
- Contextual embeddings similarity
- Library: `bert-score`

### 4. Frontend Components (4-5h)

#### 4.1 TestExamplesPage
```typescript
- List of test examples (table)
- Add new test example (form)
- Edit test example (modal)
- Delete test example (confirmation)
- Bulk import (JSON upload)
- Export to JSON (download)
```

#### 4.2 EvaluationPage
```typescript
- Run evaluation button
- Progress indicator
- Results table (scores, time)
- Statistics dashboard
- Charts (score distribution)
- Export results (CSV/JSON)
```

#### 4.3 Components
```typescript
- TestExampleForm.tsx
- TestExampleList.tsx
- EvaluationResults.tsx
- MetricsChart.tsx
- BulkImportDialog.tsx
```

### 5. API Integration (1-2h)

#### 5.1 API Client
```typescript
// frontend/src/api/testExamples.ts
- createTestExample()
- getTestExamples()
- updateTestExample()
- deleteTestExample()
- bulkImport()
- exportTestExamples()

// frontend/src/api/evaluations.ts
- runEvaluation()
- runBulkEvaluation()
- getEvaluations()
- getEvaluationStats()
```

### 6. Testing (2-3h)

#### 6.1 Backend Tests
```python
tests/phase3_api_endpoints/
  - test_test_examples_api.py
  - test_evaluations_api.py
  - test_metrics.py
```

#### 6.2 Integration Tests
```python
tests/integration/
  - test_evaluation_pipeline.py
```

---

## 📦 Dependencies

### Python Packages
```bash
pip install nltk rouge-score bert-score
```

### NLTK Data
```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
```

---

## 🗂️ File Structure

```
backend/
├── routers/
│   ├── test_examples.py      # NEW
│   └── evaluations.py         # NEW
├── services/
│   ├── test_example_service.py  # NEW
│   └── evaluation_service.py    # NEW
└── utils/
    └── metrics.py             # NEW

frontend/src/
├── pages/
│   ├── TestExamplesPage.tsx   # NEW
│   └── EvaluationPage.tsx     # NEW
├── components/
│   ├── TestExampleForm.tsx    # NEW
│   ├── TestExampleList.tsx    # NEW
│   ├── EvaluationResults.tsx  # NEW
│   └── MetricsChart.tsx       # NEW
└── api/
    ├── testExamples.ts        # NEW
    └── evaluations.ts         # NEW
```

---

## 📊 Timeline

### Dan 1 (4-5h)
- ✅ Plan kreiran
- [ ] Backend models review
- [ ] API endpoints (Test Examples CRUD)
- [ ] TestExampleService implementation

### Dan 2 (4-5h)
- [ ] Metrics implementation (BLEU, ROUGE, BERTScore)
- [ ] EvaluationService implementation
- [ ] API endpoints (Evaluations)

### Dan 3 (4-5h)
- [ ] Frontend TestExamplesPage
- [ ] Frontend EvaluationPage
- [ ] API integration

### Dan 4 (3-4h)
- [ ] Testing (backend + integration)
- [ ] Bug fixes
- [ ] Documentation

**Total**: 15-19 hours (~4 dana)

---

## ✅ Success Criteria

### Functional
- [ ] Korisnik može kreirati test pitanja
- [ ] Korisnik može importovati test pitanja iz JSON-a
- [ ] Sistem automatski evaluira odgovore
- [ ] Prikazuju se metrike (BLEU, ROUGE, BERTScore)
- [ ] Korisnik može exportovati rezultate

### Technical
- [ ] API endpoints rade ispravno
- [ ] Metrics se računaju tačno
- [ ] Frontend prikazuje rezultate
- [ ] Testovi prolaze (>90% coverage)

### Performance
- [ ] Single evaluation < 5s
- [ ] Bulk evaluation (10 tests) < 30s
- [ ] UI responsive

---

## 🎯 Prioriteti

### Must Have
1. Test Examples CRUD
2. Single evaluation
3. Basic metrics (BLEU, ROUGE)
4. Frontend UI

### Should Have
5. Bulk evaluation
6. BERTScore
7. Statistics dashboard
8. Export/Import

### Nice to Have
9. Charts and visualizations
10. Advanced analytics
11. Comparison between runs

---

## 📝 Notes

- Koristiti postojeće modele (`test_example.py`, `evaluation.py`)
- Metrics biblioteke su standardne (nltk, rouge-score, bert-score)
- Frontend dizajn konzistentan sa postojećim stranicama
- Testovi moraju proći pre merge-a

---

**Created**: 2026-05-20  
**Status**: Ready to start  
**Next**: Implementacija backend API endpoints