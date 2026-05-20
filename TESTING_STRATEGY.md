# 🧪 Strategija Automatizovanog Testiranja - PDF2GPU

## Pregled

Svaka faza razvoja će imati automatizovane testove koji će se izvršavati pre prelaska na sledeću fazu. Testovi će biti organizovani po fazama i automatski će se pokretati.

---

## 📋 Test Struktura

```
PDF2GPU/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest konfiguracija i fixtures
│   ├── test_runner.py                 # Glavni test runner
│   │
│   ├── phase1_backend_core/
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py      # Test svih API endpoints
│   │   ├── test_pdf_processing.py     # Test PDF procesiranja
│   │   ├── test_rag_engine.py         # Test RAG sistema
│   │   ├── test_ollama_service.py     # Test Ollama integracije
│   │   ├── test_progress_tracking.py  # Test progress tracking
│   │   └── test_database.py           # Test SQLite operacija
│   │
│   ├── phase2_frontend_core/
│   │   ├── __init__.py
│   │   ├── test_components.test.tsx   # React component tests
│   │   ├── test_api_integration.test.tsx
│   │   ├── test_serbian_ui.test.tsx   # Test srpskog UI
│   │   └── test_progress_ui.test.tsx  # Test progress komponenti
│   │
│   ├── phase3_test_examples/
│   │   ├── __init__.py
│   │   ├── test_crud_operations.py    # Test CRUD za test primere
│   │   ├── test_evaluation.py         # Test evaluacije
│   │   └── test_import_export.py      # Test import/export
│   │
│   ├── phase4_version_comparison/
│   │   ├── __init__.py
│   │   ├── test_comparison_logic.py   # Test logike poređenja
│   │   └── test_comparison_ui.test.tsx
│   │
│   ├── phase5_feedback/
│   │   ├── __init__.py
│   │   ├── test_feedback_collection.py
│   │   └── test_feedback_analytics.py
│   │
│   ├── phase6_session_logging/
│   │   ├── __init__.py
│   │   ├── test_session_tracking.py
│   │   └── test_session_export.py
│   │
│   ├── phase7_integration/
│   │   ├── __init__.py
│   │   ├── test_end_to_end.py         # E2E testovi
│   │   ├── test_performance.py        # Performance testovi
│   │   └── test_gpu_utilization.py    # GPU testovi
│   │
│   └── phase8_deployment/
│       ├── __init__.py
│       ├── test_docker_build.py       # Test Docker build
│       └── test_docker_compose.py     # Test Docker Compose
│
├── pytest.ini                          # Pytest konfiguracija
├── jest.config.js                      # Jest konfiguracija (frontend)
└── run_tests.py                        # Automatski test runner
```

---

## 🎯 Test Kategorije

### 1. **Unit Tests** (Brzi, izolovani)
- Testiraju pojedinačne funkcije/komponente
- Izvršavaju se pri svakoj promeni koda
- Cilj: 100% code coverage za kritične funkcije

### 2. **Integration Tests** (Srednji)
- Testiraju interakciju između komponenti
- Izvršavaju se posle svake faze
- Cilj: Verifikacija da sve komponente rade zajedno

### 3. **End-to-End Tests** (Spori, kompleksni)
- Testiraju ceo workflow od početka do kraja
- Izvršavaju se u FAZI 7
- Cilj: Simulacija realnog korišćenja

### 4. **Performance Tests** (Specijalizovani)
- Testiraju brzinu i GPU iskorišćenje
- Izvršavaju se u FAZI 7
- Cilj: Verifikacija optimizacija

---

## 🔧 Test Tools

### Backend (Python)
```bash
pytest                  # Test framework
pytest-cov             # Code coverage
pytest-asyncio         # Async test podrška
pytest-mock            # Mocking
httpx                  # HTTP client za API testove
faker                  # Test data generation
```

### Frontend (TypeScript/React)
```bash
jest                   # Test framework
@testing-library/react # React testing
@testing-library/user-event # User interaction simulation
msw                    # API mocking
```

---

## 📊 Test Metrics

Svaka faza mora da prođe sledeće metrike:

