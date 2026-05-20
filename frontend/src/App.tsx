/**
 * Main App Component
 * Glavni komponent aplikacije sa routing-om
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import { ToastProvider } from './components/Toast';

// Pages
import CollectionsPage from './pages/CollectionsPage';
import CollectionDetailPage from './pages/CollectionDetailPage';
import SearchPage from './pages/SearchPage';
import PDFDetailPage from './pages/PDFDetailPage';
import ChatPage from './pages/ChatPage';
import TestExamplesPage from './pages/TestExamplesPage';
import EvaluationsPage from './pages/EvaluationsPage';
import EvaluationConfigPage from './pages/EvaluationConfigPage';
import EvaluationComparePage from './pages/EvaluationComparePage';

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <ToastProvider>
            <CssBaseline />
            <BrowserRouter>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/collections" replace />} />
                  <Route path="/collections" element={<CollectionsPage />} />
                  <Route path="/collections/:id" element={<CollectionDetailPage />} />
                  <Route path="/search" element={<SearchPage />} />
                  <Route path="/pdfs/:id" element={<PDFDetailPage />} />
                  <Route path="/chat" element={<ChatPage />} />
                  <Route path="/test-examples" element={<TestExamplesPage />} />
                  <Route path="/evaluations" element={<EvaluationsPage />} />
                  <Route path="/evaluations/config" element={<EvaluationConfigPage />} />
                  <Route path="/evaluations/compare/:id1/:id2" element={<EvaluationComparePage />} />
                </Routes>
              </Layout>
            </BrowserRouter>
          </ToastProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;

// Made with Bob
