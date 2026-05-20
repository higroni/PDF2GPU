# 📋 PDF2GPU - Plan Implementacije

> **🧪 VAŽNO**: Svaka faza razvoja uključuje automatizovane testove koji se moraju izvršiti i proći pre prelaska na sledeću fazu. Pogledaj [`TESTING_STRATEGY.md`](TESTING_STRATEGY.md) za detalje.

**Datum**: 19. maj 2026.
**Verzija**: 1.2 (Ažurirano - dodato poređenje verzija)
**Status**: ✅ Odobreno - Spremno za implementaciju

---

## 🎯 Pregled Projekta

**Naziv**: PDF2GPU
**Opis**: Web aplikacija za RAG sistem sa GPU optimizacijom, management PDF-ova, chat interfejsom, poređenjem verzija i feedback sistemom

**Glavna Namena**: Testiranje obrade skupova PDF fajlova na srpskom jeziku (zakoni, procedure, pravilnici) i treniranje modela za kvalitetno odgovaranje na pitanja

**Tehnološki Stack**:
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Material-UI
- **Jezik UI**: Srpski (latinica)
- **Baza**: SQLite (feedback, test primeri, verzije) + Qdrant (vektori)
- **RAG Engine**: Postojeći optimizovani kod iz PDFpropisi
- **Deployment**: Docker + Docker Compose (lokalno)
- **Auth**: Single-user (bez login sistema)

---

## 🏗️ Arhitektura Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         PDF2GPU SISTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FRONTEND (React)                      │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  1. PDF Management Page                                  │   │
│  │     • Upload PDF                                         │   │
│  │     • List/Delete PDFs                                   │   │
│  │     • Trigger Retraining                                 │   │
│  │                                                           │   │
│  │  2. Chat Interface                                       │   │
│  │     • Message history                                    │   │
│  │     • Real-time responses                                │   │
│  │     • LLM model selector (Ollama models)                 │   │
│  │     • Feedback buttons (👍/👎)                           │   │
│  │                                                           │   │
│  │  3. Test Examples Management                             │   │
│  │     • Add/Edit/Delete test Q&A pairs                     │   │
│  │     • Import/Export JSON                                 │   │
│  │     • Run evaluation (sa progress)                       │   │
│  │     • Version comparison                                 │   │
│  │                                                           │   │
│  │  4. Settings Panel                                       │   │
│  │     • RAG Parameters (temperature, chunk_size, etc.)     │   │
│  │     • Model selection                                    │   │
│  │     • Apply & Restart (sa progress)                      │   │
│  │                                                           │   │
│  │  5. Feedback Panel                                       │   │
│  │     • Rate answer accuracy                               │   │
│  │     • Rate language quality                              │   │
│  │     • Rate chunk relevance                               │   │
│  │                                                           │   │
│  │  6. Session Logging                                      │   │
│  │     • Enable/Disable logging                             │   │
│  │     • Download session logs                              │   │
│  │                                                           │   │
│  │  7. Project Configuration Management                     │   │
│  │     • Export project config (JSON)                       │   │
│  │     • Import project config                              │   │
│  │     • Compare configurations                             │   │
│  │     • View evaluation history                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   BACKEND (FastAPI)                      │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  API Endpoints:                                          │   │
│  │                                                           │   │
│  │  /api/pdfs                                               │   │
│  │    • POST   - Upload PDF                                 │   │
│  │    • GET    - List PDFs                                  │   │
│  │    • DELETE - Remove PDF                                 │   │
│  │                                                           │   │
│  │  /api/training                                           │   │
│  │    • POST   - Trigger retraining                         │   │
│  │    • GET    - Training status                            │   │
│  │    • WS     - Progress updates                           │   │
│  │                                                           │   │
│  │  /api/chat                                               │   │
│  │    • POST   - Send message                               │   │
│  │    • WS     - WebSocket for streaming                    │   │
│  │                                                           │   │
│  │  /api/models                                             │   │
│  │    • GET    - List available Ollama models               │   │
│  │                                                           │   │
│  │  /api/test-examples                                      │   │
│  │    • GET    - List test examples                         │   │
│  │    • POST   - Add test example                           │   │
│  │    • PUT    - Update test example                        │   │
│  │    • DELETE - Remove test example                        │   │
│  │    • POST   - Import from JSON                           │   │
│  │    • GET    - Export to JSON                             │   │
│  │                                                           │   │
│  │  /api/evaluation                                         │   │
│  │    • POST   - Run evaluation                             │   │
│  │    • WS     - Progress updates                           │   │
│  │    • GET    - Get results                                │   │
│  │    • GET    - List all versions                          │   │
│  │                                                           │   │
│  │  /api/comparison                                         │   │
│  │    • POST   - Compare versions                           │   │
│  │    • GET    - Get comparison results                     │   │
│  │                                                           │   │
│  │  /api/settings                                           │   │
│  │    • GET    - Get current settings                       │   │
│  │    • PUT    - Update settings                            │   │
│  │    • POST   - Restart with new settings                 │   │
│  │                                                           │   │
│  │  /api/feedback                                           │   │
│  │    • POST   - Submit feedback                            │   │
│  │    • GET    - Get feedback stats                         │   │
│  │                                                           │   │
│  │  /api/sessions                                           │   │
│  │    • POST   - Start/Stop logging                         │   │
│  │    • GET    - Download session log                       │   │
│  │                                                           │   │
│  │  /api/config                                             │   │
│  │    • POST   - Export project configuration               │   │
│  │    • POST   - Import project configuration               │   │
│  │    • GET    - List saved configurations                  │   │
│  │    • POST   - Compare configurations                     │   │
│  │    • DELETE - Delete configuration                       │   │
│  │                                                           │   │
│  │  /api/collections                                        │   │
│  │    • GET    - List Qdrant collections                    │   │
│  │    • POST   - Create new collection                      │   │
│  │    • DELETE - Delete collection                          │   │
│  │    • PUT    - Switch active collection                   │   │
│  │                                                           │   │
│  │  /api/progress                                           │   │
│  │    • WS     - Real-time progress updates                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    RAG ENGINE                            │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  • PDF Processing (PyMuPDF)                              │   │
│  │  • Transliteration (Cyr→Lat)                            │   │
│  │  • Chunking (Semantic)                                   │   │
│  │  • Embeddings (BGE-M3 + GPU)                            │   │
│  │  • Vector Storage (Qdrant - multi-collection support)   │   │
│  │  • Hybrid Search (70%/30%)                               │   │
│  │  • Reranking (BGE-reranker + GPU)                       │   │
│  │  • LLM Generation (Qwen2.5:14b)                         │   │
│  │  • Spell Checking (Dictionary)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  DATA STORAGE                            │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  • SQLite (feedback, sessions, settings, test examples,  │   │
│  │            evaluation versions)                          │   │
│  │  • Qdrant (vector embeddings)                            │   │
│  │  • File System (uploaded PDFs, test JSONs, results)     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Struktura Foldera