| Metrika | Minimum | Cilj |
|---------|---------|------|
| Code Coverage | 80% | 90%+ |
| Test Pass Rate | 100% | 100% |
| Performance Regression | 0% | 0% |
| API Response Time | <500ms | <200ms |
| GPU Utilization | >70% | >85% |

---

## 🚀 Automatski Test Runner

### `run_tests.py`

```python
#!/usr/bin/env python3
"""
Automatski test runner za PDF2GPU projekat.
Pokreće testove za određenu fazu i generiše izveštaj.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class TestRunner:
    def __init__(self, phase: str):
        self.phase = phase
        self.results = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    def run_backend_tests(self, test_path: str) -> Tuple[bool, Dict]:
        """Pokreće Python testove sa pytest"""
        print(f"\n🧪 Pokretanje backend testova: {test_path}")
        
        cmd = [
            "pytest",
            test_path,
            "-v",                          # Verbose
            "--cov=backend",               # Coverage
            "--cov-report=term-missing",   # Prikaži missing lines
            "--cov-report=json",           # JSON izveštaj
            "--tb=short",                  # Kraći traceback
            "--color=yes"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse coverage
        coverage_data = {}
        if Path("coverage.json").exists():
            with open("coverage.json") as f:
                coverage_data = json.load(f)
        
        return result.returncode == 0, {
            "passed": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "coverage": coverage_data.get("totals", {}).get("percent_covered", 0)
        }
    
    def run_frontend_tests(self, test_path: str) -> Tuple[bool, Dict]:
        """Pokreće TypeScript testove sa Jest"""
        print(f"\n🧪 Pokretanje frontend testova: {test_path}")
        
        cmd = [
            "npm",
            "test",
            "--",
            test_path,
            "--coverage",
            "--watchAll=false",
            "--json",
            "--outputFile=jest-results.json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="frontend")
        
        # Parse results
        jest_data = {}
        if Path("frontend/jest-results.json").exists():
            with open("frontend/jest-results.json") as f:
                jest_data = json.load(f)
        
        return result.returncode == 0, {
            "passed": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "coverage": jest_data.get("coverageMap", {})
        }
    
    def run_phase_tests(self) -> bool:
        """Pokreće sve testove za određenu fazu"""
        phase_config = {
            "phase1": {
                "backend": ["tests/phase1_backend_core/"],
                "frontend": []
            },
            "phase2": {
                "backend": [],
                "frontend": ["tests/phase2_frontend_core/"]
            },
            "phase3": {
                "backend": ["tests/phase3_test_examples/"],
                "frontend": []
            },
            "phase4": {
                "backend": ["tests/phase4_version_comparison/"],
                "frontend": ["tests/phase4_version_comparison/"]
            },
            "phase5": {
                "backend": ["tests/phase5_feedback/"],
                "frontend": []
            },
            "phase6": {
                "backend": ["tests/phase6_session_logging/"],
                "frontend": []
            },
            "phase7": {
                "backend": ["tests/phase7_integration/"],
                "frontend": []
            },
            "phase8": {
                "backend": ["tests/phase8_deployment/"],
                "frontend": []
            }
        }
        
        config = phase_config.get(self.phase, {})
        all_passed = True
        
        # Backend testovi
        for test_path in config.get("backend", []):
            passed, results = self.run_backend_tests(test_path)
            self.results["tests"][test_path] = results
            all_passed = all_passed and passed
        
        # Frontend testovi
        for test_path in config.get("frontend", []):
            passed, results = self.run_frontend_tests(test_path)
            self.results["tests"][test_path] = results
            all_passed = all_passed and passed
        
        return all_passed
    
    def generate_report(self):
        """Generiše test izveštaj"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"].values() if t["passed"])
        
        self.results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        # Sačuvaj JSON izveštaj
        report_path = f"test_reports/{self.phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path("test_reports").mkdir(exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Prikaži summary
        print("\n" + "="*60)
        print(f"📊 TEST IZVEŠTAJ - {self.phase.upper()}")
        print("="*60)
        print(f"Ukupno testova: {total_tests}")
        print(f"✅ Prošlo: {passed_tests}")
        print(f"❌ Palo: {total_tests - passed_tests}")
        print(f"📈 Pass Rate: {self.results['summary']['pass_rate']:.1f}%")
        print(f"\n📄 Detaljan izveštaj: {report_path}")
        print("="*60)
        
        return self.results["summary"]["pass_rate"] >= 80  # Minimum 80% pass rate

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <phase>")
        print("Phases: phase1, phase2, phase3, phase4, phase5, phase6, phase7, phase8")
        sys.exit(1)
    
    phase = sys.argv[1]
    runner = TestRunner(phase)
    
    print(f"\n🚀 Pokretanje testova za {phase.upper()}")
    
    tests_passed = runner.run_phase_tests()
    report_ok = runner.generate_report()
    
    if tests_passed and report_ok:
        print("\n✅ SVI TESTOVI SU PROŠLI! Možeš nastaviti na sledeću fazu.")
        sys.exit(0)
    else:
        print("\n❌ TESTOVI NISU PROŠLI! Ispravi greške pre nego što nastaviš.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🔄 Workflow za Svaku Fazu

### 1. **Razvoj**
```bash
# Razvijaj feature
# ...
```

### 2. **Lokalni Testovi** (Tokom razvoja)
```bash
# Backend
pytest tests/phase1_backend_core/ -v

