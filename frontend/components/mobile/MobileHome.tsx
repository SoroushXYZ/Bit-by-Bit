import { Box, Stack, CircularProgress, Alert, Button, Typography } from '@mui/material';
import DatePicker from '@/components/ui/DatePicker';
import { useNewsletterContext } from '@/contexts/NewsletterContext';
import MobileNewsCard from './MobileNewsCard';
import MobileGitRepoCard from './MobileGitRepoCard';
import MobileStockCard from './MobileStockCard';
import { Component, HeadlineComponent, SecondaryComponent, QuickLinkComponent, GitRepoComponent, StockComponent } from '@/types/components';

/**
 * Mobile-specific home page component
 * Displays news in scrollable card layout
 */
export default function MobileHome() {
  const { 
    layout, 
    isLoading, 
    error, 
    refreshData,
    selectedDate, 
    availableDates, 
    newsletterDate, 
    selectDate 
  } = useNewsletterContext();

  // Filter and sort components for mobile display
  // Order: Headlines/Secondary -> GitRepos -> QuickLinks -> Stocks
  const headlinesAndSecondary = layout?.components
    .filter((comp: Component) => 
      comp.type === 'headline' || comp.type === 'secondary'
    )
    .sort((a: Component, b: Component) => {
      if (a.type === 'headline' && b.type !== 'headline') return -1;
      if (a.type !== 'headline' && b.type === 'headline') return 1;
      const aPriority = 'priority' in a ? a.priority : 0;
      const bPriority = 'priority' in b ? b.priority : 0;
      return bPriority - aPriority;
    }) || [];

  const gitRepos = layout?.components
    .filter((comp: Component) => comp.type === 'gitRepo') || [];

  const quickLinks = layout?.components
    .filter((comp: Component) => comp.type === 'quickLink') || [];

  const stocks = layout?.components
    .filter((comp: Component) => comp.type === 'stock') || [];

  return (
    <Box sx={{ pb: 4 }}>
      <Stack spacing={2} sx={{ px: 2, pt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 1 }}>
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
              <Button color="inherit" size="small" onClick={refreshData}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {!isLoading && !error && (
          <Box>
            {/* Headlines and Secondary Articles */}
            {headlinesAndSecondary.map((component: Component) => (
              <MobileNewsCard key={component.id} component={component as HeadlineComponent | SecondaryComponent | QuickLinkComponent} />
            ))}

            {/* Git Repos */}
            {gitRepos.map((component: Component) => (
              <MobileGitRepoCard key={component.id} component={component as GitRepoComponent} />
            ))}

            {/* Quick Links */}
            {quickLinks.map((component: Component) => (
              <MobileNewsCard key={component.id} component={component as QuickLinkComponent} />
            ))}

            {/* Stocks Section */}
            {stocks.length > 0 && (
              <>
                <Typography
                  variant="h6"
                  sx={{
                    mt: 3,
                    mb: 2,
                    fontWeight: 600,
                    fontSize: '1.1rem',
                    color: 'text.primary',
                  }}
                >
                  Stocks
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    justifyContent: 'center',
                    gap: 1.5,
                    mb: 2,
                  }}
                >
                  {stocks.map((component: Component) => (
                    <Box 
                      key={component.id} 
                      sx={{ 
                        width: { xs: 'calc(50% - 0.75rem)', sm: 'calc(33.333% - 1rem)' },
                        minWidth: '120px',
                        maxWidth: { xs: '200px', sm: '180px' },
                      }}
                    >
                      <MobileStockCard component={component as StockComponent} />
                    </Box>
                  ))}
                </Box>
              </>
            )}

            {headlinesAndSecondary.length === 0 && 
             gitRepos.length === 0 && 
             quickLinks.length === 0 && 
             stocks.length === 0 && (
              <Alert severity="info">
                No news available for this date.
              </Alert>
            )}
          </Box>
        )}
      </Stack>
    </Box>
  );
}