```
PDF2GPU/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py                  # Konfiguracija
│   │   ├── database.py                # SQLite setup
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── pdfs.py               # PDF management endpoints
│   │   │   ├── training.py           # Training endpoints (sa progress)
│   │   │   ├── chat.py               # Chat endpoints
│   │   │   ├── models.py             # Ollama models endpoints
│   │   │   ├── test_examples.py      # Test examples management
│   │   │   ├── evaluation.py         # Evaluation endpoints (sa progress)
│   │   │   ├── comparison.py         # Version comparison endpoints
│   │   │   ├── settings.py           # Settings endpoints
│   │   │   ├── feedback.py           # Feedback endpoints
│   │   │   ├── sessions.py           # Session logging endpoints
│   │   │   └── progress.py           # Progress WebSocket endpoint
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── pdf.py                # PDF model
│   │   │   ├── chat.py               # Chat message model
│   │   │   ├── test_example.py       # Test example model
│   │   │   ├── evaluation.py         # Evaluation result model
│   │   │   ├── version.py            # Version model
│   │   │   ├── comparison.py         # Comparison result model
│   │   │   ├── feedback.py           # Feedback model
│   │   │   ├── session.py            # Session model
│   │   │   └── progress.py           # Progress tracking model
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_processor.py      # PDF processing
│   │   │   ├── rag_engine.py         # RAG sistem
│   │   │   ├── ollama_service.py     # Ollama models integration
│   │   │   ├── training_service.py   # Training orchestration (sa progress)
│   │   │   ├── test_service.py       # Test examples management
│   │   │   ├── evaluation_service.py # Evaluation runner (sa progress)
│   │   │   ├── comparison_service.py # Version comparison
│   │   │   ├── feedback_service.py   # Feedback processing
│   │   │   ├── session_service.py    # Session logging
│   │   │   └── progress_service.py   # Progress tracking & broadcasting
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── cyrillic_to_latin.py  # Transliteracija
│   │       ├── spell_checker.py      # Spell checking
│   │       └── validators.py         # Input validation
│   │
│   ├── data/
│   │   ├── pdfs/                     # Uploaded PDFs
│   │   ├── test_examples/            # Test Q&A JSON files
│   │   ├── evaluation_results/       # Evaluation results (versioned)
│   │   ├── comparisons/              # Comparison results
│   │   ├── qdrant_data/              # Qdrant storage
│   │   └── feedback.db               # SQLite database
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── App.tsx                   # Main app
│   │   ├── index.tsx                 # Entry point
│   │   │
│   │   ├── components/
│   │   │   ├── Common/
│   │   │   │   ├── ProgressBar.tsx
│   │   │   │   ├── ProgressDialog.tsx
│   │   │   │   └── LoadingSpinner.tsx
│   │   │   │
│   │   │   ├── PDFManagement/
│   │   │   │   ├── PDFList.tsx
│   │   │   │   ├── PDFUpload.tsx
│   │   │   │   └── RetrainingButton.tsx (sa progress)
│   │   │   │
│   │   │   ├── TestExamples/
│   │   │   │   ├── TestExamplesList.tsx
│   │   │   │   ├── TestExampleForm.tsx
│   │   │   │   ├── TestExampleImport.tsx
│   │   │   │   ├── TestExampleExport.tsx
│   │   │   │   ├── EvaluationRunner.tsx (sa progress)
│   │   │   │   ├── VersionSelector.tsx
│   │   │   │   └── VersionComparison.tsx
│   │   │   │
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── ModelSelector.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   └── FeedbackButtons.tsx
│   │   │   │
│   │   │   ├── Settings/
│   │   │   │   ├── SettingsPanel.tsx
│   │   │   │   ├── RAGParameters.tsx
│   │   │   │   └── ModelSelector.tsx
│   │   │   │
│   │   │   ├── Feedback/
│   │   │   │   ├── FeedbackForm.tsx
│   │   │   │   ├── AccuracyRating.tsx
│   │   │   │   ├── LanguageRating.tsx
│   │   │   │   └── ChunkRating.tsx
│   │   │   │
│   │   │   └── Session/
│   │   │       ├── SessionControls.tsx
│   │   │       └── SessionDownload.tsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                # API client
│   │   │   └── websocket.ts          # WebSocket client
│   │   │
│   │   ├── types/
│   │   │   ├── pdf.ts
│   │   │   ├── test_example.ts
│   │   │   ├── evaluation.ts
│   │   │   ├── version.ts
│   │   │   ├── comparison.ts
│   │   │   ├── chat.ts
│   │   │   ├── settings.ts
│   │   │   ├── feedback.ts
│   │   │   └── progress.ts
│   │   │
│   │   ├── i18n/
│   │   │   ├── sr.json              # Srpski prevodi
│   │   │   └── index.ts             # i18n setup
│   │   │
│   │   └── styles/
│   │       └── global.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── PLAN.md (ovaj fajl)
```

