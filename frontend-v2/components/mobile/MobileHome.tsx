import { Box, Typography, Paper, Stack } from '@mui/material';

/**
 * Mobile-specific home page component
 * Completely different UI/UX from desktop
 */
export default function MobileHome() {
  return (
    <Box sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            Bit-by-Bit
          </Typography>
          <Typography variant="h6" component="h2" color="text.secondary" gutterBottom>
            Newsletter
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Mobile Experience
          </Typography>
        </Paper>

        <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
          <Typography variant="body1">
            This is the mobile-optimized view with a completely different design and interaction pattern.
          </Typography>
        </Paper>
      </Stack>
    </Box>
  );
}

