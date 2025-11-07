import { Box, Container } from '@mui/material';
import DesktopNavbar from './DesktopNavbar';

interface DesktopLayoutProps {
  children: React.ReactNode;
}

/**
 * Desktop-specific layout component
 * Optimized for larger screens with grid-based layouts
 */
export default function DesktopLayout({ children }: DesktopLayoutProps) {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: 'background.default',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <DesktopNavbar />
      <Box
        sx={{
          flex: 1,
          py: 4,
        }}
      >
        <Container maxWidth="lg">
          {children}
        </Container>
      </Box>
    </Box>
  );
}

