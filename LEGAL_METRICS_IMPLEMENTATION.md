# Legal Metrics Implementation - Instrukcije

## Status: U toku

Implementacija legal-specific metrika za evaluaciju RAG sistema na pravnim dokumentima na srpskom jeziku.

## Šta je urađeno:

### 1. ✅ Lemmatization Service (`backend/rag/lemmatization_service.py`)
- Koristi `classla` biblioteku za srpski jezik
- Normalizuje reči na osnovni oblik (7 padeža u srpskom)
- Primer: "obveznika" → "obveznik"

### 2. ✅ Legal Metrics Service (`backend/rag/legal_metrics.py`)
Implementirane metrike:
- **Legal Term Accuracy**: Precision, Recall, F1 za pravne termine
- **Citation Accuracy**: Tačnost citiranja članova zakona
- **Completeness Score**: Kompletnost odgovora (0-1)

### 3. ✅ Database Model Update (`backend/models/test_example_result.py`)
Dodato 5 novih kolona:
- `legal_term_precision`
- `legal_term_recall`
- `legal_term_f1`
- `citation_accuracy`
- `completeness_score`

### 4. ✅ Database Migration (`backend/alembic/versions/add_legal_metrics_columns.py`)
Alembic migracija za dodavanje novih kolona.

---

## Sledeći koraci (NAKON završetka testa):

### Korak 1: Pokreni migraciju baze
```bash
# Zaustavi backend ako radi
# Ctrl+C u terminalu

# Pokreni migraciju
alembic upgrade head

# Proveri da li su kolone dodate
# Otvori pdf2gpu.db u SQLite browseru i proveri test_example_results tabelu
```

### Korak 2: Instaliraj classla biblioteku
```bash
pip install classla
```

### Korak 3: Preuzmi srpski model za classla
```python
# Pokreni Python i izvrši:
import classla
classla.download('sr')
```

### Korak 4: Integriši legal metrics u evaluation_service.py

Potrebno je dodati:

```python
# Na vrhu fajla
from backend.rag.legal_metrics import (
    calculate_legal_term_accuracy,
    calculate_citation_accuracy,
    calculate_completeness_score
)

# U metodi _evaluate_single_example(), nakon računanja standardnih metrika:

# Calculate legal-specific metrics
legal_term_metrics = calculate_legal_term_accuracy(
    generated_answer, 
    test_example.expected_answer
)
citation_acc = calculate_citation_accuracy(
    generated_answer,
    test_example.expected_answer
)
completeness = calculate_completeness_score(
    generated_answer,
    test_example.expected_answer
)

# Dodaj u result objekat:
result.legal_term_precision = legal_term_metrics["precision"]
result.legal_term_recall = legal_term_metrics["recall"]
result.legal_term_f1 = legal_term_metrics["f1"]
result.citation_accuracy = citation_acc
result.completeness_score = completeness
```

### Korak 5: Update frontend za prikaz novih metrika

U `frontend/src/types/api.ts`:
```typescript
export interface TestExampleResult {
  // ... existing fields
  legal_term_precision?: number;
  legal_term_recall?: number;
  legal_term_f1?: number;
  citation_accuracy?: number;
  completeness_score?: number;
}
```

U `frontend/src/components/PerformanceBreakdown.tsx`:
Dodaj sekciju za Legal Metrics sa prikazom novih metrika.

### Korak 6: (Opciono) Integriši lemmatization u RAG pipeline

Za query processing u `backend/rag/rag_engine.py`:
```python
from backend.rag.lemmatization_service import LemmatizationService

# U __init__:
self.lemmatizer = LemmatizationService()

# U search metodi, pre embedding-a:
lemmatized_query = self.lemmatizer.lemmatize(query)
# Koristi lemmatized_query za pretragu
```

---

## Testiranje

Nakon implementacije:

1. Pokreni evaluaciju sa test primerima
2. Proveri da li se nove metrike računaju i čuvaju
3. Proveri prikaz u frontend-u
4. Uporedi rezultate sa i bez lemmatizacije

---

## Očekivani rezultati

- **Legal Term Accuracy**: Trebalo bi da bude visoka (>0.8) za dobre odgovore
- **Citation Accuracy**: 1.0 ako su svi citati tačni, 0.0 ako nema citata
- **Completeness Score**: 0.7-1.0 za kompletne odgovore

---

## Napomene

- Lemmatizacija može poboljšati pretragu za ~5-10%
- Legal metrics daju bolji uvid u kvalitet odgovora od standardnih metrika
- Citation accuracy je kritična za pravne dokumente

---

**Kreirao:** Bob  
**Datum:** 2026-05-21  
**Status:** Čeka završetak testa za nastavak implementacije