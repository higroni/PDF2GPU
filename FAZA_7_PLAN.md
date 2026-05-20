# FAZA 7: Frontend Development & Integration

## Status: 🚀 READY TO START

## Pregled

Frontend aplikacija je već kreirana sa React + TypeScript + Vite + Material-UI stack-om. Potrebno je:
1. Verifikacija i testiranje postojećih komponenti
2. Implementacija nedostajućih funkcionalnosti
3. Integracija sa backend API-jem
4. Testiranje end-to-end workflow-a

---

## Trenutno Stanje Frontend-a

### ✅ Već Implementirano

**Struktura:**
- React 18 + TypeScript
- Vite build tool
- Material-UI (MUI) komponente
- React Router za navigaciju
- TanStack Query za data fetching
- Axios za HTTP requests

**Stranice:**
- `CollectionsPage` - Pregled svih kolekcija
- `CollectionDetailPage` - Detalji pojedinačne kolekcije
- `SearchPage` - Pretraga dokumenata
- `PDFDetailPage` - Detalji PDF dokumenta
- `ChatPage` - Chat interfejs

**Komponente:**
- `ChatWindow` - Glavni chat prozor
- `ChatMessage` - Pojedinačna poruka
- `MessageInput` - Input za unos poruka
- `MessageList` - Lista poruka

**API Integracija:**
- `api/client.ts` - Axios konfiguracija
- `api/collections.ts` - Collections API
- `api/pdfs.ts` - PDFs API
- `api/search.ts` - Search API

**Hooks:**
- `useCollections` - Fetch kolekcija
- `usePDFs` - Fetch PDF-ova
- `useSearch` - Search funkcionalnost
- `useWebSocket` - WebSocket konekcija

---

## Zadaci za FAZU 7

### 1. Verifikacija i Instalacija Dependencies ⏱️ 15 min

**Zadatak:**
- Provera `package.json` dependencies
- Instalacija npm paketa
- Provera da li postoji `.env` fajl

**Komande:**
```bash
cd frontend
npm install
```

**Očekivani rezultat:**
- Svi paketi instalirani
- `node_modules/` direktorijum kreiran

---

### 2. Kreiranje Environment Configuration ⏱️ 10 min

**Zadatak:**
- Kreirati `.env` fajl sa backend URL-om
- Konfiguracija API endpoint-a

**Fajl: `frontend/.env`**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

### 3. Implementacija Nedostajućih Komponenti ⏱️ 2h

#### 3.1 Layout Komponenta
**Fajl: `frontend/src/components/Layout.tsx`**
- Navigation bar sa linkovima
- Sidebar (opciono)
- Footer
- Responsive design

#### 3.2 PDF Upload Komponenta
**Fajl: `frontend/src/components/PDFUpload.tsx`**
- Drag & drop funkcionalnost
- File picker
- Progress bar za upload
- Validacija fajlova (samo PDF)

#### 3.3 Collection Manager Komponenta
**Fajl: `frontend/src/components/CollectionManager.tsx`**
- Kreiranje nove kolekcije
- Editovanje kolekcije
- Brisanje kolekcije
- Dodavanje PDF-ova u kolekciju

#### 3.4 Search Results Komponenta
**Fajl: `frontend/src/components/SearchResults.tsx`**
- Prikaz rezultata pretrage
- Highlighting relevantnih delova
- Pagination
- Sortiranje po relevantnosti

---

### 4. Poboljšanje Postojećih Stranica ⏱️ 1.5h

#### 4.1 CollectionsPage
- Dodati dugme za kreiranje nove kolekcije
- Grid/List view toggle
- Search/filter kolekcija
- Statistika (broj dokumenata, veličina)

#### 4.2 CollectionDetailPage
- Prikaz svih PDF-ova u kolekciji
- Upload novih PDF-ova
- Brisanje PDF-ova iz kolekcije
- Metadata editing

#### 4.3 SearchPage
- Advanced search opcije
- Filteri (po kolekciji, datumu, tipu)
- Export rezultata
- Bookmark funkcionalnost

#### 4.4 ChatPage
- Chat history
- Export konverzacije
- Feedback buttons (👍/👎)
- Source citations u odgovorima

---

