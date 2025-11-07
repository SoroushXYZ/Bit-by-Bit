import { Box, Typography, Paper, Stack, CircularProgress, Alert, Button } from '@mui/material';
import DynamicGridLayout from '@/components/layout/DynamicGridLayout';
import DatePicker from '@/components/ui/DatePicker';
import { NewsletterLayout } from '@/types/components';
import { useNewsletterContext } from '@/contexts/NewsletterContext';

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
  const { selectedDate, availableDates, newsletterDate, selectDate } = useNewsletterContext();

  return (
    <Box>
      <Stack spacing={3}>
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <DatePicker
            selectedDate={selectedDate}
            availableDates={availableDates}
            newsletterDate={newsletterDate}
            onDateSelect={selectDate}
          />
        </Box>

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

