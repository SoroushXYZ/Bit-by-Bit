import { Box, Container } from '@mui/material';
import MobileNavbar from './MobileNavbar';

interface MobileLayoutProps {
  children: React.ReactNode;
}

/**
 * Mobile-specific layout component
 * Optimized for phone screens with vertical scrolling
 */
export default function MobileLayout({ children }: MobileLayoutProps) {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: 'background.default',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <MobileNavbar />
      <Box
        sx={{
          flex: 1,
          pb: 2,
        }}
      >
        <Container maxWidth="sm" disableGutters>
          {children}
        </Container>
      </Box>
    </Box>
  );
}

