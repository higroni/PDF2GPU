/**
 * PDFUpload Component
 * Komponenta za upload PDF fajlova sa drag & drop funkcionalnoscu
 */
import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  Typography,
  LinearProgress,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as PdfIcon,
  Delete as DeleteIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { apiClient } from '../api/client';

interface PDFUploadProps {
  collectionId: number;
  onUploadComplete?: () => void;
}

interface UploadFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

export const PDFUpload: React.FC<PDFUploadProps> = ({ collectionId, onUploadComplete }) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    const pdfFiles = droppedFiles.filter((file) => file.type === 'application/pdf');

    if (pdfFiles.length !== droppedFiles.length) {
      alert('Samo PDF fajlovi su dozvoljeni!');
    }

    addFiles(pdfFiles);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  }, []);

  const addFiles = (newFiles: File[]) => {
    const uploadFiles: UploadFile[] = newFiles.map((file) => ({
      file,
      status: 'pending',
      progress: 0,
    }));
    setFiles((prev) => [...prev, ...uploadFiles]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (uploadFile: UploadFile, index: number) => {
    const formData = new FormData();
    formData.append('file', uploadFile.file);
    formData.append('collection_id', collectionId.toString());

    try {
      // Update status to uploading
      setFiles((prev) =>
        prev.map((f, i) => (i === index ? { ...f, status: 'uploading' as const } : f))
      );

      const response = await apiClient.post('/api/pdfs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          setFiles((prev) =>
            prev.map((f, i) => (i === index ? { ...f, progress } : f))
          );
        },
      });

      // Update status to success
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index ? { ...f, status: 'success' as const, progress: 100 } : f
        )
      );

      if (onUploadComplete) {
        onUploadComplete();
      }
    } catch (error: any) {
      console.error('Upload failed:', error);
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index
            ? {
                ...f,
                status: 'error' as const,
                error: error.response?.data?.detail || 'Upload failed',
              }
            : f
        )
      );
    }
  };

  const uploadAll = async () => {
    const pendingFiles = files
      .map((f, index) => ({ file: f, index }))
      .filter((f) => f.file.status === 'pending');

    for (const { file, index } of pendingFiles) {
      await uploadFile(file, index);
    }
  };

  const clearCompleted = () => {
    setFiles((prev) => prev.filter((f) => f.status !== 'success'));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <PdfIcon />;
    }
  };

  const pendingCount = files.filter((f) => f.status === 'pending').length;
  const uploadingCount = files.filter((f) => f.status === 'uploading').length;
  const successCount = files.filter((f) => f.status === 'success').length;
  const errorCount = files.filter((f) => f.status === 'error').length;

  return (
    <Box>
      {/* Drop Zone */}
      <Paper
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        sx={{
          p: 4,
          textAlign: 'center',
          border: '2px dashed',
          borderColor: isDragging ? 'primary.main' : 'grey.300',
          backgroundColor: isDragging ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.3s',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Prevucite PDF fajlove ovde
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          ili
        </Typography>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadIcon />}
          sx={{ mt: 2 }}
        >
          Izaberite fajlove
          <input
            type="file"
            hidden
            multiple
            accept="application/pdf"
            onChange={handleFileSelect}
          />
        </Button>
      </Paper>

      {/* File List */}
      {files.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Fajlovi ({files.length})
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {successCount > 0 && (
                <Chip
                  label={`${successCount} uspešno`}
                  color="success"
                  size="small"
                />
              )}
              {errorCount > 0 && (
                <Chip
                  label={`${errorCount} greška`}
                  color="error"
                  size="small"
                />
              )}
              {pendingCount > 0 && (
                <Chip
                  label={`${pendingCount} čeka`}
                  color="default"
                  size="small"
                />
              )}
            </Box>
          </Box>

          <List>
            {files.map((uploadFile, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  uploadFile.status === 'pending' && (
                    <IconButton edge="end" onClick={() => removeFile(index)}>
                      <DeleteIcon />
                    </IconButton>
                  )
                }
              >
                <ListItemIcon>{getStatusIcon(uploadFile.status)}</ListItemIcon>
                <ListItemText
                  primary={uploadFile.file.name}
                  secondary={
                    <Box>
                      <Typography variant="caption" display="block">
                        {formatFileSize(uploadFile.file.size)}
                      </Typography>
                      {uploadFile.status === 'uploading' && (
                        <LinearProgress
                          variant="determinate"
                          value={uploadFile.progress}
                          sx={{ mt: 1 }}
                        />
                      )}
                      {uploadFile.status === 'error' && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                          {uploadFile.error}
                        </Alert>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>

          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Button
              variant="contained"
              onClick={uploadAll}
              disabled={pendingCount === 0 || uploadingCount > 0}
              startIcon={<UploadIcon />}
            >
              Upload sve ({pendingCount})
            </Button>
            {successCount > 0 && (
              <Button variant="outlined" onClick={clearCompleted}>
                Obriši uspešne
              </Button>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default PDFUpload;

// Made with Bob
