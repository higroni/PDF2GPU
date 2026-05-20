# 📦 Project Configuration Management - Specifikacija

## Pregled

Sistem za čuvanje i učitavanje kompletne konfiguracije PDF2GPU projekta u jedan JSON fajl, uključujući rezultate izvršavanja po fazama.

---

## 🎯 Funkcionalnosti

### 1. **Export Project Configuration**
Čuva kompletan snapshot projekta u JSON fajl:
- Spisak PDF fajlova (sa metadata)
- Test pitanja i odgovori
- Parametri modela (RAG, LLM)
- Konfiguracioni prompt
- Rezultati evaluacija po fazama
- Timestamp i verzija

### 2. **Import Project Configuration**
Učitava prethodno sačuvanu konfiguraciju:
- Restaurira PDF fajlove
- Učitava test setove
- Primenjuje parametre
- Prikazuje istoriju rezultata

### 3. **Compare Configurations**
Poredi dve različite konfiguracije:
- Razlike u parametrima
- Razlike u rezultatima
- Vizualizacija poboljšanja/pogoršanja

---

## 📄 JSON Format

### Project Configuration File (`project_config.json`)

```json
{
  "project_info": {
    "name": "Poreski Propisi Test 1",
    "description": "Test obrade poreskih propisa sa optimizovanim parametrima",
    "collection_name": "poreski_propisi_test_1",
    "created_at": "2026-05-20T12:00:00Z",
    "updated_at": "2026-05-20T14:30:00Z",
    "version": "1.0",
    "config_version": "1.0"
  },
  
  "pdfs": [
    {
      "id": "pdf_001",
      "filename": "Godisnji_porez_na_dohodak_gradjana.pdf",
      "original_path": "data/pdfs/zakoni/Godisnji_porez_na_dohodak_gradjana.pdf",
      "size_bytes": 1234567,
      "pages": 45,
      "uploaded_at": "2026-05-20T12:05:00Z",
      "processed_at": "2026-05-20T12:06:30Z",
      "chunks_count": 234,
      "category": "zakoni",
      "metadata": {
        "language": "sr",
        "encoding": "utf-8"
      }
    }
  ],
  
  "test_examples": [
    {
      "id": "test_001",
      "question": "Kolika je stopa poreza na dohodak za prihode do 3 miliona dinara?",
      "expected_answer": "Stopa poreza na dohodak za prihode do 3 miliona dinara godišnje iznosi 10%.",
      "category": "porezi",
      "difficulty": "easy",
      "created_at": "2026-05-20T12:10:00Z"
    },
    {
      "id": "test_002",
      "question": "Koji su uslovi za oslobađanje od plaćanja poreza na dohodak?",
      "expected_answer": "Oslobođeni su od plaćanja poreza na dohodak građani čiji godišnji prihod ne prelazi 2.5 miliona dinara.",
      "category": "porezi",
      "difficulty": "medium",
      "created_at": "2026-05-20T12:11:00Z"
    }
  ],
  
  "model_config": {
    "embedding_model": {
      "name": "BAAI/bge-m3",
      "dimensions": 1024,
      "batch_size": 128,
      "device": "cuda",
      "precision": "fp16"
    },
    "llm_model": {
      "name": "qwen2.5:14b",
      "temperature": 0.1,
      "top_p": 0.9,
      "max_tokens": 2048,
      "context_window": 32768
    },
    "reranker_model": {
      "name": "BAAI/bge-reranker-v2-m3",
      "batch_size": 32,
      "device": "cuda"
    }
  },
  
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
  
  "system_prompt": {
    "template": "Ti si ekspert za poreske propise u Srbiji. Odgovaraj precizno na osnovu dostavljenih dokumenata. Ako ne znaš odgovor, reci da ne znaš.",
    "language": "sr-Latn",
    "tone": "professional"
  },
  
  "evaluation_history": [
    {
      "phase": "phase1_baseline",
      "timestamp": "2026-05-20T12:30:00Z",
      "duration_seconds": 120,
      "results": {
        "total_questions": 50,
        "correct_answers": 42,
        "accuracy": 0.84,
        "precision": 0.86,
        "recall": 0.82,
        "f1_score": 0.84,
        "avg_response_time_ms": 1500,
        "gpu_utilization_avg": 0.75
      },
      "config_snapshot": {
        "llm_temperature": 0.1,
        "chunk_size": 500,
        "top_k": 10
      }
    },
    {
      "phase": "phase2_optimized",
      "timestamp": "2026-05-20T13:00:00Z",
      "duration_seconds": 115,
      "results": {
        "total_questions": 50,
        "correct_answers": 47,
        "accuracy": 0.94,
        "precision": 0.95,
        "recall": 0.93,
        "f1_score": 0.94,
        "avg_response_time_ms": 1200,
        "gpu_utilization_avg": 0.85
      },
      "config_snapshot": {
        "llm_temperature": 0.05,
        "chunk_size": 600,
        "top_k": 15
      },
      "improvements": {
        "accuracy_delta": 0.10,
        "speed_delta": -300,
        "gpu_delta": 0.10
      }
    }
  ],
  
  "metadata": {
    "total_pdfs": 1,
    "total_test_examples": 50,
    "total_evaluations": 2,
    "best_accuracy": 0.94,
    "best_phase": "phase2_optimized",
    "tags": ["porezi", "zakoni", "optimizovano"],
    "notes": "Optimizovana konfiguracija sa boljim chunk size-om i nižom temperaturom"
  }
}
```

