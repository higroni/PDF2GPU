# 🗂️ Collection Management - Upravljanje Qdrant Kolekcijama

## Pregled

Sistem za upravljanje različitim Qdrant kolekcijama omogućava organizaciju različitih skupova PDF dokumenata u odvojene vektorske baze. Svaki projekat može imati svoju kolekciju, što omogućava:

- **Izolaciju podataka**: Različiti skupovi dokumenata u odvojenim kolekcijama
- **Paralelno testiranje**: Testiranje različitih konfiguracija bez mešanja podataka
- **Organizacija**: Logičko grupisanje dokumenata (npr. "poreski_propisi", "radni_zakoni", "procedure")
- **Fleksibilnost**: Lako prebacivanje između različitih skupova dokumenata

---

## 🎯 Funkcionalnosti

### 1. **Kreiranje Nove Kolekcije**
- Automatsko kreiranje kolekcije pri kreiranju novog projekta
- Definisanje naziva kolekcije (mora biti jedinstveno)
- Automatska konfiguracija vektorskih dimenzija (1024 za BGE-M3)
- Podrška za hybrid search (dense + sparse vektori)

### 2. **Prebacivanje Između Kolekcija**
- Aktivna kolekcija se čuva u projektu
- Brzo prebacivanje bez ponovnog učitavanja modela
- Automatsko učitavanje metapodataka kolekcije

### 3. **Brisanje Kolekcije**
- Sigurno brisanje sa potvrdom
- Provera da li je kolekcija aktivna
- Čišćenje svih povezanih podataka

### 4. **Pregled Kolekcija**
- Lista svih dostupnih kolekcija
- Broj dokumenata po kolekciji
- Veličina kolekcije
- Status (aktivna/neaktivna)

---

## 📄 API Endpoints

### 1. **List Collections**

```http
GET /api/collections

Response:
{
  "collections": [
    {
      "name": "poreski_propisi_test_1",
      "vectors_count": 234,
      "points_count": 234,
      "status": "active",
      "created_at": "2026-05-20T12:00:00Z",
      "size_bytes": 12345678,
      "config": {
        "vector_size": 1024,
        "distance": "Cosine"
      }
    },
    {
      "name": "radni_zakoni",
      "vectors_count": 456,
      "points_count": 456,
      "status": "inactive",
      "created_at": "2026-05-19T10:00:00Z",
      "size_bytes": 23456789,
      "config": {
        "vector_size": 1024,
        "distance": "Cosine"
      }
    }
  ],
  "active_collection": "poreski_propisi_test_1"
}
```

### 2. **Create Collection**

```http
POST /api/collections
Content-Type: application/json

{
  "name": "novi_propisi",
  "description": "Novi skup poreskih propisa za 2026"
}

Response:
{
  "success": true,
  "collection_name": "novi_propisi",
  "message": "Collection created successfully",
  "config": {
    "vector_size": 1024,
    "distance": "Cosine",
    "on_disk_payload": true
  }
}
```

### 3. **Switch Active Collection**

```http
PUT /api/collections/active
Content-Type: application/json

{
  "collection_name": "radni_zakoni"
}

Response:
{
  "success": true,
  "previous_collection": "poreski_propisi_test_1",
  "active_collection": "radni_zakoni",
  "vectors_count": 456,
  "message": "Switched to collection: radni_zakoni"
}
```

### 4. **Delete Collection**

```http
DELETE /api/collections/{collection_name}

Response:
{
  "success": true,
  "message": "Collection 'radni_zakoni' deleted successfully",
  "deleted_vectors": 456
}
```

### 5. **Get Collection Info**

```http
GET /api/collections/{collection_name}

Response:
{
  "name": "poreski_propisi_test_1",
  "vectors_count": 234,
  "points_count": 234,
  "indexed_vectors_count": 234,
  "status": "active",
  "optimizer_status": "ok",
  "config": {
    "params": {
      "vectors": {
        "size": 1024,
        "distance": "Cosine"
      }
    }
  },
  "payload_schema": {
    "text": "keyword",
    "source": "keyword",
    "page": "integer"
  }
}
```

---

## 🎨 UI Components

### Collection Selector (u Settings Panel)

