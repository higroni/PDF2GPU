# FAZA 9: Evaluation Configuration System

## Status: 📋 PLANNING → 🚀 READY TO START

**Cilj:** Implementirati kompletan sistem za konfiguraciju, pokretanje i poređenje evaluacija sa različitim RAG parametrima

---

## 🎯 Pregled Funkcionalnosti

### Ključne Komponente:
1. **Evaluation Configuration** - Kreiranje evaluacije sa custom RAG parametrima
2. **Config Snapshot** - Čuvanje kompletne konfiguracije uz evaluaciju
3. **Performance Tracking** - Praćenje vremena po fazama pipeline-a
4. **Side-by-Side Comparison** - Poređenje evaluacija sa različitim parametrima
5. **Tooltips & Documentation** - Objašnjenja za sve parametre

---

## 📊 RAG Pipeline Komponente (Tehnički Redosled)

### 1️⃣ PDF Processing (PyMuPDF)
- **Transliteracija** (Checkbox)
  - Ćirilica → Latinica
  - Avg Time: ~50ms per document

### 2️⃣ Chunking (Obavezno)
- **Strategy** (Dropdown): semantic, fixed, sentence, paragraph
- **Chunk Size** (Number): 100-2000 karaktera
- **Chunk Overlap** (Number): 0-500 karaktera
- Avg Time: ~100ms per document

### 3️⃣ Embeddings (BGE-M3 + GPU)
- **Model** (Dropdown): BAAI/bge-m3, MiniLM, E5-Large
- **Device** (Dropdown): CUDA, CPU
- **Batch Size** (Number): 64-256
- Avg Time: ~2.5s per 100 chunks (GPU)

### 4️⃣ Vector Storage (Qdrant)
- **Type** (Dropdown): Local, Remote
- **Path** (Text): ./data/qdrant_storage
- Avg Time: ~50ms per 100 vectors

### 5️⃣ Query Processing
- **Spell Check** (Checkbox)
- **Language** (Dropdown): Srpski
- Avg Time: ~20ms per query

### 6️⃣ Hybrid Search
- **Type** (Dropdown): Hybrid, Semantic, BM25
- **Semantic Weight** (Slider): 0.0-1.0
- **BM25 Weight** (Slider): 0.0-1.0
- **Top K** (Number): 1-50
- Avg Time: ~150ms per query

### 7️⃣ Reranking (BGE-reranker + GPU)
- **Model** (Dropdown): BGE-reranker-v2-m3, None
- **Top N** (Number): 1-20
- **Batch Size** (Number): 16-64
- Avg Time: ~200ms per query (GPU)

### 8️⃣ LLM Generation (Qwen2.5:14b)
- **Model** (Dropdown): qwen2.5:14b, qwen2.5:7b, llama3.1:8b
- **Temperature** (Slider): 0.0-1.0
- **Top P** (Slider): 0.0-1.0
- **Top K** (Number): 1-100
- **Max Tokens** (Number): 512-8192
- Avg Time: ~2.5s per query (14B model)

---

## 🗄️ Database Schema Changes

### Evaluation Model Extension
```python
class Evaluation(Base):
    # Existing fields...
    id, name, description, status
    total_examples, completed_examples
    avg_bleu_score, avg_rouge_l, avg_bert_score
    exact_match_percentage
    created_at, started_at, completed_at
    
    # NEW: Configuration
    collection_id = Column(Integer, ForeignKey("collections.id"))
    config_snapshot = Column(Text, nullable=False)  # JSON
    
    # NEW: Performance Metrics (averages)
    avg_query_processing_ms = Column(Integer)
    avg_search_ms = Column(Integer)
    avg_reranking_ms = Column(Integer)
    avg_llm_generation_ms = Column(Integer)
    avg_total_latency_ms = Column(Integer)
    total_evaluation_time_seconds = Column(Integer)
    
    # Relationship
    collection = relationship("Collection")
```

