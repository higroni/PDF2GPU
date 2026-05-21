# Best Practices: Legal RAG System for Serbian Language - Local Deployment (Part 1)

## Executive Summary

Ovaj dokument sadrži najbolje prakse, preporuke i optimizacije za RAG sistem fokusiran na pravnu tematiku na srpskom jeziku, sa ciljem lokalnog deployment-a na ograničenim GPU resursima.

**Ciljevi:**
- Visoka tačnost odgovora na pravna pitanja
- Optimalna brzina izvršavanja (sesije do 2-3h)
- Jezička ispravnost na srpskom jeziku
- Skalabilnost na 100+ PDF dokumenata
- Efikasno korišćenje lokalnih GPU resursa

---

## 1. SPECIFIČNOSTI PRAVNE TEMATIKE

### 1.1 Karakteristike Pravnih Dokumenata

**Izazovi:**
- **Struktura**: Hijerarhijska organizacija (zakoni → članovi → stavovi → tačke)
- **Terminologija**: Precizna pravna terminologija koja mora biti očuvana
- **Reference**: Česte reference na druge zakone, članove, propise
- **Kontekst**: Značenje zavisi od šireg konteksta
- **Verzije**: Zakoni se menjaju - potrebno praćenje verzija

**Preporuke:**

1. **Chunk Strategy**: Koristiti **semantic chunking** sa respektovanjem strukture
   - Čuvati celinu člana/stava kao chunk gde je moguće
   - Overlap od 100-150 tokena za očuvanje konteksta
   - Max chunk size: 512-768 tokena

2. **Metadata Enrichment**: Dodati metadata za svaki chunk:
   ```python
   metadata = {
       "document_title": "Zakon o porezu na dohodak građana",
       "article_number": "Član 15",
       "section": "Stav 2",
       "effective_date": "2024-01-01",
       "document_type": "zakon",
       "legal_area": "poreski_sistem"
   }
   ```

---

## 2. SRPSKI JEZIK - SPECIFIČNOSTI

### 2.1 Ćirilica vs Latinica

**Preporuka: Unified Latin (brže, manje memorije)**
- Konvertovati sve u latinicu pri indeksiranju
- Konvertovati query u latinicu
- Generisati odgovor u latinici

**Razlog**: Manje GPU memorije, brže pretraživanje, bolji rezultati sa većinom modela

### 2.2 Lemmatization

**Problem**: Srpski jezik ima 7 padeža, što otežava exact matching

**Rešenje:**
```python
from classla import Pipeline

nlp = Pipeline('sr', processors='tokenize,pos,lemma')

def lemmatize_text(text):
    doc = nlp(text)
    return " ".join([word.lemma for sent in doc.sentences for word in sent.words])
```

---

## 3. EMBEDDING MODELI

### 3.1 Preporuke

**Top izbor: `BAAI/bge-m3`**
- Multilingual, odličan za srpski
- 1024 dimenzije
- Bolji od trenutnog mpnet modela

**Alternativa: `intfloat/multilingual-e5-large`**

### 3.2 Fine-tuning (Opciono)

```python
from sentence_transformers import SentenceTransformer, InputExample, losses

# Kreirati training dataset od pravnih dokumenata
training_data = [
    ("Šta je poreski obveznik?", "Poreski obveznik je fizičko ili pravno lice..."),
    # ... 500-1000 parova
]

model = SentenceTransformer('BAAI/bge-m3')
# Fine-tune na vašim podacima
```

**Očekivani rezultat**: +20-30% tačnost

---

## 4. RERANKING

### 4.1 Preporuka

**Model: `BAAI/bge-reranker-v2-m3`**
- Multilingual, odličan za srpski
- Bolji od ms-marco za non-English

### 4.2 Hybrid Search Strategy

```python
def hybrid_search(query, collection, top_k=20):
    # 1. Semantic search (70%)
    semantic_results = vector_search(query, top_k=top_k)
    
    # 2. Keyword search (30%) - BM25
    keyword_results = bm25_search(query, top_k=top_k)
    
    # 3. Merge sa weighted scoring
    merged = merge_results(
        semantic_results, weight=0.7,
        keyword_results, weight=0.3
    )
    
    # 4. Rerank top 20
    reranked = rerank_results(query, merged, top_k=5)
    
    return reranked
```

**Zašto hybrid?**
- Semantic: Hvata konceptualnu sličnost
- Keyword: Hvata exact matches (važno za pravne termine, brojeve članaka)

---

## 5. LLM MODELI

### 5.1 Preporuka za Lokalni Deployment

**Model: `mistralai/Mistral-7B-Instruct-v0.2`**
- 7B parametara
- ~7GB u 4-bit quantization
- Odličan za srpski
- Brz i precizan