---

## 🎨 UI/UX Dizajn

### 1. PDF Management Page

```
┌─────────────────────────────────────────────────────────────┐
│  PDF2GPU - Document Management                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📁 Upload New PDF                                   │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Drag & Drop or Click to Upload             │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  [Upload] [Cancel]                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📚 Current Documents (3)                            │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ 📄 Godisnji_porez_na_dohodak_gradjana.pdf    │  │   │
│  │  │    Size: 2.5 MB | Uploaded: 2026-05-15       │  │   │
│  │  │    [View] [Delete]                            │  │   │
│  │  ├───────────────────────────────────────────────┤  │   │
│  │  │ 📄 Zakon_o_porezu_na_dodatu_vrednost.pdf     │  │   │
│  │  │    Size: 3.1 MB | Uploaded: 2026-05-16       │  │   │
│  │  │    [View] [Delete]                            │  │   │
│  │  ├───────────────────────────────────────────────┤  │   │
│  │  │ 📄 Poreski_propisi_2026.pdf                  │  │   │
│  │  │    Size: 1.8 MB | Uploaded: 2026-05-17       │  │   │
│  │  │    [View] [Delete]                            │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🔄 Retraining                                       │   │
│  │  Last training: 2026-05-17 14:30                    │   │
│  │  Status: ✅ Ready                                    │   │
│  │  [Start Retraining]                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Chat Interface

```
┌─────────────────────────────────────────────────────────────┐
│  PDF2GPU - Razgovor                           [⚙️ Podešavanja]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🤖 Model: [qwen2.5:14b ▼]  [Osveži Listu]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  💬 Istorija Razgovora                               │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ 👤 Korisnik (14:25)                           │  │   │
│  │  │ Da li imam pravo na poresku olakšicu ako     │  │   │
│  │  │ imam 32 godine?                               │  │   │
│  │  ├───────────────────────────────────────────────┤  │   │
│  │  │ 🤖 Asistent (14:25) [qwen2.5:14b]            │  │   │
│  │  │ Da, imate pravo na poresku olakšicu. Prema   │  │   │
│  │  │ članu 15. Zakona...                           │  │   │
│  │  │                                                │  │   │
│  │  │ 📚 Izvori:                                    │  │   │
│  │  │ • Clan 15. - Poreski obveznik... (0.89)      │  │   │
│  │  │ • Umanjenje poreza... (0.85)                 │  │   │
│  │  │                                                │  │   │
│  │  │ [👍 Korisno] [👎 Nije korisno] [📝 Oceni]    │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Ukucajte vaše pitanje...                            │   │
│  │  [Pošalji]                                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [📝 Logovanje Sesije: UKLJUČENO] [💾 Preuzmi Log]          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Napomena**: Model selector prikazuje sve trenutno dostupne modele u Ollama. Korisnik može da promeni model u bilo kom trenutku, a promena se primenjuje na sledeće poruke. Svaki odgovor prikazuje koji model je korišćen.