### TestExampleResult Model Extension
```python
class TestExampleResult(Base):
    # Existing fields...
    id, evaluation_id, test_example_id
    generated_answer
    bleu_score, rouge_1, rouge_2, rouge_l
    bert_score_precision, bert_score_recall, bert_score_f1
    exact_match, word_overlap
    execution_time_ms, context_used
    created_at
    
    # NEW: Performance Breakdown
    query_processing_ms = Column(Integer)
    search_ms = Column(Integer)
    reranking_ms = Column(Integer)
    llm_generation_ms = Column(Integer)
    total_latency_ms = Column(Integer)
```

### Config Snapshot JSON Structure
```json
{
  "pipeline": {
    "pdf_processing": {
      "transliteration_enabled": true
    },
    "chunking": {
      "strategy": "semantic",
      "chunk_size": 500,
      "chunk_overlap": 50
    },
    "embeddings": {
      "model": "BAAI/bge-m3",
      "dimensions": 1024,
      "device": "cuda",
      "batch_size": 128
    },
    "vector_storage": {
      "type": "local",
      "path": "./data/qdrant_storage"
    },
    "query_processing": {
      "spell_check_enabled": false,
      "language": "sr"
    },
    "search": {
      "type": "hybrid",
      "semantic_weight": 0.7,
      "bm25_weight": 0.3,
      "top_k": 10
    },
    "reranking": {
      "model": "BAAI/bge-reranker-v2-m3",
      "top_n": 5,
      "batch_size": 32
    },
    "llm": {
      "model": "qwen2.5:14b",
      "temperature": 0.1,
      "top_p": 0.9,
      "top_k": 40,
      "max_tokens": 2048,
      "context_window": 32768
    }
  }
}
```

---

## 🔧 Backend Implementation

### 1. Database Migration
**File:** `migrate_add_evaluation_config.py`
- Add `collection_id` to evaluations
- Add `config_snapshot` to evaluations
- Add performance fields to evaluations
- Add performance fields to test_example_results

### 2. Evaluation Service Updates
**File:** `backend/services/evaluation_service.py`

**New Methods:**
```python
async def create_with_config(
    name: str,
    description: str,
    collection_id: int,
    config_dict: dict,
    test_example_ids: List[int]
) -> Evaluation

async def run_with_config(
    evaluation_id: int
) -> Evaluation

def compare_evaluations(
    eval_id_1: int,
    eval_id_2: int
) -> dict

def clone_evaluation(
    evaluation_id: int,
    new_name: str
) -> Evaluation
```

**Timing Implementation:**
```python
async def _evaluate_single_example(...):
    timings = {}
    
    # Track each phase
    start = time.time()
    # ... query processing ...
    timings['query_processing_ms'] = (time.time() - start) * 1000
    
    start = time.time()
    # ... search ...
    timings['search_ms'] = (time.time() - start) * 1000
    
    # ... etc for all phases
    
    return result, timings
```

### 3. New API Endpoints
**File:** `backend/routers/evaluations.py`

```python
POST   /api/evaluations/create-with-config
  Body: {name, description, collection_id, config, test_example_ids}
  Response: EvaluationResponse

POST   /api/evaluations/{id}/run-with-config
  Response: EvaluationResponse (status=running)

GET    /api/evaluations/{id}/config
  Response: {config_snapshot, performance_breakdown}

POST   /api/evaluations/compare
  Body: {evaluation_ids: [1, 2]}
  Response: ComparisonResponse

POST   /api/evaluations/{id}/clone
  Body: {new_name}
  Response: EvaluationResponse

GET    /api/evaluations/{id}/performance
  Response: {timings, histogram, percentiles}
```

### 4. Response Schemas
```python
class EvaluationConfigResponse(BaseModel):
    pipeline: dict
    estimated_latency_ms: int

class PerformanceBreakdown(BaseModel):
    query_processing_ms: int
    search_ms: int
    reranking_ms: int
    llm_generation_ms: int
    total_latency_ms: int
    
class ComparisonResponse(BaseModel):
    evaluation_1: EvaluationResponse
    evaluation_2: EvaluationResponse
    config_diff: dict
    metrics_diff: dict
    performance_diff: dict
    winner: str  # "evaluation_1" or "evaluation_2"
```

