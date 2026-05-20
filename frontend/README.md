# PDF2GPU Frontend

React + TypeScript + Material-UI frontend aplikacija za PDF2GPU RAG sistem.

## Tehnologije

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool i dev server
- **Material-UI (MUI)** - UI komponente
- **React Router** - Routing
- **TanStack Query** - Server state management
- **Axios** - HTTP client

## Instalacija

```bash
# Instaliraj dependencies
npm install

# Kopiraj .env fajl
cp .env.example .env
```

## Pokretanje

```bash
# Development server (port 3000)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

## Struktura projekta

```
frontend/
├── src/
│   ├── api/              # API client i servisi
│   │   ├── client.ts     # Axios instance
│   │   ├── collections.ts
│   │   ├── pdfs.ts
│   │   └── search.ts
│   ├── hooks/            # React Query hooks
│   │   ├── useCollections.ts
│   │   ├── usePDFs.ts
│   │   └── useSearch.ts
│   ├── pages/            # Stranice
│   │   ├── CollectionsPage.tsx
│   │   ├── CollectionDetailPage.tsx
│   │   ├── SearchPage.tsx
│   │   └── PDFDetailPage.tsx
│   ├── types/            # TypeScript tipovi
│   │   └── api.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   ├── theme.ts          # MUI tema
│   └── vite-env.d.ts     # Vite type definitions
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## API Endpoints

Frontend komunicira sa backend API-jem na `http://localhost:8000`:

- `/api/collections` - Upravljanje kolekcijama
- `/api/pdfs` - Upload i upravljanje PDF-ovima
- `/api/search` - Pretraga i RAG

## Razvoj

### Dodavanje nove stranice

1. Kreiraj komponent u `src/pages/`
2. Dodaj route u `App.tsx`
3. Kreiraj potrebne hooks u `src/hooks/`

### Dodavanje novog API servisa

1. Kreiraj servis u `src/api/`
2. Dodaj tipove u `src/types/api.ts`
3. Kreiraj React Query hooks u `src/hooks/`

## Status

**FAZA 4 - Frontend Osnova**: ✅ Završeno

- ✅ Vite + React + TypeScript setup
- ✅ Material-UI integracija
- ✅ React Router konfiguracija
- ✅ API client (Axios)
- ✅ TypeScript tipovi
- ✅ React Query hooks
- ✅ Osnovne stranice (placeholder)

## Sledeće faze

- **FAZA 5**: Chat i WebSocket integracija
- **FAZA 6**: Evaluacija i testiranje
- **FAZA 7**: Settings i konfiguracija
- **FAZA 8**: Finalizacija i deployment
