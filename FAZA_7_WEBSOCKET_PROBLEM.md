# WebSocket Problem - Root Cause Analiza i Rešenje

## Problem
Frontend dobija **timeout of 30000ms exceeded** grešku kada pokušava da se poveže na WebSocket endpoint tokom izvršavanja evaluacije.

## Root Cause

### Originalni Kod (POGREŠAN)
```python
# backend/routers/evaluations.py - linija 133-138
background_tasks.add_task(
    service.run_evaluation,  # ❌ PROBLEM!
    evaluation_id=evaluation_id,
    test_example_ids=data.test_example_ids,
    collection_id=data.collection_id
)
```

### Šta se dešava:

1. **Frontend pozove** `/api/evaluations/{id}/run`
2. **Backend odmah vrati** HTTP response sa `status="running"`
3. **HTTP konekcija se zatvori** ✅
4. **Database session se zatvori** ❌
5. **Tek ONDA** se pokreće `service.run_evaluation()` u pozadini
6. **Background task koristi zatvorenu DB session** ❌

### Posledica:
- Background task pokušava da koristi **zatvorenu database session**
- Database session **nije thread-safe**
- Svi ostali HTTP zahtevi (uključujući WebSocket) se **blokiraju**
- Frontend ne može da se poveže na WebSocket endpoint
- **Timeout nakon 30 sekundi**

## Rešenje

### Novi Kod (ISPRAVAN)
```python
# backend/routers/evaluations.py

async def _run_evaluation_background(
    evaluation_id: int,
    test_example_ids: Optional[List[int]],
    collection_id: Optional[int]
):
    """Helper function to run evaluation in background with NEW DB session"""
    from backend.database import SessionLocal
    db = SessionLocal()  # ✅ NOVA SESSION!
    try:
        service = EvaluationService(db)
        await service.run_evaluation(
            evaluation_id=evaluation_id,
            test_example_ids=test_example_ids,
            collection_id=collection_id
        )
    except Exception as e:
        logger.error(f"Background evaluation error: {e}")
    finally:
        db.close()  # ✅ CLEANUP!


@router.post("/{evaluation_id}/run")
async def run_evaluation(...):
    # ...
    background_tasks.add_task(
        _run_evaluation_background,  # ✅ Helper sa novom session
        evaluation_id=evaluation_id,
        test_example_ids=data.test_example_ids,
        collection_id=data.collection_id
    )
```

### Ključne Izmene:

1. **Nova helper funkcija** `_run_evaluation_background()`
2. **Kreira NOVU database session** unutar background task-a
3. **Properly cleanup** - zatvara session u `finally` bloku
4. **Nezavisna od HTTP request lifecycle**

## Kako Testirati

1. **Restartuj backend server**:
   ```bash
   cd backend
   python -m uvicorn backend.main:app --reload
   ```

2. **Pokreni evaluaciju**:
   - Idi na Evaluations stranicu
   - Klikni "Run" na nekoj evaluaciji

3. **Otvori Log Viewer**:
   - Klikni "Log" dugme (ikona Article)
   - Trebalo bi da vidiš real-time log poruke

4. **Proveri WebSocket konekciju**:
   - Otvori Browser DevTools → Network → WS
   - Trebalo bi da vidiš aktivnu WebSocket konekciju
   - Status: `101 Switching Protocols`

## Tehnički Detalji

### FastAPI BackgroundTasks Lifecycle:
```
1. HTTP Request arrives
2. Dependency injection (get_db) creates DB session
3. Endpoint handler executes
4. background_tasks.add_task() registers task
5. HTTP Response sent ✅
6. DB session closed ❌
7. Background task starts executing ❌ (uses closed session)
```

### Ispravljen Lifecycle:
```
1. HTTP Request arrives
2. Dependency injection (get_db) creates DB session
3. Endpoint handler executes
4. background_tasks.add_task() registers helper function
5. HTTP Response sent ✅
6. DB session closed ✅
7. Background task starts executing ✅
8. Helper creates NEW DB session ✅
9. Evaluation runs with new session ✅
10. Helper closes session in finally block ✅
```

## Zaključak

Problem je bio u **lifecycle management** database session-a. FastAPI BackgroundTasks se izvršavaju **nakon** što se HTTP response vrati i **nakon** što se dependency-injected resursi (kao DB session) cleanup-uju.

Rešenje je kreiranje **nove, nezavisne database session** unutar background task-a, što omogućava:
- ✅ Evaluacija se izvršava u pozadini
- ✅ HTTP endpoint odmah vraća response
- ✅ WebSocket konekcije mogu da se uspostave
- ✅ Frontend može da dobija real-time log poruke
- ✅ Nema blokiranja drugih HTTP zahteva

## Status
✅ **REŠENO** - Backend ispravljen, spreman za testiranje

---
*Made with Bob - Root Cause Analysis*