---

## 🎨 Frontend Implementation

### 1. New Pages

#### EvaluationConfigPage.tsx
**Route:** `/evaluations/new`

**Components:**
- Form za kreiranje evaluacije
- Kolekcija selector
- Test pitanja selector
- Pipeline konfiguracija (8 sekcija)
- Tooltips za sve parametre
- Estimated performance
- Save/Run buttons

#### EvaluationComparePage.tsx
**Route:** `/evaluations/compare`

**Components:**
- Selector za 2 evaluacije
- Side-by-side prikaz
- Config diff highlighting
- Metrics comparison
- Performance comparison
- Winner indicator

### 2. Updated Pages

#### EvaluationsPage.tsx
**Updates:**
- Dodaj "Uporedi" dugme
- Dodaj "Kloniraj" dugme
- Prikaži config snapshot u details
- Prikaži performance breakdown

### 3. New Components

#### ConfigSection.tsx
```typescript
interface ConfigSectionProps {
  title: string;
  icon: ReactNode;
  tooltip: string;
  children: ReactNode;
  estimatedTime?: string;
}
```

#### PerformanceBreakdown.tsx
```typescript
interface PerformanceBreakdownProps {
  timings: {
    query_processing_ms: number;
    search_ms: number;
    reranking_ms: number;
    llm_generation_ms: number;
    total_latency_ms: number;
  };
  showHistogram?: boolean;
}
```

#### ComparisonView.tsx
```typescript
interface ComparisonViewProps {
  evaluation1: Evaluation;
  evaluation2: Evaluation;
  configDiff: ConfigDiff;
  metricsDiff: MetricsDiff;
  performanceDiff: PerformanceDiff;
}
```

### 4. API Client Updates
**File:** `frontend/src/api/evaluations.ts`

```typescript
export const createEvaluationWithConfig = async (data: {
  name: string;
  description: string;
  collection_id: number;
  config: PipelineConfig;
  test_example_ids: number[];
}): Promise<Evaluation>

export const runEvaluationWithConfig = async (
  evaluationId: number
): Promise<Evaluation>

export const compareEvaluations = async (
  evaluationIds: [number, number]
): Promise<ComparisonResponse>

export const cloneEvaluation = async (
  evaluationId: number,
  newName: string
): Promise<Evaluation>

export const getEvaluationPerformance = async (
  evaluationId: number
): Promise<PerformanceBreakdown>
```

---

## 📋 Tooltips Content

### Chunking
- **Strategy:** "Način deljenja teksta na delove. Semantic deli po semantičkim granicama, Fixed po fiksnoj veličini."
- **Chunk Size:** "Veličina svakog dela teksta. Optimalno: 300-800 karaktera. Manji = precizniji, veći = brži."
- **Overlap:** "Preklapanje između delova. Sprečava gubitak konteksta. Optimalno: 10-20% chunk size-a."

### Embeddings
- **Model:** "Model za konverziju teksta u vektore. BGE-M3 je najbolji za multilingual, MiniLM najbrži."
- **Device:** "CUDA koristi GPU (10-50x brže), CPU radi svuda ali sporije."
- **Batch Size:** "Broj chunks-a procesiranih odjednom. Veći = brže, ali više GPU memorije."

### Search
- **Type:** "Hybrid kombinuje semantic i keyword search. Semantic samo embeddings, BM25 samo keywords."
- **Semantic Weight:** "Težina semantic search-a u hybrid modu. Veća = više semantičke sličnosti."
- **BM25 Weight:** "Težina keyword search-a. Semantic + BM25 mora biti = 1.0."
- **Top K:** "Broj rezultata za reranking. Optimalno: 5-20."

