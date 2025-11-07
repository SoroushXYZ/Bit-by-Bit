import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button,
  Container,
  useTheme,
  alpha,
} from '@mui/material';
import { useRouter } from 'next/router';
import ThemeToggle from '@/components/theme/ThemeToggle';

/**
 * Desktop-optimized navbar with horizontal navigation
 */
export default function DesktopNavbar() {
  const router = useRouter();
  const theme = useTheme();

  const menuItems = [
    { label: 'Home', href: '/' },
    { label: 'Newsletters', href: '/newsletters' },
    { label: 'About', href: '/about' },
  ];

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        backgroundColor: alpha(theme.palette.background.paper, 0.8),
        backdropFilter: 'blur(10px)',
        color: 'text.primary',
        borderBottom: 1,
        borderColor: 'divider',
      }}
    >
      <Container maxWidth="lg">
        <Toolbar
          disableGutters
          sx={{
            minHeight: 80,
            justifyContent: 'space-between',
            py: 1,
          }}
        >
          <Typography
            variant="h4"
            component="div"
            sx={{
              fontWeight: 800,
              letterSpacing: '-0.02em',
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              cursor: 'pointer',
              '&:hover': {
                opacity: 0.9,
              },
            }}
            onClick={() => router.push('/')}
          >
            Bit-by-Bit
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {menuItems.map((item) => {
              const isActive = router.pathname === item.href;
              return (
                <Button
                  key={item.label}
                  onClick={() => router.push(item.href)}
                  sx={{
                    color: isActive ? 'primary.main' : 'text.secondary',
                    fontWeight: isActive ? 600 : 400,
                    textTransform: 'none',
                    fontSize: '1rem',
                    px: 2,
                    py: 1,
                    borderRadius: 2,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.08),
                      color: 'primary.main',
                    },
                    ...(isActive && {
                      backgroundColor: alpha(theme.palette.primary.main, 0.12),
                    }),
                  }}
                >
                  {item.label}
                </Button>
              );
            })}
            <ThemeToggle />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

