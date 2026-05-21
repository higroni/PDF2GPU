# Best Practices: Legal RAG System for Serbian Language - Local Deployment (Part 2)

## 10. HARDWARE PREPORUKE

### 10.1 Trenutni Setup (Pretpostavka)

- GPU: RTX 3060/3070 (8-12GB VRAM)
- RAM: 16-32GB
- Storage: SSD

### 10.2 Optimizacije za Trenutni Hardware

**GPU Memory Management:**
```python
import torch

# Očistiti cache između evaluacija
torch.cuda.empty_cache()

# Koristiti gradient checkpointing za LLM
model.gradient_checkpointing_enable()

# Koristiti mixed precision
from torch.cuda.amp import autocast

with autocast():
    embeddings = model.encode(texts)
```

**RAM Optimization:**
```python
# Učitavati dokumente lazy (ne sve odjednom)
def lazy_load_documents(pdf_paths):
    for path in pdf_paths:
        yield process_pdf(path)

# Koristiti generators umesto lista
chunks = (chunk for doc in lazy_load_documents(paths) for chunk in doc.chunks)
```

### 10.3 Upgrade Path (za buduće skaliranje)

**Opcija 1: Lokalni Upgrade**
- GPU: RTX 4090 (24GB VRAM) - ~$1600
- Omogućava: Mixtral-8x7B, Llama-70B (quantized)

**Opcija 2: Cloud GPU**
- RunPod: RTX 4090 - $0.69/h
- Vast.ai: RTX 4090 - $0.50-0.80/h
- Lambda Labs: A100 (40GB) - $1.10/h

**Preporuka**: 
- Za development: Lokalni hardware
- Za production/velike evaluacije: Cloud GPU (pay-as-you-go)

---

## 11. MONITORING I DEBUGGING

### 11.1 Logging Strategy

```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/rag_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def rag_query_with_logging(query, config):
    logger.info(f"Query: {query}")
    
    start = time.time()
    query_embedding = embed_query(query)
    logger.info(f"Embedding time: {time.time() - start:.2f}s")
    
    start = time.time()
    results = search(query_embedding, top_k=20)
    logger.info(f"Search time: {time.time() - start:.2f}s")
    
    start = time.time()
    reranked = rerank(query, results, top_k=5)
    logger.info(f"Rerank time: {time.time() - start:.2f}s")
    
    start = time.time()
    answer = generate_answer(query, reranked)
    logger.info(f"Generation time: {time.time() - start:.2f}s")
    
    return answer
```

### 11.2 Performance Profiling

```python
import cProfile
import pstats

def profile_rag_pipeline():
    profiler = cProfile.Profile()
    profiler.enable()
    
    run_evaluation(test_questions, config)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

### 11.3 Error Handling

```python
class RAGError(Exception):
    """Base exception za RAG sistem"""
    pass