### Reranking
- **Model:** "Model za preciznije rangiranje rezultata. BGE-reranker najbolji, None isključuje reranking."
- **Top N:** "Broj rezultata nakon reranking-a. Mora biti ≤ Top K. Optimalno: 3-7."

### LLM
- **Model:** "LLM za generisanje odgovora. 14B najbolji kvalitet, 7B brži."
- **Temperature:** "Kontroliše kreativnost. 0.0 = deterministički, 1.0 = kreativno. Za QA: 0.0-0.3."
- **Top P:** "Nucleus sampling. Kontroliše raznovrsnost tokena. Optimalno: 0.8-0.95."
- **Top K:** "Broj top tokena za sampling. Manji = konzervativnije. Optimalno: 20-50."
- **Max Tokens:** "Maksimalna dužina odgovora. Optimalno za QA: 512-2048."

---

## 📊 Implementation Timeline

### Faza 1: Backend Core (Dan 1-2, 8-10h)
1. ✅ Database migration
2. ✅ Extend Evaluation model
3. ✅ Extend TestExampleResult model
4. ✅ Update evaluation_service
5. ✅ Add timing tracking
6. ✅ Implement create_with_config
7. ✅ Implement run_with_config
8. ✅ Implement compare_evaluations
9. ✅ Add new API endpoints
10. ✅ Test API

### Faza 2: Frontend Core (Dan 3-4, 8-10h)
11. ✅ Create EvaluationConfigPage
12. ✅ Create ConfigSection component
13. ✅ Add tooltips
14. ✅ Add form validation
15. ✅ Create PerformanceBreakdown component
16. ✅ Create EvaluationComparePage
17. ✅ Create ComparisonView component
18. ✅ Update EvaluationsPage
19. ✅ Add API client methods
20. ✅ Test UI flow

### Faza 3: Integration & Polish (Dan 5, 4-6h)
21. ✅ End-to-end testing
22. ✅ Performance optimization
23. ✅ UI/UX improvements
24. ✅ Documentation
25. ✅ Bug fixing

**Total:** 20-26 sati (5 dana)

---

## ✅ Success Criteria

### Functionality
- [ ] Mogu kreirati evaluaciju sa custom config-om
- [ ] Config se snima kao JSON snapshot
- [ ] Evaluacija koristi snapshot config
- [ ] Performance se prati po fazama
- [ ] Mogu uporediti 2 evaluacije
- [ ] Vidim config diff
- [ ] Vidim metrics diff
- [ ] Vidim performance diff
- [ ] Mogu klonirati evaluaciju
- [ ] Tooltips objašnjavaju sve parametre

### Performance
- [ ] Timing tracking < 5ms overhead
- [ ] Config snapshot < 10KB
- [ ] Comparison API < 500ms
- [ ] UI responsive

### UX
- [ ] Intuitivna forma
- [ ] Jasni tooltips
- [ ] Validacija input-a
- [ ] Error handling
- [ ] Loading states
- [ ] Success feedback

---

## 🎯 Deliverables

1. **Database Migration** - `migrate_add_evaluation_config.py`
2. **Backend Service** - Updated `evaluation_service.py`
3. **API Endpoints** - Updated `evaluations.py` router
4. **Frontend Pages** - `EvaluationConfigPage.tsx`, `EvaluationComparePage.tsx`
5. **Components** - `ConfigSection.tsx`, `PerformanceBreakdown.tsx`, `ComparisonView.tsx`
6. **API Client** - Updated `evaluations.ts`
7. **Documentation** - Tooltips, README updates
8. **Tests** - Unit & integration tests

---

## 📝 Notes

- Config snapshot omogućava reproducibilnost
- Performance tracking pomaže optimizaciji
- Side-by-side comparison olakšava eksperimentisanje
- Tooltips smanjuju learning curve
- Cloning ubrzava iteraciju

---

**Created:** 2026-05-20
**Status:** Ready to start
**Priority:** HIGH - Ključna funkcionalnost za RAG optimizaciju