/**
 * Collections Page
 * Stranica za prikaz i upravljanje kolekcijama
 */
import { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  TextField,
  InputAdornment,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import {
  Add as AddIcon,
  Folder as FolderIcon,
  CheckCircle as CheckCircleIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  ViewModule as GridViewIcon,
  ViewList as ListViewIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useCollections } from '../hooks/useCollections';
import CollectionManager from '../components/CollectionManager';
import { apiClient } from '../api/client';

export default function CollectionsPage() {
  const navigate = useNavigate();
  const { data: collections, isLoading, error, refetch } = useCollections();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [managerOpen, setManagerOpen] = useState(false);
  const [managerMode, setManagerMode] = useState<'create' | 'edit'>('create');
  const [editingCollection, setEditingCollection] = useState<any>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuCollectionId, setMenuCollectionId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Box mt={4}>
          <Alert severity="error">Greška pri učitavanju kolekcija</Alert>
        </Box>
      </Container>
    );
  }

  const handleCreateClick = () => {
    setManagerMode('create');
    setEditingCollection(null);
    setManagerOpen(true);
  };

  const handleEditClick = (collection: any) => {
    setManagerMode('edit');
    setEditingCollection(collection);
    setManagerOpen(true);
    setAnchorEl(null);
  };

  const handleDeleteClick = async (collectionId: number) => {
    if (window.confirm('Da li ste sigurni da želite da obrišete ovu kolekciju?')) {
      try {
        await apiClient.delete(`/api/collections/${collectionId}`);
        refetch();
      } catch (err) {
        console.error('Failed to delete collection:', err);
        alert('Greška pri brisanju kolekcije');
      }
    }
    setAnchorEl(null);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, collectionId: number) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setMenuCollectionId(collectionId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuCollectionId(null);
  };

  const handleManagerSuccess = () => {
    refetch();
  };

  const filteredCollections = collections?.filter((collection) =>
    collection.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    collection.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Kolekcije
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateClick}
          >
            Nova kolekcija
          </Button>
        </Box>

        {/* Search and View Toggle */}
        <Box display="flex" gap={2} mb={3} alignItems="center">
          <TextField
            placeholder="Pretraži kolekcije..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            sx={{ flexGrow: 1 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, newMode) => newMode && setViewMode(newMode)}
            size="small"
          >
            <ToggleButton value="grid">
              <GridViewIcon />
            </ToggleButton>
            <ToggleButton value="list">
              <ListViewIcon />
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Statistics */}
        {collections && collections.length > 0 && (
          <Box mb={3} display="flex" gap={2}>
            <Chip
              label={`Ukupno: ${collections.length} kolekcija`}
              color="primary"
              variant="outlined"
            />
            <Chip
              label={`PDF-ova: ${collections.reduce((sum, c) => sum + (c.pdf_count || 0), 0)}`}
              color="secondary"
              variant="outlined"
            />
          </Box>
        )}

        {filteredCollections && filteredCollections.length === 0 ? (
          <Alert severity="info">
            {searchQuery
              ? 'Nema kolekcija koje odgovaraju pretrazi.'
              : 'Nema kreiranih kolekcija. Kreirajte prvu kolekciju da biste počeli.'}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {filteredCollections?.map((collection) => (
              <Grid item xs={12} sm={viewMode === 'list' ? 12 : 6} md={viewMode === 'list' ? 12 : 4} key={collection.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    cursor: 'pointer',
                    '&:hover': {
                      boxShadow: 6,
                    },
                  }}
                  onClick={() => navigate(`/collections/${collection.id}`)}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" alignItems="center" mb={2}>
                      <FolderIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6" component="h2" sx={{ flexGrow: 1 }}>
                        {collection.name}
                      </Typography>
                      {collection.is_active && (
                        <CheckCircleIcon
                          color="success"
                          sx={{ mr: 1 }}
                          titleAccess="Aktivna kolekcija"
                        />
                      )}
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, collection.id)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </Box>

                    {collection.description && (
                      <Typography variant="body2" color="text.secondary" mb={2}>
                        {collection.description}
                      </Typography>
                    )}

                    <Box display="flex" gap={1} flexWrap="wrap">
                      <Chip
                        label={`${collection.pdf_count || 0} PDF-ova`}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={collection.chunking_strategy}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/collections/${collection.id}`);
                      }}
                    >
                      Otvori
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Collection Manager Dialog */}
        <CollectionManager
          open={managerOpen}
          onClose={() => setManagerOpen(false)}
          onSuccess={handleManagerSuccess}
          collection={editingCollection}
          mode={managerMode}
        />

        {/* Context Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem
            onClick={() => {
              const collection = collections?.find((c) => c.id === menuCollectionId);
              if (collection) handleEditClick(collection);
            }}
          >
            <ListItemIcon>
              <EditIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Izmeni</ListItemText>
          </MenuItem>
          <MenuItem
            onClick={() => {
              if (menuCollectionId) handleDeleteClick(menuCollectionId);
            }}
          >
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