---

## 🔧 API Endpoints

### 1. **Export Configuration**

```http
POST /api/config/export
Content-Type: application/json

{
  "project_name": "Poreski Propisi Test 1",
  "collection_name": "poreski_propisi_test_1",
  "description": "Test obrade poreskih propisa",
  "include_pdfs": true,
  "include_test_examples": true,
  "include_evaluation_history": true
}

Response:
{
  "success": true,
  "config_file": "project_configs/poreski_propisi_test_1_20260520.json",
  "download_url": "/api/config/download/poreski_propisi_test_1_20260520.json"
}
```

### 2. **Import Configuration**

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

Response:
{
  "success": true,
  "project_id": "proj_123",
  "imported": {
    "pdfs": 1,
    "test_examples": 50,
    "evaluations": 2
  },
  "warnings": []
}
```

### 3. **List Saved Configurations**

```http
GET /api/config/list

Response:
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

### 4. **Compare Configurations**

```http
POST /api/config/compare
Content-Type: application/json

{
  "config1": "poreski_propisi_test_1_20260520.json",
  "config2": "poreski_propisi_test_2_20260521.json"
}

Response:
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

### 5. **Delete Configuration**

```http
DELETE /api/config/{filename}

Response:
{
  "success": true,
  "message": "Configuration deleted successfully"
}
```

---

## 🎨 UI Components

### 1. **Configuration Management Page**

```
┌─────────────────────────────────────────────────────────┐
│  📦 Upravljanje Konfiguracijom Projekta                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Trenutna Konfiguracija                          │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Naziv: Poreski Propisi Test 1                   │   │
│  │  Kolekcija: poreski_propisi_test_1               │   │
│  │  PDF-ovi: 1                                      │   │
│  │  Test Primeri: 50                                │   │
│  │  Evaluacije: 2                                   │   │
│  │  Najbolja Tačnost: 94%                           │   │
│  │                                                   │   │
│  │  [💾 Sačuvaj Konfiguraciju]  [📥 Učitaj]        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Sačuvane Konfiguracije                          │   │
│  ├─────────────────────────────────────────────────┤   │
│  │                                                   │   │
│  │  📄 poreski_propisi_test_1_20260520.json        │   │
│  │     • Kreiran: 20.05.2026 12:00                 │   │
│  │     • PDF-ovi: 1 | Test: 50 | Eval: 2           │   │
│  │     • Najbolja tačnost: 94%                      │   │
│  │     [📥 Učitaj] [📊 Uporedi] [🗑️ Obriši]        │   │
│  │                                                   │   │
│  │  📄 poreski_propisi_test_2_20260521.json        │   │
│  │     • Kreiran: 21.05.2026 10:30                 │   │
│  │     • PDF-ovi: 3 | Test: 75 | Eval: 3           │   │
│  │     • Najbolja tačnost: 96%                      │   │
│  │     [📥 Učitaj] [📊 Uporedi] [🗑️ Obriši]        │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 2. **Export Dialog**

```
┌─────────────────────────────────────────────────────────┐
│  💾 Sačuvaj Konfiguraciju Projekta                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Naziv Projekta:                                         │
│  [Poreski Propisi Test 1                              ] │
│                                                           │
│  Opis:                                                   │
│  [Test obrade poreskih propisa sa optimizovanim       ] │
│  [parametrima                                         ] │
│                                                           │
│  Šta želiš da sačuvaš?                                   │
│  ☑ PDF fajlovi (1)                                       │
│  ☑ Test primeri (50)                                     │
│  ☑ Parametri modela                                      │
│  ☑ RAG konfiguracija                                     │
│  ☑ System prompt                                         │
│  ☑ Istorija evaluacija (2)                               │
│                                                           │
│  Tagovi (opciono):                                       │
│  [porezi, zakoni, optimizovano                        ] │
│                                                           │
│  Napomene (opciono):                                     │
│  [Optimizovana konfiguracija sa boljim chunk size-om  ] │
│                                                           │
│  [Otkaži]                              [💾 Sačuvaj]     │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 3. **Import Dialog**

```
┌─────────────────────────────────────────────────────────┐
│  📥 Učitaj Konfiguraciju Projekta                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Izaberi fajl:                                           │
│  [📁 Izaberi JSON fajl...]                              │
│                                                           │
│  Pregled konfiguracije:                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Naziv: Poreski Propisi Test 1                   │   │
│  │  Kreiran: 20.05.2026 12:00                       │   │
│  │  PDF-ovi: 1                                      │   │
│  │  Test Primeri: 50                                │   │
│  │  Evaluacije: 2                                   │   │
│  │  Najbolja Tačnost: 94%                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  Šta želiš da učitaš?                                    │
│  ☑ Restauriraj PDF fajlove                               │
│  ☑ Učitaj test primere                                   │
│  ☑ Primeni parametre modela                              │
│  ☑ Primeni RAG konfiguraciju                             │
│  ☑ Primeni system prompt                                 │
│  ☐ Prikaži samo istoriju evaluacija                      │
│                                                           │
│  ⚠️ Upozorenje: Ovo će zameniti trenutnu konfiguraciju! │
│                                                           │
│  [Otkaži]                              [📥 Učitaj]      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 4. **Comparison View**

