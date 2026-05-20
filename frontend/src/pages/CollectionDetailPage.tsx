/**
 * Collection Detail Page
 * Detalji kolekcije i PDF-ovi
 */
import { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Paper,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Description as PdfIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  MoreVert as MoreVertIcon,
  CloudUpload as UploadIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import PDFUpload from '../components/PDFUpload';
import { apiClient } from '../api/client';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function CollectionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const collectionId = id ? parseInt(id) : 0;
  const [tabValue, setTabValue] = useState(0);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPdfId, setSelectedPdfId] = useState<number | null>(null);

  // Fetch collection details
  const {
    data: collection,
    isLoading: collectionLoading,
    error: collectionError,
    refetch: refetchCollection,
  } = useQuery({
    queryKey: ['collection', collectionId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/collections/${collectionId}`);
      return response.data;
    },
  });

  // Fetch PDFs in collection
  const {
    data: pdfs,
    isLoading: pdfsLoading,
    error: pdfsError,
    refetch: refetchPdfs,
  } = useQuery({
    queryKey: ['collection-pdfs', collectionId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/collections/${collectionId}/pdfs`);
      return response.data;
    },
  });

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, pdfId: number) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedPdfId(pdfId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedPdfId(null);
  };

  const handleDeletePdf = async () => {
    if (!selectedPdfId) return;
    
    if (window.confirm('Da li ste sigurni da želite da obrišete ovaj PDF?')) {
      try {
        await apiClient.delete(`/api/pdfs/${selectedPdfId}`);
        refetchPdfs();
        refetchCollection();
      } catch (err) {
        console.error('Failed to delete PDF:', err);
        alert('Greška pri brisanju PDF-a');
      }
    }
    handleMenuClose();
  };

  const handleDownloadPdf = async () => {
    if (!selectedPdfId) return;
    
    try {
      const response = await apiClient.get(`/api/pdfs/${selectedPdfId}/download`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `document-${selectedPdfId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('Greška pri preuzimanju PDF-a');
    }
    handleMenuClose();
  };

  const handleUploadComplete = () => {
    refetchPdfs();
    refetchCollection();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('sr-RS', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (collectionLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (collectionError || !collection) {
    return (
      <Container>
        <Box mt={4}>
          <Alert severity="error">Greška pri učitavanju kolekcije</Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        {/* Header */}
        <Box mb={4}>
          <Typography variant="h4" component="h1" gutterBottom>
            {collection.name}
          </Typography>
          {collection.description && (
            <Typography variant="body1" color="text.secondary" paragraph>
              {collection.description}
            </Typography>
          )}
          
          {/* Collection Stats */}
          <Box display="flex" gap={1} flexWrap="wrap" mt={2}>
            <Chip
              icon={<PdfIcon />}
              label={`${collection.pdf_count || 0} PDF-ova`}
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`Chunking: ${collection.chunking_strategy}`}
              variant="outlined"
            />
            {collection.is_active && (
              <Chip label="Aktivna" color="success" variant="outlined" />
            )}
          </Box>
        </Box>

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
            <Tab icon={<PdfIcon />} label="PDF Dokumenti" iconPosition="start" />
            <Tab icon={<UploadIcon />} label="Upload" iconPosition="start" />
            <Tab icon={<InfoIcon />} label="Informacije" iconPosition="start" />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <TabPanel value={tabValue} index={0}>
          {pdfsLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : pdfsError ? (
            <Alert severity="error">Greška pri učitavanju PDF-ova</Alert>
          ) : pdfs && pdfs.length === 0 ? (
            <Alert severity="info">
              Nema PDF-ova u ovoj kolekciji. Pređite na "Upload" tab da dodate dokumente.
            </Alert>
          ) : (
            <Grid container spacing={3}>
              {pdfs?.map((pdf: any) => (
                <Grid item xs={12} sm={6} md={4} key={pdf.id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="flex-start" mb={2}>
                        <PdfIcon color="error" sx={{ mr: 1, mt: 0.5 }} />
                        <Box flexGrow={1}>
                          <Typography variant="h6" component="h3" noWrap>
                            {pdf.filename}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatFileSize(pdf.file_size)}
                          </Typography>
                        </Box>
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuOpen(e, pdf.id)}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </Box>

                      <Divider sx={{ my: 1 }} />

                      <Box display="flex" flexDirection="column" gap={0.5}>
                        <Typography variant="caption" color="text.secondary">
                          Chunks: {pdf.chunk_count || 0}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Uploaded: {formatDate(pdf.created_at)}
                        </Typography>
                        {pdf.processed_at && (
                          <Chip
                            label="Processed"
                            size="small"
                            color="success"
                            sx={{ mt: 1, width: 'fit-content' }}
                          />
                        )}
                      </Box>
                    </CardContent>

                    <CardActions>
                      <Button
                        size="small"
                        onClick={() => navigate(`/pdfs/${pdf.id}`)}
                      >
                        Detalji
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        startIcon={<DeleteIcon />}
                        onClick={async () => {
                          if (window.confirm('Da li ste sigurni da želite da obrišete ovaj PDF?')) {
                            try {
                              await apiClient.delete(`/api/pdfs/${pdf.id}`);
                              refetchPdfs();
                              refetchCollection();
                            } catch (err) {
                              console.error('Failed to delete PDF:', err);
                              alert('Greška pri brisanju PDF-a');
                            }
                          }
                        }}
                      >
                        Obriši
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <PDFUpload
            collectionId={collectionId}
            onUploadComplete={handleUploadComplete}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Informacije o kolekciji
            </Typography>
            <Box display="flex" flexDirection="column" gap={2} mt={2}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  ID
                </Typography>
                <Typography variant="body1">{collection.id}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Ime
                </Typography>
                <Typography variant="body1">{collection.name}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Opis
                </Typography>
                <Typography variant="body1">
                  {collection.description || 'Nema opisa'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Chunking strategija
                </Typography>
                <Typography variant="body1">{collection.chunking_strategy}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Broj PDF-ova
                </Typography>
                <Typography variant="body1">{collection.pdf_count || 0}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Kreirana
                </Typography>
                <Typography variant="body1">
                  {formatDate(collection.created_at)}
                </Typography>
              </Box>
              {collection.updated_at && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Ažurirana
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(collection.updated_at)}
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </TabPanel>

        {/* Context Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleDownloadPdf}>
            <ListItemIcon>
              <DownloadIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Preuzmi</ListItemText>
          </MenuItem>
          <MenuItem onClick={handleDeletePdf}>
            <ListItemIcon>
              <DeleteIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Obriši</ListItemText>
          </MenuItem>
        </Menu>
      </Box>
    </Container>
  );
}

// Made with Bob
