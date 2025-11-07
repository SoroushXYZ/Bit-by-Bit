import { Box, Typography, Paper, Stack } from '@mui/material';

/**
 * Desktop-specific home page component
 * Completely different UI/UX from mobile
 */
export default function DesktopHome() {
  return (
    <Box>
      <Stack spacing={3}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Typography variant="h2" component="h1" gutterBottom>
            Bit-by-Bit Newsletter
          </Typography>
          <Typography variant="h5" component="h2" gutterBottom color="text.secondary">
            Frontend V2
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
            Desktop Experience - Optimized for larger screens with grid layouts
          </Typography>
        </Paper>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' },
            gap: 3,
          }}
        >
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Grid Layout
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Desktop-optimized grid-based newsletter layout
            </Typography>
          </Paper>

          <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Rich Content
            </Typography>
            <Typography variant="body2" color="text.secondary">
              More space for detailed content and interactions
            </Typography>
          </Paper>
        </Box>
      </Stack>
    </Box>
  );
}

