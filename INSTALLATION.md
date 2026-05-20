# 🔧 PDF2GPU - Instalacioni Vodič

## 📊 Status Instalacije

### ✅ Već Instalirano

| Tehnologija | Verzija | Status |
|-------------|---------|--------|
| Python | 3.12.0 | ✅ Instalirano |
| Docker | 29.4.3 | ✅ Instalirano |
| Ollama | - | ✅ Instalirano |
| PyTorch (CUDA) | 2.11.0+cu128 | ✅ Instalirano |
| Qdrant Client | 1.18.0 | ✅ Instalirano |
| Sentence Transformers | 5.5.0 | ✅ Instalirano |
| Transformers | 5.8.1 | ✅ Instalirano |

### ❌ Potrebno Instalirati

| Tehnologija | Potrebna Verzija | Svrha |
|-------------|-------------------|-------|
| Node.js | 20.x LTS | Frontend (React) |
| npm | 10.x | Package manager za frontend |
| FastAPI | 0.115+ | Backend framework |
| pytest | 8.x | Testing framework |
| pytest-asyncio | 0.24+ | Async testing |
| pytest-cov | 6.x | Code coverage |
| uvicorn | 0.34+ | ASGI server |
| websockets | 14.x | WebSocket support |
| python-multipart | 0.0.20+ | File upload support |
| aiofiles | 24.x | Async file operations |

---

## 🚀 Instalacija - Korak po Korak

### 1. **Node.js i npm** (Frontend)

**Download i instalacija:**
```bash
# Preuzmi Node.js 20.x LTS sa:
# https://nodejs.org/en/download/

# Posle instalacije, proveri:
node --version  # Trebalo bi: v20.x.x
npm --version   # Trebalo bi: 10.x.x
```

**Alternativa - Korišćenje nvm (Node Version Manager):**
```bash
# Preuzmi nvm sa:
# https://github.com/coreybutler/nvm-windows/releases

# Instaliraj Node.js 20:
nvm install 20
nvm use 20
```

---

### 2. **Python Backend Paketi**

Kreiraj `requirements.txt` za backend:

```bash
# Pozicioniraj se u PDF2GPU folder
cd PDF2GPU

# Kreiraj requirements.txt
```

**`requirements.txt`:**
```
# Web Framework
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-multipart==0.0.20
websockets==14.1

# Async Support
aiofiles==24.1.0
asyncio==3.4.3

# Testing
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
pytest-mock==3.14.0
httpx==0.28.1
faker==34.0.0

# Database
sqlalchemy==2.0.36
alembic==1.14.0

# Validation
pydantic==2.13.4
pydantic-settings==2.7.1

# Utilities
python-dotenv==1.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Već instalirano (proveri verzije)
torch>=2.11.0
qdrant-client>=1.18.0
sentence-transformers>=5.5.0
transformers>=5.8.1
ollama>=0.6.2
PyPDF2>=3.0.1
```

**Instalacija:**
```bash
# Instaliraj sve pakete
python -m pip install -r requirements.txt

# Ili pojedinačno:
python -m pip install fastapi uvicorn[standard] python-multipart websockets
python -m pip install aiofiles pytest pytest-asyncio pytest-cov
python -m pip install sqlalchemy alembic pydantic pydantic-settings
```

---

### 3. **Frontend Setup** (React + TypeScript)

**Kreiranje React projekta:**
```bash
# Pozicioniraj se u PDF2GPU folder
cd PDF2GPU

# Kreiraj React app sa TypeScript
npx create-react-app frontend --template typescript

# Uđi u frontend folder
cd frontend

# Instaliraj Material-UI
npm install @mui/material @emotion/react @emotion/styled

# Instaliraj dodatne pakete
npm install @mui/icons-material
npm install axios
npm install react-router-dom
npm install @types/react-router-dom

# Testing libraries (već uključene u CRA)
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event

# API mocking za testove
npm install --save-dev msw

# WebSocket client
npm install socket.io-client
```