### 5. WebSocket Integracija ⏱️ 1h

**Zadatak:**
- Implementacija real-time chat-a
- Reconnection logic
- Error handling
- Typing indicators

**Fajl: `frontend/src/hooks/useWebSocket.ts`**
- Provera postojeće implementacije
- Dodavanje reconnection logike
- Event handlers za različite tipove poruka

---

### 6. Error Handling & Loading States ⏱️ 1h

**Zadatak:**
- Global error boundary
- Loading skeletons
- Toast notifications
- Retry mechanisms

**Komponente:**
- `ErrorBoundary.tsx`
- `LoadingSkeleton.tsx`
- `Toast.tsx`

---

### 7. Styling & Responsiveness ⏱️ 1.5h

**Zadatak:**
- Mobile-first design
- Tablet optimizacija
- Desktop layout
- Dark mode support (opciono)

**Fajlovi:**
- `theme.ts` - MUI theme customization
- Responsive breakpoints
- Custom CSS za specifične komponente

---

### 8. Testing Frontend-a ⏱️ 2h

#### 8.1 Unit Tests
- Component tests sa React Testing Library
- Hook tests
- Utility function tests

#### 8.2 Integration Tests
- API integration tests
- WebSocket tests
- Router tests

#### 8.3 E2E Tests (opciono)
- Cypress ili Playwright
- Critical user flows

---

### 9. Build & Deployment Priprema ⏱️ 30 min

**Zadatak:**
- Production build
- Environment variables
- Static file serving
- CORS konfiguracija

**Komande:**
```bash
npm run build
npm run preview
```

---

### 10. Dokumentacija ⏱️ 1h

**Fajl: `frontend/README.md`**
- Setup instrukcije
- Development workflow
- Build process
- Deployment guide
- Component documentation

---

## Prioriteti

### 🔴 HIGH PRIORITY (Must Have)
1. Environment configuration
2. Layout komponenta
3. PDF Upload funkcionalnost
4. WebSocket integracija
5. Error handling

### 🟡 MEDIUM PRIORITY (Should Have)
1. Advanced search
2. Collection management UI
3. Chat history
4. Responsive design
5. Loading states

### 🟢 LOW PRIORITY (Nice to Have)
1. Dark mode
2. E2E tests
3. Export funkcionalnosti
4. Advanced filters
5. Animations

---

## Testiranje

### Manual Testing Checklist
- [ ] Kreiranje kolekcije
- [ ] Upload PDF-a
- [ ] Pretraga dokumenata
- [ ] Chat funkcionalnost
- [ ] WebSocket konekcija
- [ ] Error scenarios
- [ ] Mobile view
- [ ] Tablet view
- [ ] Desktop view

### Automated Testing
- [ ] Component unit tests
- [ ] API integration tests
- [ ] WebSocket tests
- [ ] Router tests

---

## Očekivani Rezultati

### Funkcionalna Aplikacija
- ✅ Sve stranice funkcionalne
- ✅ API integracija radi
- ✅ WebSocket real-time chat
- ✅ Responsive design
- ✅ Error handling

### Performance
- ⚡ Fast initial load (<3s)
- ⚡ Smooth interactions
- ⚡ Optimized bundle size
- ⚡ Lazy loading komponenti

### User Experience
- 🎨 Clean, intuitive UI
- 🎨 Consistent design
- 🎨 Helpful error messages
- 🎨 Loading indicators

---

## Tehnologije

- **Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **UI Library:** Material-UI (MUI)
- **State Management:** TanStack Query
- **HTTP Client:** Axios
- **Routing:** React Router v6
- **WebSocket:** Native WebSocket API
- **Testing:** React Testing Library, Jest

---

## Sledeći Koraci

Nakon završetka FAZE 7:
1. **FAZA 8:** Docker & Deployment
2. **FAZA 9:** Performance Optimization
3. **FAZA 10:** Final Documentation & Release

---

## Napomene

- Frontend je već dobro strukturiran
- Fokus na integraciju sa backend-om
- Testiranje end-to-end workflow-a
- Responsive design je kritičan
- Error handling mora biti robustan

---

**Estimated Total Time:** 10-12 hours
**Complexity:** Medium
**Dependencies:** Backend API mora biti pokrenut
