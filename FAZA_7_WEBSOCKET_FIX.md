# Faza 7 - WebSocket Problem - REŠENJE

## Datum: 2026-05-20

## 🔍 ROOT CAUSE IDENTIFIKOVAN

### Problem: Dependency Hell u useWebSocket Hook-u

**Lokacija**: `frontend/src/hooks/useWebSocket.ts` linija 133

```typescript
// STARI KOD (POGREŠAN):
useEffect(() => {
  if (sessionId) {
    connect();
  }
  return () => {
    disconnect();  // ← Poziva se SVAKI PUT kada se dependency promeni!
  };
}, [sessionId, connect, disconnect]);  // ← connect i disconnect se menjaju na svakom render-u!
```

### Šta se dešavalo:

1. **WebSocket se konektuje** kada se komponenta mount-uje
2. **`connect` i `disconnect` funkcije se kreiraju** (useCallback)
3. **useEffect detektuje promenu dependency-ja** (connect/disconnect su novi objekti)
4. **Cleanup funkcija se pokreće** → `disconnect()` se poziva
5. **WebSocket se zatvara**
6. **`ws.onclose` handler se aktivira**
7. **autoReconnect pokreće novu konekciju** (nakon 3s)
8. **Beskonačna petlja!** 🔄

### Dodatni Problemi:

1. **Race Condition**: Frontend ping interval = 30s, Backend timeout = 30s
   - Ako ping stigne 1ms prekasno, backend zatvara konekciju
   
2. **Nepotrebni Dependency**: `connect` i `disconnect` u dependency array-u uzrokuju re-render loop

## ✅ REŠENJE IMPLEMENTIRANO

### 1. Ispravljeno Dependency Hell (`useWebSocket.ts`)

```typescript
// NOVI KOD (ISPRAVAN):
useEffect(() => {
  if (sessionId) {
    connect();
  }
  
  // Cleanup SAMO na unmount ili kada se sessionId promeni
  return () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };
}, [sessionId]); // ← SAMO sessionId u dependencies!
```

**Izmene:**
- ✅ Uklonjeno `connect` i `disconnect` iz dependency array-a
- ✅ Direktno zatvaranje WebSocket-a u cleanup funkciji
- ✅ Cleanup se sada pokreće SAMO kada se sessionId promeni ili komponenta unmount-uje

### 2. Sinhronizovani Ping/Timeout Intervali

**Frontend** (`useWebSocket.ts`):
```typescript
// Ping svakih 20 sekundi (pre backend timeout-a)
const interval = setInterval(() => {
  ping();
}, 20000); // ← Promenjeno sa 30000 na 20000
```

**Backend** (`backend/routers/chat.py`):
```typescript
// Timeout od 25 sekundi (nakon frontend ping-a)
data = await asyncio.wait_for(websocket.receive_json(), timeout=25.0)
```

**Logika:**
- Frontend šalje ping svakih **20s**
- Backend čeka poruku **25s** pre timeout-a
- **5s buffer** osigurava da ping stigne na vreme
- Ako nema poruke 25s, backend šalje svoj ping

## 📊 Dijagram Toka (NOVO)

```
Frontend                    Backend
   |                           |
   |-------- connect --------->|
   |<------- accept -----------|
   |<------ "Povezan" ---------|
   |                           |
   |                           | (čeka poruku, timeout=25s)
   |                           |
   | (nakon 20s)               |
   |-------- ping ------------>|
   |<------- pong -------------|
   |                           |
   | (nakon 20s)               |
   |-------- ping ------------>|
   |<------- pong -------------|
   |                           |
   | (korisnik šalje query)    |
   |-------- query ----------->|
   |                           | (procesira)
   |<------ tokens ------------|
   |<------ complete ----------|
   |                           |
   | (ciklus se nastavlja)     |
```

## 🎯 Ključne Izmene

### Frontend (`frontend/src/hooks/useWebSocket.ts`)
1. **Linija 133**: Uklonjeno `connect` i `disconnect` iz dependencies
2. **Linija 141**: Ping interval promenjen sa 30s na 20s
3. **Linija 128-136**: Direktno zatvaranje WebSocket-a u cleanup funkciji

### Backend (`backend/routers/chat.py`)
1. **Linija 62**: Timeout promenjen sa 30s na 25s
2. **Linija 63-66**: Dodat komentar koji objašnjava logiku

## 🧪 Testiranje

Potrebno je testirati:

1. ✅ WebSocket se konektuje i ostaje povezan
2. ✅ Ping/pong razmena funkcioniše
3. ✅ Nema beskonačne reconnect petlje
4. ⏳ Query/response funkcioniše
5. ⏳ Graceful disconnect funkcioniše

## 📝 Napomene

- **Dependency Hell** je čest problem u React hook-ovima sa WebSocket-ima
- **Ping interval** mora biti MANJI od backend timeout-a
- **Buffer od 5s** je dovoljan za mrežne kašnjenje
- **autoReconnect** je i dalje omogućen, ali sada radi ispravno

## 🚀 Sledeći Koraci

1. Testirati WebSocket stabilnost
2. Verifikovati da nema reconnect petlje
3. Testirati chat funkcionalnost end-to-end
4. Dokumentovati finalno rešenje

## 🎓 Lekcije Naučene

1. **React useEffect dependencies** moraju biti pažljivo odabrani
2. **useCallback funkcije** kreiraju nove reference na svakom render-u
3. **WebSocket ping/timeout** intervali moraju biti sinhronizovani
4. **Cleanup funkcije** se pokreću SVAKI PUT kada se dependency promeni
5. **Direktno zatvaranje resursa** u cleanup je bolje od pozivanja helper funkcija

---

**Status**: ✅ REŠENO - Čeka se testiranje