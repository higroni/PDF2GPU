/**
 * Search Page
 * Stranica za pretragu dokumenata
 */
import { Container, Typography, Box } from '@mui/material';

export default function SearchPage() {
  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Pretraga
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Pretraga dokumenata - u razvoju
        </Typography>
        {/* TODO: Implementirati search funkcionalnost */}
      </Box>
    </Container>
  );
}

// Made with Bob