```
┌─────────────────────────────────────────────────────────┐
│  📊 Poređenje Konfiguracija                             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Konfiguracija 1: poreski_propisi_test_1_20260520.json  │
│  Konfiguracija 2: poreski_propisi_test_2_20260521.json  │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  PDF Fajlovi                                     │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Config 1: 1 PDF                                │   │
│  │  Config 2: 3 PDF (+2)                           │   │
│  │  • Dodato: zakon_o_radu.pdf, pravilnik_1.pdf    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Test Primeri                                    │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Config 1: 50 test primera                      │   │
│  │  Config 2: 75 test primera (+25)                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Parametri Modela                                │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  LLM Temperature:                                │   │
│  │    Config 1: 0.10                                │   │
│  │    Config 2: 0.05 (↓ 0.05)                      │   │
│  │                                                   │   │
│  │  Chunk Size:                                     │   │
│  │    Config 1: 500                                 │   │
│  │    Config 2: 600 (↑ 100)                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Rezultati                                       │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Tačnost:                                        │   │
│  │    Config 1: 84% ████████░░                     │   │
│  │    Config 2: 96% ██████████ (↑ 12%)            │   │
│  │                                                   │   │
│  │  Brzina:                                         │   │
│  │    Config 1: 1500ms ███████░░░                  │   │
│  │    Config 2: 1200ms █████░░░░░ (↓ 300ms)       │   │
│  │                                                   │   │
│  │  GPU Iskorišćenje:                               │   │
│  │    Config 1: 75% ███████░░░                     │   │
│  │    Config 2: 85% █████████░ (↑ 10%)            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  🏆 Preporuka: Config 2 je bolji (sve metrike poboljšane)│
│                                                           │
│  [Zatvori]                    [📥 Učitaj Config 2]      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow

### 1. **Kreiranje Nove Konfiguracije**

```
1. Upload PDF-ova
2. Dodaj test primere
3. Podesi parametre
4. Pokreni evaluaciju
5. Sačuvaj konfiguraciju (Export)
```

### 2. **Učitavanje Postojeće Konfiguracije**

```
1. Otvori Configuration Management
2. Izaberi sačuvanu konfiguraciju
3. Klikni "Učitaj"
4. Potvrdi opcije učitavanja
5. Sistem restaurira sve podatke
```

### 3. **Poređenje Konfiguracija**

```
1. Izaberi dve konfiguracije
2. Klikni "Uporedi"
3. Pregledaj razlike
4. Odluči koju konfiguraciju koristiti
5. Učitaj bolju konfiguraciju
```

---

## 💾 Backend Implementation

### Service: `config_service.py`

```python
class ConfigService:
    def export_config(self, project_name: str, options: dict) -> str:
        """Exportuje konfiguraciju u JSON fajl"""
        
    def import_config(self, config_file: str, options: dict) -> dict:
        """Importuje konfiguraciju iz JSON fajla"""
        
    def list_configs(self) -> List[dict]:
        """Lista svih sačuvanih konfiguracija"""
        
    def compare_configs(self, config1: str, config2: str) -> dict:
        """Poredi dve konfiguracije"""
        
    def delete_config(self, filename: str) -> bool:
        """Briše konfiguraciju"""
```

---

## 📈 Benefits

1. **Reproducibility** - Možeš tačno ponoviti test sa istim parametrima
2. **Version Control** - Praćenje evolucije konfiguracije kroz vreme
3. **Collaboration** - Deljenje konfiguracija sa drugima
4. **Comparison** - Lako poređenje različitih pristupa
5. **Backup** - Sigurnosna kopija kompletnog projekta
6. **Documentation** - Automatska dokumentacija eksperimenata

---

## ✅ Zaključak

Ovaj sistem omogućava:
- ✅ Čuvanje kompletne konfiguracije u jedan JSON fajl
- ✅ Učitavanje prethodno sačuvanih konfiguracija
- ✅ Praćenje rezultata po fazama
- ✅ Poređenje različitih konfiguracija
- ✅ Reproducibilnost eksperimenata
- ✅ Lako deljenje i backup projekata