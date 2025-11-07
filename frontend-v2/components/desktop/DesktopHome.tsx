import { Box, Typography, Paper, Stack, CircularProgress, Alert, Button } from '@mui/material';
import DynamicGridLayout from '@/components/layout/DynamicGridLayout';
import { NewsletterLayout } from '@/types/components';

interface DesktopHomeProps {
  layout: NewsletterLayout | null;
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
}

/**
 * Desktop-specific home page component
 * Completely different UI/UX from mobile
 */
export default function DesktopHome({ layout, isLoading, error, onRetry }: DesktopHomeProps) {
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
        </Paper>

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert 
            severity="error" 
            action={
              <Button color="inherit" size="small" onClick={onRetry}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {layout && !isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <DynamicGridLayout layout={layout} />
          </Box>
        )}

        {!layout && !isLoading && !error && (
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              No newsletter data available
            </Typography>
          </Paper>
        )}
      </Stack>
    </Box>
  );
}