# Frontend
cd frontend && npm test
```

### 3. **Automatski Test Pre Commit**
```bash
# Pokreni sve testove za trenutnu fazu
python run_tests.py phase1
```

### 4. **Ako Testovi Prođu**
```bash
# Commit i nastavi
git add .
git commit -m "FAZA 1: Implementacija backend core"
```

### 5. **Ako Testovi Padnu**
```bash
# Pregledaj izveštaj
cat test_reports/phase1_*.json

# Ispravi greške
# Ponovi testove
python run_tests.py phase1
```

---

## 📝 Test Primeri

### Backend Test Primer

```python
# tests/phase1_backend_core/test_pdf_processing.py

import pytest
from pathlib import Path
from backend.services.pdf_processor import PDFProcessor

@pytest.fixture
def sample_pdf():
    """Fixture koji vraća putanju do test PDF-a"""
    return Path("tests/fixtures/sample.pdf")

@pytest.fixture
def pdf_processor():
    """Fixture koji kreira PDFProcessor instancu"""
    return PDFProcessor()

class TestPDFProcessing:
    """Test suite za PDF procesiranje"""
    
    def test_pdf_upload(self, pdf_processor, sample_pdf):
        """Test upload PDF fajla"""
        result = pdf_processor.upload(sample_pdf)
        
        assert result["success"] is True
        assert "pdf_id" in result
        assert result["filename"] == "sample.pdf"
    
    def test_pdf_parsing(self, pdf_processor, sample_pdf):
        """Test parsiranja PDF-a"""
        pdf_id = pdf_processor.upload(sample_pdf)["pdf_id"]
        result = pdf_processor.parse(pdf_id)
        
        assert result["success"] is True
        assert len(result["chunks"]) > 0
        assert all("text" in chunk for chunk in result["chunks"])
    
    def test_transliteration(self, pdf_processor):
        """Test transliteracije ćirilice u latinicu"""
        cyrillic_text = "Годишњи порез на доходак грађана"
        latin_text = pdf_processor.transliterate(cyrillic_text)
        
        assert latin_text == "Godišnji porez na dohodak građana"
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, pdf_processor, tmp_path):
        """Test batch procesiranja više PDF-ova"""
        # Kreiraj test PDF-ove
        pdf_files = [tmp_path / f"test_{i}.pdf" for i in range(5)]
        
        results = await pdf_processor.batch_process(pdf_files)
        
        assert len(results) == 5
        assert all(r["success"] for r in results)
    
    def test_error_handling_invalid_pdf(self, pdf_processor):
        """Test error handling za nevažeći PDF"""
        with pytest.raises(ValueError, match="Invalid PDF file"):
            pdf_processor.parse("invalid_id")
```

### Frontend Test Primer

```typescript
// tests/phase2_frontend_core/test_components.test.tsx

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PDFUpload } from '@/components/PDFManagement/PDFUpload';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