### 5.2 Quantization

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    quantization_config=quantization_config,
    device_map="auto"
)
```

**Rezultat**: 4x manje memorije, ~10% sporije, zanemarljiv pad kvaliteta

### 5.3 Prompt Engineering

```python
LEGAL_SYSTEM_PROMPT = """Ti si AI asistent specijalizovan za srpsko zakonodavstvo i pravne propise. 

PRAVILA:
1. Odgovaraj ISKLJUČIVO na osnovu dostavljenog konteksta
2. Ako informacija nije u kontekstu, reci "Ne mogu dati precizan odgovor"
3. Uvek navedi izvor (naziv zakona, broj člana)
4. Koristi preciznu pravnu terminologiju
5. Odgovaraj na srpskom jeziku, gramatički ispravno
6. Ne izmišljaj informacije

KONTEKST:
{context}

PITANJE: {question}

ODGOVOR:"""
```

**Parametri:**
- `temperature=0.1` (niska kreativnost)
- `top_p=0.9` (nucleus sampling)
- `repetition_penalty=1.1`

---

## 6. EVALUATION METRICS

### 6.1 Dodatne Metrike za Pravnu Tematiku

**1. Legal Term Accuracy**
```python
def legal_term_accuracy(generated, reference, legal_terms_dict):
    gen_terms = extract_legal_terms(generated)
    ref_terms = extract_legal_terms(reference)
    
    precision = len(gen_terms & ref_terms) / len(gen_terms) if gen_terms else 0
    recall = len(gen_terms & ref_terms) / len(ref_terms) if ref_terms else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {"precision": precision, "recall": recall, "f1": f1}
```

**2. Citation Accuracy**
```python
def citation_accuracy(generated, reference):
    gen_citations = extract_article_references(generated)
    ref_citations = extract_article_references(reference)
    
    correct = len(gen_citations & ref_citations)
    total = len(ref_citations)
    
    return correct / total if total > 0 else 0
```

### 6.2 Composite Legal Score

```python
def legal_rag_score(generated, reference, context):
    # Standardne metrike (40%)
    standard_score = (bleu + rouge['rougeL'] + bert['f1']) / 3
    
    # Pravne metrike (60%)
    legal_score = (
        term_acc['f1'] * 0.3 +
        citation_acc * 0.2 +
        factual * 0.3 +
        completeness * 0.2
    )
    
    # Finalni score: 40% standard + 60% legal
    final_score = standard_score * 0.4 + legal_score * 0.6
    
    return final_score
```

---

## 7. OPTIMIZACIJA ZA SKALIRANJE

### 7.1 Batch Processing

```python
def batch_embed_documents(documents, batch_size=32):
    embeddings = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        batch_embeddings = embedding_model.encode(batch, batch_size=batch_size)
        embeddings.append(batch_embeddings)
    return torch.cat(embeddings)
```

### 7.2 Qdrant Optimization

```python
client.create_collection(
    collection_name="legal_documents",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    optimizers_config=OptimizersConfigDiff(
        indexing_threshold=10000,
        memmap_threshold=20000,
    ),
    hnsw_config={"m": 16, "ef_construct": 100}
)
```

### 7.3 Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_evaluation(test_questions, config, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(
            lambda q: evaluate_single_question(q, config),
            test_questions
        ))
    return results
```

**Pažnja**: `max_workers=4` za GPU operacije

---

## 8. IMPLEMENTACIONI PLAN

### FAZA 1: Optimizacija Embedding-a (1-2 dana)
1. Testirati `BAAI/bge-m3` model
2. Implementirati lemmatization
3. Dodati hybrid search
4. Benchmark

**Očekivani rezultat**: +10-15% tačnost

### FAZA 2: Optimizacija Reranking-a (1 dan)
1. Zameniti reranker sa `BAAI/bge-reranker-v2-m3`
2. Testirati različite top_k vrednosti
3. Benchmark

**Očekivani rezultat**: +5-10% tačnost

### FAZA 3: LLM Optimizacija (2-3 dana)
1. Testirati Mistral-7B-Instruct sa 4-bit quantization
2. Optimizovati prompt
3. Implementirati response validation
4. Benchmark

**Očekivani rezultat**: +15-20% tačnost, 2x brže

### FAZA 4: Chunking Strategy (1-2 dana)
1. Implementirati semantic chunking
2. Testirati različite chunk_size i overlap
3. Dodati metadata enrichment
4. Benchmark

**Očekivani rezultat**: +10-15% tačnost

### FAZA 5: Dodatne Metrike (1 dan)
1. Implementirati legal term accuracy
2. Implementirati citation accuracy
3. Kreirati composite legal score

### FAZA 6: Skaliranje (2-3 dana)
1. Implementirati batch processing
2. Optimizovati Qdrant
3. Dodati caching
4. Parallel processing
5. Testirati na 100 dokumenata

**Očekivani rezultat**: Sesije < 2h za 500+ pitanja

### FAZA 7: Fine-tuning (opciono, 3-5 dana)
1. Kreirati training dataset (500-1000 parova)
2. Fine-tune embedding model
3. Benchmark

**Očekivani rezultat**: +20-30% tačnost

---

## 9. OČEKIVANI REZULTATI

### Baseline (Trenutni Setup)
- Tačnost: ~60-70%
- Brzina: ~5-10s po pitanju
- Jezička ispravnost: ~70-80%

### Nakon Optimizacija (Faze 1-6)
- Tačnost: **80-85%** (+15-20%)
- Brzina: **2-3s po pitanju** (2-3x brže)
- Jezička ispravnost: **85-90%** (+10-15%)

### Nakon Fine-tuning-a (Faza 7)
- Tačnost: **85-90%** (+5-10%)
- Jezička ispravnost: **90-95%** (+5-10%)

### Skaliranje na 100+ Dokumenata
- Vreme indeksiranja: ~30-60 min (jednokratno)
- Vreme evaluacije (500 pitanja): **< 2h**
- Memorija: ~8-12GB GPU, ~16GB RAM

---

**Nastavak u Part 2: Hardware preporuke, monitoring, best practices checklist**