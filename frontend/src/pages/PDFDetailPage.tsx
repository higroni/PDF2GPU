/**
 * PDF Detail Page
 * Detalji PDF dokumenta
 */
import { Container, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { useParams } from 'react-router-dom';
import { usePDF } from '@/hooks/usePDFs';

export default function PDFDetailPage() {
  const { id } = useParams<{ id: string }>();
  const pdfId = id ? parseInt(id) : 0;
  const { data: pdf, isLoading, error } = usePDF(pdfId);

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !pdf) {
    return (
      <Container>
        <Box mt={4}>
          <Alert severity="error">Greška pri učitavanju PDF-a</Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          {pdf.original_filename}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Status: {pdf.processing_status}
        </Typography>
        {/* TODO: Dodati više detalja o PDF-u */}
      </Box>
    </Container>
  );
}

// Made with Bob