// Mock API server
const server = setupServer(
  rest.post('/api/pdfs/upload', (req, res, ctx) => {
    return res(ctx.json({ success: true, pdf_id: '123' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('PDFUpload Component', () => {
  test('prikazuje upload dugme', () => {
    render(<PDFUpload />);
    
    const uploadButton = screen.getByText(/Otpremi PDF/i);
    expect(uploadButton).toBeInTheDocument();
  });
  
  test('omogućava upload PDF fajla', async () => {
    render(<PDFUpload />);
    
    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Izaberi PDF/i);
    
    await userEvent.upload(input, file);
    
    expect(input.files[0]).toBe(file);
    expect(input.files).toHaveLength(1);
  });
  
  test('prikazuje progress bar tokom upload-a', async () => {
    render(<PDFUpload />);
    
    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Izaberi PDF/i);
    
    await userEvent.upload(input, file);
    fireEvent.click(screen.getByText(/Otpremi/i));
    
    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });
  
  test('prikazuje success poruku posle uspešnog upload-a', async () => {
    render(<PDFUpload />);
    
    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Izaberi PDF/i);
    
    await userEvent.upload(input, file);
    fireEvent.click(screen.getByText(/Otpremi/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Uspešno otpremljeno/i)).toBeInTheDocument();
    });
  });
  
  test('prikazuje error poruku ako upload ne uspe', async () => {
    server.use(
      rest.post('/api/pdfs/upload', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Upload failed' }));
      })
    );
    
    render(<PDFUpload />);
    
    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Izaberi PDF/i);
    
    await userEvent.upload(input, file);
    fireEvent.click(screen.getByText(/Otpremi/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Greška pri otpremanju/i)).toBeInTheDocument();
    });
  });
});
```

---

## 🎯 Test Coverage Ciljevi

### FAZA 1 - Backend Core
- ✅ API endpoints: 100%
- ✅ PDF processing: 95%+
- ✅ RAG engine: 90%+
- ✅ Database operations: 100%

### FAZA 2 - Frontend Core
- ✅ Components: 90%+
- ✅ API integration: 95%+
- ✅ Serbian UI: 100%

### FAZA 3-6 - Features
- ✅ Business logic: 90%+
- ✅ UI components: 85%+

### FAZA 7 - Integration
- ✅ E2E workflows: 100%
- ✅ Performance: 100%

### FAZA 8 - Deployment
- ✅ Docker build: 100%
- ✅ Docker Compose: 100%

---

## 🔍 Continuous Testing

### Pre-commit Hook

```bash
# .git/hooks/pre-commit

#!/bin/bash

echo "🧪 Pokretanje testova pre commit-a..."

# Pokreni testove za trenutnu fazu
python run_tests.py phase1

if [ $? -ne 0 ]; then
    echo "❌ Testovi nisu prošli! Commit je blokiran."
    exit 1
fi

echo "✅ Testovi su prošli! Nastavljam sa commit-om."
exit 0
```

---

## 📈 Test Reporting

Posle svake faze, generiše se detaljan izveštaj:

```
test_reports/
├── phase1_20260520_120000.json
├── phase2_20260521_140000.json
├── ...
└── final_report.json
```

Svaki izveštaj sadrži:
- ✅ Broj testova (passed/failed)
- 📊 Code coverage
- ⏱️ Execution time
- 🐛 Error details
- 📈 Performance metrics

---

## 🚨 Failure Handling

Ako testovi padnu:

1. **Pregledaj izveštaj**
   ```bash
   cat test_reports/phase1_*.json
   ```

2. **Identifikuj problem**
   - Greška u kodu?
   - Greška u testu?
   - Missing dependency?

3. **Ispravi**
   - Fix code
   - Update test
   - Install dependency

4. **Re-run testove**
   ```bash
   python run_tests.py phase1
   ```

5. **Repeat dok ne prođu**

---

## ✅ Zaključak

Ova strategija osigurava:
- ✅ Kvalitet koda kroz automatizovano testiranje
- ✅ Brzo otkrivanje grešaka
- ✅ Sigurnost pri refaktorisanju
- ✅ Dokumentaciju kroz testove
- ✅ Confidence pri deploy-u

**Pravilo**: Nijedna faza se ne smatra završenom dok svi testovi ne prođu!