---

### 3. Settings Panel

```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🤖 Model Settings                                   │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ Model: [qwen2.5:14b ▼]                       │  │   │
│  │  │ Temperature: [0.1] ━━━━━━━━━━━━━━━━━━━━━━━  │  │   │
│  │  │ Max Tokens: [500]                             │  │   │
│  │  │ Context Window: [8192]                        │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📄 Chunking Settings                                │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ Chunk Size: [500] characters                  │  │   │
│  │  │ Chunk Overlap: [50] characters                │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🔍 Search Settings                                  │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ Semantic Weight: [0.7] ━━━━━━━━━━━━━━━━━━━━  │  │   │
│  │  │ BM25 Weight: [0.3] ━━━━━━━━━━━━━━━━━━━━━━━━  │  │   │
│  │  │ Top K Results: [5]                            │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  💬 Prompt Settings                                  │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ System Prompt:                                │  │   │
│  │  │ ┌─────────────────────────────────────────┐   │  │   │
│  │  │ │ Ti si ekspert za poreske propise...     │   │  │   │
│  │  │ │                                          │   │  │   │
│  │  │ └─────────────────────────────────────────┘   │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [Apply Settings] [Restart System] [Reset to Defaults]      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```


### 2. Test Examples Management Page

```
┌─────────────────────────────────────────────────────────────┐
│  PDF2GPU - Upravljanje Test Primerima                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ➕ Dodaj Novi Test Primer                           │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ Pitanje:                                      │  │   │
│  │  │ ┌─────────────────────────────────────────┐   │  │   │
│  │  │ │ Da li imam pravo na poresku olakšicu?   │   │  │   │
│  │  │ └─────────────────────────────────────────┘   │  │   │
│  │  │                                               │  │   │
│  │  │ Tačan Odgovor:                                │  │   │
│  │  │ ┌─────────────────────────────────────────┐   │  │   │
│  │  │ │ Da, imate pravo prema članu 15...       │   │  │   │
│  │  │ │                                          │   │  │   │
│  │  │ └─────────────────────────────────────────┘   │  │   │
│  │  │                                               │  │   │
│  │  │ [Sačuvaj] [Otkaži]                            │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📋 Test Primeri (25)                                │   │
│  │  [Import JSON] [Export JSON] [Pokreni Evaluaciju]   │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ 1. Da li imam pravo na poresku olakšicu?     │  │   │
│  │  │    Odgovor: Da, imate pravo prema članu...   │  │   │
│  │  │    [Uredi] [Obriši] [Test]                   │  │   │
│  │  ├───────────────────────────────────────────────┤  │   │
│  │  │ 2. Koliko iznosi porez na dohodak?           │  │   │
│  │  │    Odgovor: Porez na dohodak iznosi 10%...   │  │   │
│  │  │    [Uredi] [Obriši] [Test]                   │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📊 Poslednja Evaluacija                             │   │
│  │  Datum: 17.05.2026 15:45                            │   │
│  │  Verzija: v1.2.3                                    │   │
│  │  Tačnost: 92% (23/25)                               │   │
│  │  Prosečno vreme: 4.2s                               │   │
│  │  [Prikaži Detalje] [Pokreni Ponovo]                 │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ Progress: ████████████████░░░░ 80%          │    │   │
│  │  │ Test: 20/25 - Trenutno pitanje...           │    │   │
│  │  │ Vreme: 1:20 / ~1:40                         │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🔄 Poređenje Verzija                                │   │
│  │  Verzija A: [v1.2.3 ▼]  Verzija B: [v1.1.0 ▼]      │   │
│  │  [Uporedi Verzije]                                   │   │
│  │                                                       │   │
│  │  📊 Rezultati Poređenja:                             │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ Pitanje 1: Da li imam pravo na olakšicu?     │  │   │
│  │  │                                               │  │   │
│  │  │ v1.2.3: Da, imate pravo prema članu 15...    │  │   │
│  │  │ Tačnost: ✅ | Vreme: 4.2s                    │  │   │
│  │  │                                               │  │   │
│  │  │ v1.1.0: Da, imate pravo na olakšicu...       │  │   │
│  │  │ Tačnost: ✅ | Vreme: 5.8s                    │  │   │
│  │  │                                               │  │   │
│  │  │ Poboljšanje: ⬆️ 27% brže                     │  │   │
│  │  ├───────────────────────────────────────────────┤  │   │
│  │  │ Pitanje 2: Koliko iznosi porez?              │  │   │
│  │  │ ...                                           │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  📈 Ukupna Statistika:                               │   │
│  │  • Tačnost: v1.2.3 (92%) vs v1.1.0 (88%)            │   │
│  │  • Brzina: v1.2.3 (4.2s) vs v1.1.0 (5.8s)           │   │
│  │  • Poboljšanje: +4% tačnost, +27% brzina            │   │
│  │                                                       │   │
│  │  [Preuzmi Izveštaj] [Prikaži Grafikon]              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---
---

### 4. Feedback Panel

```
┌─────────────────────────────────────────────────────────────┐
│  📝 Provide Feedback                                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Question: "Da li imam pravo na poresku olakšicu?"          │
│  Answer: "Da, imate pravo na poresku olakšicu..."           │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ✅ Answer Accuracy                                  │   │
│  │  Is the answer correct?                              │   │
│  │  ○ Correct    ○ Incorrect                            │   │
│  │  Comment (optional): ___________________________     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🔤 Language Quality                                 │   │
│  │  Is the language correct?                            │   │
│  │  ○ Good    ○ Has errors                              │   │
│  │  If errors, select type:                             │   │
│  │  ☐ Spelling    ☐ Grammar    ☐ Mixed script          │   │
│  │  Correction (optional): _________________________    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📚 Source Relevance                                 │   │
│  │  Rate each source:                                   │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ 1. Clan 15. - Poreski obveznik... (0.89)     │  │   │
│  │  │    ○ Relevant    ○ Not Relevant               │  │   │
│  │  ├───────────────────────────────────────────────┤  │   │
│  │  │ 2. Umanjenje poreza... (0.85)                │  │   │
│  │  │    ○ Relevant    ○ Not Relevant               │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [Submit Feedback] [Cancel]                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Tehnička Implementacija

