# Faza 7 - WebSocket Problem - Izveštaj

## Datum: 2026-05-20

## Problem
WebSocket konekcija se uspostavlja ali se odmah zatvara, što dovodi do beskonačne petlje reconnect pokušaja.

## Simptomi
1. Chat sesija se uspešno kreira (POST `/api/chat/sessions` vraća 200 OK)
2. WebSocket se konektuje (`WebSocket connected: 31`)
3. WebSocket se odmah diskonektuje (`WebSocket disconnected: 31`)
4. Frontend automatski pokušava reconnect (zbog `autoReconnect: true`)
5. Ciklus se ponavlja beskonačno

## Uzrok
Backend WebSocket endpoint čeka na `await websocket.receive_json()` sa timeout-om od 30 sekundi, ali frontend ne šalje ništa odmah nakon konekcije. Međutim, čini se da se konekcija zatvara PRE nego što timeout istekne.

## Pokušana Rešenja

### 1. Ispravljeno kreiranje sesije
- **Problem**: Backend je pokušavao da kreira NOVU sesiju u WebSocket endpointu
- **Rešenje**: Sesija se sada kreira samo preko POST `/api/chat/sessions`
- **Status**: ✅ Uspešno

### 2. Ispravljen response format
- **Problem**: Backend vraćao `session_id`, frontend očekivao `id`
- **Rešenje**: Backend sada vraća oba polja
- **Status**: ✅ Uspešno

### 3. Dodat timeout za receive_json
- **Problem**: `receive_json()` blokira beskonačno
- **Rešenje**: Dodat `asyncio.wait_for()` sa timeout-om od 30s
- **Status**: ⚠️ Delimično - konekcija se i dalje zatvara

## Trenutno Stanje Koda

### Backend (`backend/routers/chat.py`)
```python
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    await manager.connect(websocket, session_id)
    chat_service = ChatService(db)
    
    try:
        session_id_int = int(session_id)
        await manager.send_status(session_id, "Povezan")
        
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
            except asyncio.TimeoutError:
                await manager.send_message(session_id, {"type": "ping", "content": "keepalive"})
                continue
            
            # Process message...
```

### Frontend (`frontend/src/hooks/useWebSocket.ts`)
```typescript
export const useWebSocket = (sessionId: string | null, options: WebSocketHookOptions = {}) => {
  const {
    autoReconnect = true,  // ← Problem: automatski reconnect
    reconnectInterval = 3000,
  } = options;
  
  // ...
  
  ws.onclose = () => {
    if (autoReconnect && sessionId) {
      setTimeout(() => connect(), reconnectInterval);  // ← Beskonačna petlja
    }
  };
}
```

## Moguća Rešenja

### Opcija 1: Onemogućiti Auto-Reconnect (Brzo)
Promeniti default vrednost `autoReconnect` na `false` u `useWebSocket.ts`.

**Prednosti:**
- Brzo rešenje
- Zaustavlja beskonačnu petlju

**Mane:**
- Gubi se automatsko reconnect funkcionalnost
- Korisnik mora ručno da osvežava stranicu

### Opcija 2: Implementirati Heartbeat Mehanizam (Preporučeno)
Frontend šalje ping poruke svakih 10-15 sekundi da održi konekciju.

**Prednosti:**
- Održava konekciju aktivnom
- Detektuje mrtve konekcije
- Standardna praksa za WebSocket

**Mane:**
- Zahteva izmene i na frontendu i na backendu

### Opcija 3: Debugging - Proveriti Zašto se Zatvara
Dodati detaljnije logovanje da vidimo TAČAN razlog zatvaranja.

## Preporuka
Kombinacija Opcije 1 (privremeno) i Opcije 2 (dugoročno):

1. **Odmah**: Onemogućiti auto-reconnect da zaustavimo beskonačnu petlju
2. **Zatim**: Implementirati heartbeat mehanizam
3. **Na kraju**: Ponovo omogućiti auto-reconnect sa boljom logikom

## Sledeći Koraci
1. Onemogućiti `autoReconnect` u `useWebSocket.ts`
2. Testirati da li WebSocket ostaje povezan bez reconnect petlje
3. Ako radi, implementirati heartbeat
4. Ako ne radi, dodati detaljnije logovanje za debugging

## Napomene
- Chat funkcionalnost je SKORO spremna - samo WebSocket konekcija pravi problem
- Svi ostali delovi sistema rade ispravno (kreiranje sesije, routing, database)
- Problem je specifičan za WebSocket lifecycle management