def safe_rag_query(query, config, max_retries=3):
    for attempt in range(max_retries):
        try:
            return rag_query(query, config)
        except Exception as e:
            logger.error(f"Error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## 12. BEST PRACTICES - CHECKLIST

### Pre-Processing
- [ ] Transliteracija ćirilice u latinicu
- [ ] Lemmatization za srpski jezik
- [ ] Očuvanje pravne strukture (članovi, stavovi)
- [ ] Metadata enrichment (document_title, article_number, etc.)
- [ ] Normalizacija referenci

### Chunking
- [ ] Semantic chunking sa respektovanjem strukture
- [ ] Chunk size: 512-768 tokena
- [ ] Overlap: 100-150 tokena
- [ ] Testiranje različitih strategija

### Embedding
- [ ] Testiranje `BAAI/bge-m3` modela
- [ ] Fine-tuning na pravnim dokumentima (opciono)
- [ ] Batch processing za efikasnost
- [ ] Dimensionality reduction (opciono)

### Search
- [ ] Hybrid search (70% semantic + 30% keyword)
- [ ] Top-k: 20 rezultata pre reranking-a
- [ ] Qdrant optimizacija (m=16, ef_construct=100)

### Reranking
- [ ] `BAAI/bge-reranker-v2-m3` model
- [ ] Top-n: 5 rezultata nakon reranking-a
- [ ] Testiranje različitih top-n vrednosti

### LLM Generation
- [ ] Mistral-7B-Instruct sa 4-bit quantization
- [ ] Temperature: 0.1 (niska kreativnost)
- [ ] Top-p: 0.9 (nucleus sampling)
- [ ] Repetition penalty: 1.1
- [ ] Optimizovan prompt za pravnu tematiku
- [ ] Response validation

### Evaluation
- [ ] Standardne metrike (BLEU, ROUGE, BERTScore)
- [ ] Legal term accuracy
- [ ] Citation accuracy
- [ ] Factual consistency
- [ ] Completeness score
- [ ] Composite legal score

### Performance
- [ ] Batch processing
- [ ] Parallel processing (max_workers=4 za GPU)
- [ ] Caching često postavljanih pitanja
- [ ] GPU memory management
- [ ] Profiling i optimizacija bottleneck-ova

### Monitoring
- [ ] Detaljno logovanje svih koraka
- [ ] Performance profiling
- [ ] Error handling sa retry logikom
- [ ] Tracking metrika tokom vremena

---

## 13. KONKRETNE PREPORUKE ZA VAŠ PROJEKAT

### 13.1 Prioriteti (Redosled implementacije)

**Visok prioritet (najveći impact):**
1. ✅ **LLM optimizacija** - Mistral-7B + 4-bit quantization
   - Očekivani gain: +15-20% tačnost, 2x brže
   - Vreme: 2-3 dana
   - Težina: Srednja

2. ✅ **Embedding model upgrade** - `BAAI/bge-m3`
   - Očekivani gain: +10-15% tačnost
   - Vreme: 1-2 dana
   - Težina: Laka

3. ✅ **Reranker upgrade** - `BAAI/bge-reranker-v2-m3`
   - Očekivani gain: +5-10% tačnost
   - Vreme: 1 dan
   - Težina: Laka

4. ✅ **Prompt engineering** za pravnu tematiku
   - Očekivani gain: +10-15% tačnost
   - Vreme: 1 dan
   - Težina: Laka

**Srednji prioritet:**
5. ✅ **Hybrid search** (semantic + keyword)
   - Očekivani gain: +5-10% tačnost
   - Vreme: 1-2 dana
   - Težina: Srednja

6. ✅ **Chunking strategy** optimizacija
   - Očekivani gain: +10-15% tačnost
   - Vreme: 1-2 dana
   - Težina: Srednja

7. ✅ **Dodatne metrike** (legal term accuracy, citation accuracy)
   - Očekivani gain: Bolja evaluacija
   - Vreme: 1 dan
   - Težina: Laka

**Nizak prioritet (ali važno za skaliranje):**
8. ✅ **Batch processing** i **parallel processing**
   - Očekivani gain: 2-3x brže evaluacije
   - Vreme: 1-2 dana
   - Težina: Srednja

9. ✅ **Caching** i **Qdrant optimizacija**
   - Očekivani gain: Brže pretraživanje
   - Vreme: 1 dan
   - Težina: Laka

10. ✅ **Fine-tuning** (opciono, ako imate vremena)
    - Očekivani gain: +20-30% tačnost
    - Vreme: 3-5 dana
    - Težina: Teška

### 13.2 Preporučeni Workflow

**Korak 1: Baseline Evaluation (1 dan)**
```bash
# Pokrenuti evaluaciju sa trenutnim setup-om na 150 pitanja
python run_evaluation.py --config baseline --questions 150

# Dokumentovati rezultate:
# - Tačnost (BLEU, ROUGE, BERTScore)
# - Brzina (avg time per question)
# - Jezička ispravnost (manual review na 20 pitanja)
```

**Korak 2: Quick Wins (3-4 dana)**
```bash
# 1. Upgrade embedding model
python upgrade_embedding.py --model BAAI/bge-m3

# 2. Upgrade reranker
python upgrade_reranker.py --model BAAI/bge-reranker-v2-m3

# 3. Optimize prompt
python optimize_prompt.py --template legal_serbian

# 4. Run evaluation
python run_evaluation.py --config optimized_v1 --questions 150
```

**Očekivani rezultat nakon Koraka 2**: +20-30% tačnost

**Korak 3: LLM Upgrade (2-3 dana)**
```bash
# 1. Download i setup Mistral-7B
python setup_mistral.py --quantization 4bit

# 2. Test na malom setu
python test_llm.py --model mistral-7b --questions 20

# 3. Full evaluation
python run_evaluation.py --config mistral_v1 --questions 150
```

**Očekivani rezultat nakon Koraka 3**: +15-20% tačnost (ukupno +35-50%)

**Korak 4: Chunking i Search Optimization (2-3 dana)**
```bash
# 1. Test različite chunking strategije
python test_chunking.py --strategies semantic,fixed,sentence

# 2. Implement hybrid search
python implement_hybrid_search.py

# 3. Full evaluation
python run_evaluation.py --config optimized_v2 --questions 150
```

**Očekivani rezultat nakon Koraka 4**: +10-15% tačnost (ukupno +45-65%)

**Korak 5: Skaliranje na 100+ Dokumenata (2-3 dana)**
```bash
# 1. Batch processing
python batch_index_documents.py --documents 100

# 2. Parallel evaluation
python run_evaluation.py --config production --questions 500 --parallel

# 3. Monitor performance
python monitor_performance.py
```

**Očekivani rezultat**: Evaluacija 500 pitanja < 2h

### 13.3 Testiranje i Validacija

**Test Set Struktura:**
```
test_questions/
├── basic/          # 30% - jednostavna pitanja
├── intermediate/   # 50% - srednje složena
├── advanced/       # 20% - složena pitanja
└── edge_cases/     # Granični slučajevi
```

**Validacija:**
1. **Automatska** (metrike): BLEU, ROUGE, BERTScore, legal metrics
2. **Manuelna** (sample): 20-30 pitanja ručno pregledati
3. **A/B testing**: Uporediti različite konfiguracije

---

## 14. ZAKLJUČAK

### 14.1 Ključne Preporuke

**Za vaš use case (pravna tematika, srpski jezik, lokalni deployment):**

1. **Embedding**: `BAAI/bge-m3` (najbolji za srpski)
2. **Reranker**: `BAAI/bge-reranker-v2-m3` (multilingual)
3. **LLM**: `Mistral-7B-Instruct` sa 4-bit quantization
4. **Chunking**: Semantic, 512-768 tokena, 100-150 overlap
5. **Search**: Hybrid (70% semantic + 30% keyword)
6. **Prompt**: Specijalizovan za pravnu tematiku, temperature=0.1

### 14.2 Očekivani Rezultati

**Baseline → Optimized:**
- Tačnost: 60-70% → **80-90%** (+20-30%)
- Brzina: 5-10s → **2-3s** (2-3x brže)
- Jezička ispravnost: 70-80% → **85-95%** (+15-20%)

**Skaliranje:**
- 100+ dokumenata: ✅ Moguće
- 500+ pitanja: ✅ < 2h evaluacija
- Lokalni hardware: ✅ 8-12GB GPU dovoljno

### 14.3 Sledeći Koraci

**Odmah:**
1. Pročitati oba dokumenta (Part 1 i Part 2)
2. Pokrenuti baseline evaluaciju na 150 pitanja
3. Dokumentovati trenutne rezultate

**Ove nedelje:**
1. Implementirati Quick Wins (Korak 2)
2. Testirati na 150 pitanja
3. Uporediti sa baseline-om

**Sledeće nedelje:**
1. LLM upgrade (Korak 3)
2. Chunking optimization (Korak 4)
3. Finalna evaluacija

**Za mesec dana:**
1. Skaliranje na 100+ dokumenata
2. Generisanje 500+ test pitanja
3. Production-ready setup

### 14.4 Dodatni Resursi

**Modeli:**
- HuggingFace: https://huggingface.co/models
- BAAI/bge-m3: https://huggingface.co/BAAI/bge-m3
- Mistral-7B: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2

**Alati:**
- Qdrant: https://qdrant.tech/documentation/
- LangChain: https://python.langchain.com/docs/
- Sentence Transformers: https://www.sbert.net/

**Zajednica:**
- r/LocalLLaMA (Reddit)
- HuggingFace Discord
- Qdrant Discord

---

## 15. KONTAKT I PODRŠKA

Ako imate pitanja ili trebate pomoć sa implementacijom:

1. **Dokumentacija**: Pročitajte oba dela (Part 1 i Part 2)
2. **Testiranje**: Pokrenite baseline evaluaciju
3. **Pitanja**: Postavite konkretna pitanja sa rezultatima testova

**Srećno sa optimizacijom! 🚀**

---

*Dokument kreiran: 2026-05-21*
*Verzija: 1.0*
*Autor: Bob (AI Assistant)*