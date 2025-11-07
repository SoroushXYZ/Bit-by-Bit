import { useDevice } from '@/hooks/useDevice';
import MobileLayout from '@/components/layout/MobileLayout';
import DesktopLayout from '@/components/layout/DesktopLayout';
import MobileHome from '@/components/mobile/MobileHome';
import DesktopHome from '@/components/desktop/DesktopHome';
import { useNewsletterData } from '@/hooks/useNewsletterData';
import { Box, Typography, Paper, CircularProgress, Alert, Button } from '@mui/material';

/**
 * Home page with completely different mobile and desktop experiences
 * Uses device detection to render appropriate layout and content
 */
export default function Home() {
  const { isMobile } = useDevice();
  const { data, isLoading, error, refreshData } = useNewsletterData();

  // Completely separate experiences based on device type
  if (isMobile) {
    return (
      <MobileLayout>
        <MobileHome />
        <Box sx={{ mt: 2, p: 2 }}>
          <Typography variant="h6" gutterBottom>Backend Data (Raw)</Typography>
          {isLoading && <CircularProgress />}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
              <Button onClick={refreshData} size="small" sx={{ ml: 2 }}>
                Retry
              </Button>
            </Alert>
          )}
          {data && (
            <Paper sx={{ p: 2, mt: 2, overflow: 'auto' }}>
              <pre style={{ margin: 0, fontSize: '0.75rem' }}>
                {JSON.stringify(data, null, 2)}
              </pre>
            </Paper>
          )}
        </Box>
      </MobileLayout>
    );
  }

  return (
    <DesktopLayout>
      <DesktopHome />
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>Backend Data (Raw)</Typography>
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        )}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
            <Button onClick={refreshData} size="small" sx={{ ml: 2 }}>
              Retry
            </Button>
          </Alert>
        )}
        {data && (
          <Paper sx={{ p: 3, mt: 2, overflow: 'auto', maxHeight: '600px' }}>
            <pre style={{ margin: 0, fontSize: '0.875rem' }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          </Paper>
        )}
      </Box>
    </DesktopLayout>
  );
}