### Backend (FastAPI)

**Ključne Komponente**:

1. **PDF Management Service**
   - Upload handling (multipart/form-data)
   - File validation (PDF format, size limits)
   - Storage management
   - Deletion with cleanup

2. **Training Service**
   - Background task za retraining
   - Progress tracking
   - Status updates via WebSocket
   - Error handling

3. **RAG Engine Service**
   - Wrapper oko postojećeg koda
   - Dynamic parameter loading
   - GPU resource management
   - Caching optimizacija

4. **Feedback Service**
   - Feedback collection
   - Data aggregation
   - Automatic improvements trigger
   - Analytics

5. **Session Service**
   - Session tracking
   - Log generation
   - Export functionality

---

### Frontend (React + TypeScript)

**Ključne Komponente**:

1. **State Management**
   - React Context API ili Redux
   - Global state za settings
   - Chat history state
   - Session state

2. **Real-time Communication**
   - WebSocket za streaming responses
   - Progress updates
   - Training status

3. **Form Handling**
   - React Hook Form
   - Validation
   - Error handling

4. **UI Components**
   - Material-UI ili Ant Design
   - Custom components
   - Responsive design

---

## 📦 Deployment

### Docker Setup

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./backend/data/qdrant_data:/qdrant/storage
```

---

## 📋 Faze Implementacije

### FAZA 1: Backend Core (1 nedelja)

**Zadaci**:
- [ ] Setup FastAPI projekat sa Material-UI komponentama
- [ ] Implementiraj PDF management API
- [ ] Implementiraj training API sa progress tracking
- [ ] Implementiraj test examples API
- [ ] Implementiraj evaluation API sa progress tracking
- [ ] Integriši postojeći RAG kod
- [ ] Setup SQLite baza
- [ ] Implementiraj settings API
- [ ] Implementiraj progress WebSocket endpoint

**Deliverables**:
- Funkcionalan backend API
- Progress tracking sistem
- Dokumentacija API-ja (OpenAPI)
- Unit testovi

---

### FAZA 2: Frontend Core (1 nedelja)

**Zadaci**:
- [ ] Setup React + TypeScript + Material-UI projekat
- [ ] Setup i18n za srpski jezik
- [ ] Implementiraj PDF Management page sa progress bar
- [ ] Implementiraj Test Examples Management page
- [ ] Implementiraj Chat interface
- [ ] Implementiraj Settings panel sa progress indikatorima
- [ ] Setup API client
- [ ] Implementiraj WebSocket komunikaciju za progress
- [ ] Implementiraj progress komponente (ProgressBar, ProgressDialog)

**Deliverables**:
- Funkcionalan frontend na srpskom
- Progress indikatori za sve operacije
- Responsive dizajn
- Integration sa backend-om

---

### FAZA 3: Test Examples & Evaluation (4-5 dana)

**Zadaci**:
- [ ] Implementiraj test examples CRUD
- [ ] Implementiraj JSON import/export
- [ ] Implementiraj evaluation runner sa progress tracking
- [ ] Implementiraj evaluation results display
- [ ] Integriši sa postojećim evaluation kodom

**Deliverables**:
- Kompletan test management sistem
- Evaluation sa progress tracking
- JSON import/export funkcionalnost

---

### FAZA 4: Version Comparison (3-4 dana)

**Zadaci**:
- [ ] Implementiraj version storage
- [ ] Implementiraj comparison API
- [ ] Implementiraj comparison UI
- [ ] Implementiraj side-by-side prikaz
- [ ] Implementiraj statistiku poboljšanja
- [ ] Implementiraj export izveštaja

**Deliverables**:
- Kompletan version comparison sistem
- Vizualizacija poboljšanja
- Export funkcionalnost

---

### FAZA 5: Feedback System (3-4 dana)

**Zadaci**:
- [ ] Implementiraj feedback API
- [ ] Implementiraj feedback UI na srpskom
- [ ] Integriši sa postojećim feedback loop kodom
- [ ] Implementiraj analytics dashboard

**Deliverables**:
- Kompletan feedback sistem
- Analytics dashboard

---

### FAZA 6: Session Logging (2-3 dana)

**Zadaci**:
- [ ] Implementiraj session tracking
- [ ] Implementiraj log generation
- [ ] Implementiraj export funkcionalnost
- [ ] Implementiraj UI kontrole

**Deliverables**:
- Session logging sistem
- Export funkcionalnost

---

### FAZA 7: Testing & Optimization (3-4 dana)

**Zadaci**:
- [ ] Integration testing
- [ ] Performance testing
- [ ] UI/UX testing na srpskom
- [ ] Progress tracking testing
- [ ] Bug fixing
- [ ] Dokumentacija na srpskom

**Deliverables**:
- Testiran sistem
- Dokumentacija
- Deployment guide

---

### FAZA 8: Docker & Deployment (2-3 dana)

**Zadaci**:
- [ ] Kreiraj Dockerfile-ove
- [ ] Setup docker-compose za lokalni deployment
- [ ] Test deployment
- [ ] Kreiraj deployment dokumentaciju na srpskom

**Deliverables**:
- Docker setup
- Lokalni deployment guide
- Production-ready sistem

---

## 📊 Estimacija Vremena

| Faza | Trajanje | Prioritet |
|------|----------|-----------|
| FAZA 1: Backend Core | 1 nedelja | Visok |
| FAZA 2: Frontend Core | 1 nedelja | Visok |
| FAZA 3: Test Examples & Evaluation | 4-5 dana | Visok |
| FAZA 4: Version Comparison | 3-4 dana | Visok |
| FAZA 5: Feedback System | 3-4 dana | Srednji |
| FAZA 6: Session Logging | 2-3 dana | Srednji |
| FAZA 7: Testing & Optimization | 3-4 dana | Visok |
| FAZA 8: Docker & Deployment | 2-3 dana | Visok |
| **UKUPNO** | **~5-6 nedelja** | - |

---

## 🎯 Success Criteria

### Funkcionalni Zahtevi

- ✅ Korisnik može da upload-uje PDF-ove
- ✅ Korisnik može da briše PDF-ove
- ✅ Korisnik može da pokrene retraining sa progress indikatorom
- ✅ Korisnik može da upravlja test primerima (CRUD)
- ✅ Korisnik može da importuje/exportuje test primere (JSON)
- ✅ Korisnik može da pokrene evaluaciju sa progress indikatorom
- ✅ Korisnik može da poredi različite verzije evaluacije
- ✅ Korisnik može da postavlja pitanja u chat-u
- ✅ Korisnik može da bira LLM model iz Ollama u chat interfejsu
- ✅ Korisnik može da menja RAG parametre
- ✅ Korisnik može da restartuje sistem sa progress indikatorom
- ✅ Korisnik može da ocenjuje odgovore
- ✅ Korisnik može da uključi/isključi session logging
- ✅ Korisnik može da preuzme session log
- ✅ UI je na srpskom jeziku (latinica)

### Nefunkcionalni Zahtevi

- ✅ Vreme odgovora < 10s
- ✅ Single-user aplikacija (bez autentifikacije)
- ✅ GPU optimizacija aktivna
- ✅ Responsive UI (desktop + tablet)
- ✅ Material-UI dizajn
- ✅ Progress indikatori za sve duže operacije
- ✅ Lokalni deployment (Docker)
- ✅ Secure (input validation, file upload limits)
- ✅ UI na srpskom jeziku (latinica)

---

## 🚀 Sledeći Koraci

1. **Odobrenje plana** - Čekam tvoj feedback
2. **Setup projekta** - Kreiraj folder strukturu
3. **FAZA 1** - Počni sa backend implementacijom

---

## ✅ Odgovori na Pitanja

1. **UI Framework**: ✅ Material-UI
2. **Authentication**: ✅ Single-user (bez login sistema)
3. **Multi-language**: ✅ UI na srpskom jeziku (latinica)
4. **Deployment**: ✅ Lokalni deployment (Docker)
5. **Monitoring**: ✅ Nije potreban za sada

## 🆕 Dodatni Zahtevi

6. **Test Examples Management**: ✅ CRUD operacije, JSON import/export
7. **Progress Indicators**: ✅ Za sve duže operacije (retraining, evaluation, restart)
8. **Evaluation System**: ✅ Pokretanje evaluacije sa progress tracking
9. **Version Comparison**: ✅ Poređenje različitih verzija evaluacije sa statistikom
10. **LLM Model Selection**: ✅ Izbor modela u chat interfejsu iz dostupnih Ollama modela

---

**Status**: ✅ Odobreno i ažurirano
**Sledeći korak**: Početak implementacije FAZE 1

---

## 🎯 Preporuke za Testiranje Obrade PDF Fajlova na Srpskom

### Što Plan Već Pokriva

✅ **Batch Upload & Processing**
- Upload više PDF-ova odjednom
- Automatsko procesiranje svih fajlova
- Progress tracking za svaki fajl

✅ **Evaluacija Kvaliteta**
- Test primeri sa pitanjima i tačnim odgovorima
- Automatska evaluacija tačnosti
- Poređenje različitih verzija (parametara, modela)
- Metrike: precision, recall, F1 score

✅ **Optimizacija za Srpski Jezik**
- Transliteracija (Ćirilica → Latinica)
- Spell checking
- Multilingual embedding model (BGE-M3)
- Hybrid search (semantička + keyword)

✅ **Eksperimentisanje**
- Promena LLM modela u chat interfejsu
- Promena RAG parametara (chunk size, overlap, temperature)
- Poređenje rezultata između verzija
- Feedback loop za kontinualno poboljšanje

### Dodatne Preporuke

#### 1. **Organizacija PDF Fajlova**
Preporučujem da organizuješ PDF-ove po kategorijama:
```
data/pdfs/
├── zakoni/
│   ├── zakon_o_porezu.pdf
│   └── zakon_o_radu.pdf
├── procedure/
│   ├── procedura_1.pdf
│   └── procedura_2.pdf
└── pravilnici/
    ├── pravilnik_1.pdf
    └── pravilnik_2.pdf
