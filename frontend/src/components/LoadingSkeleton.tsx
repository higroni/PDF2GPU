/**
 * LoadingSkeleton Component
 * Reusable skeleton loaders za različite komponente
 */
import React from 'react';
import { Box, Card, CardContent, Skeleton, Grid } from '@mui/material';

interface LoadingSkeletonProps {
  variant?: 'card' | 'list' | 'detail' | 'chat';
  count?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'card',
  count = 3,
}) => {
  if (variant === 'card') {
    return (
      <Grid container spacing={3}>
        {Array.from({ length: count }).map((_, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Skeleton variant="circular" width={40} height={40} sx={{ mr: 1 }} />
                  <Skeleton variant="text" width="60%" height={32} />
                </Box>
                <Skeleton variant="text" width="100%" />
                <Skeleton variant="text" width="80%" />
                <Box display="flex" gap={1} mt={2}>
                  <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 1 }} />
                  <Skeleton variant="rectangular" width={100} height={24} sx={{ borderRadius: 1 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  if (variant === 'list') {
    return (
      <Box>
        {Array.from({ length: count }).map((_, index) => (
          <Box key={index} mb={2}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
                  <Box flexGrow={1}>
                    <Skeleton variant="text" width="40%" height={24} />
                    <Skeleton variant="text" width="60%" height={20} />
                  </Box>
                  <Skeleton variant="rectangular" width={80} height={36} sx={{ borderRadius: 1 }} />
                </Box>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>
    );
  }

  if (variant === 'detail') {
    return (
      <Box>
        <Skeleton variant="text" width="50%" height={48} sx={{ mb: 2 }} />
        <Skeleton variant="text" width="80%" height={24} sx={{ mb: 3 }} />
        <Box display="flex" gap={1} mb={4}>
          <Skeleton variant="rectangular" width={100} height={32} sx={{ borderRadius: 1 }} />
          <Skeleton variant="rectangular" width={120} height={32} sx={{ borderRadius: 1 }} />
          <Skeleton variant="rectangular" width={80} height={32} sx={{ borderRadius: 1 }} />
        </Box>
        <Skeleton variant="rectangular" width="100%" height={400} sx={{ borderRadius: 2 }} />
      </Box>
    );
  }

  if (variant === 'chat') {
    return (
      <Box>
        {Array.from({ length: count }).map((_, index) => (
          <Box
            key={index}
            display="flex"
            justifyContent={index % 2 === 0 ? 'flex-end' : 'flex-start'}
            mb={2}
          >
            <Box display="flex" gap={1} maxWidth="75%">
              {index % 2 !== 0 && (
                <Skeleton variant="circular" width={32} height={32} />
              )}
              <Skeleton
                variant="rectangular"
                width={300}
                height={80}
                sx={{ borderRadius: 2 }}
              />
              {index % 2 === 0 && (
                <Skeleton variant="circular" width={32} height={32} />
              )}
            </Box>
          </Box>
        ))}
      </Box>
    );
  }

  return null;
};

export default LoadingSkeleton;

// Made with Bob