```
┌─────────────────────────────────────────────────────────┐
│  🗂️ Upravljanje Kolekcijama                             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Aktivna Kolekcija:                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ poreski_propisi_test_1                    ▼     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  Dostupne Kolekcije:                                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ✓ poreski_propisi_test_1 (234 vektora)         │   │
│  │   radni_zakoni (456 vektora)                    │   │
│  │   procedure_2026 (123 vektora)                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  [➕ Nova Kolekcija]  [🗑️ Obriši]  [🔄 Osveži]        │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Create Collection Dialog

```
┌─────────────────────────────────────────────────────────┐
│  ➕ Kreiranje Nove Kolekcije                             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Naziv Kolekcije:                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ novi_propisi_2026                               │   │
│  └─────────────────────────────────────────────────┘   │
│  ℹ️ Naziv mora biti jedinstven i bez razmaka            │
│                                                           │
│  Opis (opciono):                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Poreski propisi za 2026. godinu                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  [❌ Otkaži]                          [✅ Kreiraj]      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend Implementation

### Collection Service (`backend/services/collection_service.py`)

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CollectionInfo
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CollectionService:
    def __init__(self, qdrant_client: QdrantClient):
        self.client = qdrant_client
        self.active_collection: Optional[str] = None
        
    def list_collections(self) -> List[Dict]:
        """Lista svih kolekcija sa metapodacima"""
        collections = self.client.get_collections().collections
        
        result = []
        for collection in collections:
            info = self.client.get_collection(collection.name)
            result.append({
                "name": collection.name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": "active" if collection.name == self.active_collection else "inactive",
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance
                }
            })
        
        return result
    
    def create_collection(self, name: str, vector_size: int = 1024) -> bool:
        """Kreira novu kolekciju"""
        try:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {name}: {e}")
            return False
    
    def delete_collection(self, name: str) -> bool:
        """Briše kolekciju"""
        if name == self.active_collection:
            logger.warning(f"Cannot delete active collection: {name}")
            return False
            
        try:
            self.client.delete_collection(collection_name=name)
            logger.info(f"Deleted collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {name}: {e}")
            return False
    
    def switch_collection(self, name: str) -> bool:
        """Prebacuje na drugu kolekciju"""
        try:
            # Proveri da li kolekcija postoji
            collections = [c.name for c in self.client.get_collections().collections]
            if name not in collections:
                logger.error(f"Collection {name} does not exist")
                return False
            
            self.active_collection = name
            logger.info(f"Switched to collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to collection {name}: {e}")
            return False
    
    def get_collection_info(self, name: str) -> Optional[CollectionInfo]:
        """Vraća informacije o kolekciji"""
        try:
            return self.client.get_collection(collection_name=name)
        except Exception as e:
            logger.error(f"Failed to get info for collection {name}: {e}")
            return None
```

---

## 📊 Database Schema (SQLite)

### Collections Table

```sql
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 0,
    vectors_count INTEGER DEFAULT 0,
    pdfs_count INTEGER DEFAULT 0
);

CREATE INDEX idx_collections_name ON collections(name);
CREATE INDEX idx_collections_active ON collections(is_active);
```

---

## 🔄 Workflow

### Kreiranje Novog Projekta sa Kolekcijom

1. Korisnik kreira novi projekat
2. Unosi naziv projekta → automatski se generiše naziv kolekcije
3. Sistem kreira Qdrant kolekciju
4. Kolekcija se postavlja kao aktivna
5. PDF-ovi se procesiraju i embeddings se čuvaju u kolekciju

### Prebacivanje Između Projekata

1. Korisnik bira drugi projekat iz liste
2. Sistem učitava `collection_name` iz projekta
3. Prebacuje aktivnu kolekciju u Qdrant
4. Učitava PDF-ove i test primere vezane za taj projekat
5. Chat koristi novu aktivnu kolekciju za pretragu

---

## ⚠️ Napomene

1. **Jedinstveni Nazivi**: Svaka kolekcija mora imati jedinstven naziv
2. **Aktivna Kolekcija**: Samo jedna kolekcija može biti aktivna u datom trenutku
3. **Brisanje**: Ne može se obrisati aktivna kolekcija
4. **Performanse**: Prebacivanje između kolekcija je brzo (bez ponovnog učitavanja modela)
5. **Backup**: Preporučuje se redovno čuvanje kolekcija kroz export funkcionalnost

---

## 🚀 Primer Korišćenja

```python
# Inicijalizacija
collection_service = CollectionService(qdrant_client)

# Kreiranje nove kolekcije
collection_service.create_collection("poreski_propisi_2026")

# Prebacivanje na novu kolekciju
collection_service.switch_collection("poreski_propisi_2026")

# Lista svih kolekcija
collections = collection_service.list_collections()

# Brisanje stare kolekcije
collection_service.delete_collection("poreski_propisi_2025")