```

**Implementacija**: Dodaj metadata tag za kategoriju pri upload-u, omogući filtriranje po kategoriji u pretrazi.

#### 2. **Test Set po Kategorijama**
Kreiraj test setove specifične za svaku kategoriju dokumenata:
- `test_zakoni.json` - pitanja o zakonima
- `test_procedure.json` - pitanja o procedurama
- `test_pravilnici.json` - pitanja o pravilnicima

**Benefit**: Možeš videti kako sistem radi na različitim tipovima dokumenata.

#### 3. **Bulk Evaluation**
Dodaj mogućnost pokretanja evaluacije na više test setova odjednom:
- Evaluiraj sve kategorije
- Uporedi performanse između kategorija
- Identifikuj koje kategorije trebaju dodatnu optimizaciju

#### 4. **Document Statistics**
Dodaj prikaz statistike za svaki PDF:
- Broj stranica
- Broj chunk-ova
- Prosečna dužina chunk-a
- Broj embeddings-a
- Vreme procesiranja

**Benefit**: Razumeš kako različiti dokumenti utiču na performanse.

#### 5. **Query Analytics**
Prati statistiku upita:
- Najčešća pitanja
- Prosečno vreme odgovora po kategoriji
- Tačnost po kategoriji
- Najgori odgovori (za dalje poboljšanje)

#### 6. **A/B Testing Framework**
Omogući paralelno testiranje različitih konfiguracija:
- Model A vs Model B
- Parametri A vs Parametri B
- Automatsko poređenje rezultata


---

## 📦 Project Configuration Management

Sistem omogućava čuvanje i učitavanje kompletne konfiguracije projekta u jedan JSON fajl. Pogledaj [`PROJECT_CONFIG_SPEC.md`](PROJECT_CONFIG_SPEC.md) za detaljnu specifikaciju.

### Šta se Čuva u Konfiguraciji?

1. **Project Info** - Naziv, opis, datum kreiranja
2. **PDF Fajlovi** - Spisak svih PDF-ova sa metadata
3. **Test Primeri** - Sva pitanja i očekivani odgovori
4. **Model Config** - Parametri embedding, LLM i reranker modela
5. **RAG Config** - Chunking, search i reranking parametri
6. **System Prompt** - Konfiguracioni prompt
7. **Evaluation History** - Rezultati svih evaluacija po fazama sa metrikama

### Workflow

```
1. Razvij i testiraj konfiguraciju
   ↓