**`frontend/package.json` (dodatni dependencies):**
```json
{
  "dependencies": {
    "@mui/material": "^6.3.0",
    "@mui/icons-material": "^6.3.0",
    "@emotion/react": "^11.14.0",
    "@emotion/styled": "^11.14.0",
    "axios": "^1.7.9",
    "react-router-dom": "^7.2.0",
    "socket.io-client": "^4.8.1"
  },
  "devDependencies": {
    "@testing-library/react": "^16.1.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/user-event": "^14.5.2",
    "msw": "^2.8.3"
  }
}
```

---

### 4. **Docker Compose Setup**

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
      - ./project_configs:/app/project_configs
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - OLLAMA_HOST=host.docker.internal:11434
      - CUDA_VISIBLE_DEVICES=0
    depends_on:
      - qdrant
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  qdrant_data:
```

---

### 5. **Provera GPU Podrške**

```bash
# Proveri CUDA verziju
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

# Očekivani output:
# CUDA Available: True
# CUDA Version: 12.8
# GPU: NVIDIA GeForce RTX 5070 Ti
```

---

### 6. **Struktura Projekta**

```
PDF2GPU/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── api/
│   ├── services/
│   ├── models/
│   └── utils/
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── public/
│   └── src/
├── tests/
│   ├── phase1_backend_core/
│   ├── phase2_frontend_core/
│   └── ...
├── data/
│   └── pdfs/
├── project_configs/
├── test_reports/
├── docker-compose.yml
├── run_tests.py
├── PLAN.md
├── TESTING_STRATEGY.md
├── PROJECT_CONFIG_SPEC.md
└── INSTALLATION.md
```

---

## 🧪 Verifikacija Instalacije

### Backend Test

```bash
# Kreiraj test fajl
cd PDF2GPU/backend
python -c "
import fastapi
import uvicorn
import pytest
import torch
import qdrant_client
import sentence_transformers
print('✅ Svi backend paketi su instalirani!')
print(f'✅ CUDA: {torch.cuda.is_available()}')
"
```

### Frontend Test

```bash
# Proveri Node.js i npm
node --version
npm --version

# Proveri React instalaciju
cd PDF2GPU/frontend
npm list react react-dom typescript
```

---

## 📝 Sledeći Koraci

Posle instalacije:

1. **Kreiraj backend strukturu**
   ```bash
   cd PDF2GPU
   mkdir -p backend/api backend/services backend/models backend/utils
   ```

2. **Kreiraj test strukturu**
   ```bash
   mkdir -p tests/phase1_backend_core tests/phase2_frontend_core
   ```

3. **Inicijalizuj Git**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Project setup"
   ```

4. **Pokreni FAZU 1 - Backend Core**
   - Implementiraj FastAPI endpoints
   - Integriši RAG engine
   - Napiši testove
   - Pokreni `python run_tests.py phase1`

---

## 🆘 Troubleshooting

### Problem: Node.js nije instaliran
**Rešenje:** Preuzmi sa https://nodejs.org/ i instaliraj LTS verziju

### Problem: CUDA nije dostupan
**Rešenje:** 
```bash
# Reinstaliraj PyTorch sa CUDA podrškom
python -m pip uninstall torch torchvision torchaudio
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Problem: Docker ne vidi GPU
**Rešenje:**
```bash
# Instaliraj NVIDIA Container Toolkit
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### Problem: Port 8000 ili 3000 zauzet
**Rešenje:**
```bash
# Promeni portove u docker-compose.yml
# Backend: "8001:8000"
# Frontend: "3001:3000"
```

---

## ✅ Checklist Pre Početka Razvoja

- [ ] Python 3.12+ instaliran
- [ ] Node.js 20.x instaliran
- [ ] Docker instaliran i pokrenut
- [ ] Ollama instaliran i pokrenut
- [ ] CUDA dostupan (torch.cuda.is_available() == True)
- [ ] Backend requirements instalirani
- [ ] Frontend dependencies instalirani
- [ ] Struktura projekta kreirana
- [ ] Git inicijalizovan

**Kada sve ✅ - spreman si za FAZU 1!**