2. Pokreni evaluaciju i sačuvaj rezultate
   ↓
3. Export konfiguraciju u JSON
   ↓
4. Kasnije: Import konfiguraciju
   ↓
5. Uporedi sa novom konfiguracijom
```

### Primer JSON Strukture

```json
{
  "project_info": {
    "name": "Poreski Propisi Test 1",
    "created_at": "2026-05-20T12:00:00Z"
  },
  "pdfs": [...],
  "test_examples": [...],
  "model_config": {...},
  "rag_config": {...},
  "system_prompt": {...},
  "evaluation_history": [
    {
      "phase": "phase1_baseline",
      "timestamp": "2026-05-20T12:30:00Z",
      "duration_seconds": 120,
      "results": {
        "accuracy": 0.84,
        "precision": 0.86,
        "recall": 0.82,
        "f1_score": 0.84,
        "avg_response_time_ms": 1500,
        "gpu_utilization_avg": 0.75
      }
    },
    {
      "phase": "phase2_optimized",
      "results": {
        "accuracy": 0.94,
        "improvements": {
          "accuracy_delta": 0.10
        }
      }
    }
  ]
}
```

### Benefits

- ✅ **Reproducibility** - Tačno ponavljanje testova
- ✅ **Version Control** - Praćenje evolucije kroz vreme
- ✅ **Comparison** - Lako poređenje različitih pristupa
- ✅ **Backup** - Sigurnosna kopija projekta
- ✅ **Collaboration** - Deljenje konfiguracija
- ✅ **Documentation** - Automatska dokumentacija eksperimenata

### Što Možeš Dodati Kasnije (Opciono)

🔹 **Document Preprocessing**
- OCR za skenirane PDF-ove
- Automatsko uklanjanje header/footer
- Detekcija tabela i njihova posebna obrada

🔹 **Advanced Analytics**
- Grafički prikaz performansi kroz vreme
- Heatmap relevantnosti chunk-ova
- Confusion matrix za evaluaciju

🔹 **Export & Reporting**
- Automatski izveštaji o evaluaciji
- Export rezultata u Excel/CSV
- Vizualizacija poboljšanja kroz verzije

### Zaključak

Plan već pokriva sve **esencijalne** funkcionalnosti za tvoj use case:
- ✅ Batch processing PDF-ova
- ✅ Evaluacija kvaliteta
- ✅ Poređenje verzija
- ✅ Optimizacija za srpski
- ✅ Eksperimentisanje sa modelima i parametrima

Dodatne preporuke su **nice-to-have** i mogu se dodati kasnije po potrebi.
