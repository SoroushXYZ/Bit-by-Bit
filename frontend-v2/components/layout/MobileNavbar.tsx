import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  useTheme,
} from '@mui/material';
import ThemeToggle from '@/components/theme/ThemeToggle';

/**
 * Mobile-optimized navbar with drawer menu
 */
export default function MobileNavbar() {
  const theme = useTheme();

  return (
    <>
      <AppBar
        position="sticky"
        elevation={2}
        sx={{
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between', minHeight: 64 }}>
          <Typography
            variant="h5"
            component="div"
            sx={{
              fontWeight: 700,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Bit-by-Bit
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1, justifyContent: 'flex-end' }}>
            <ThemeToggle />
          </Box>
        </Toolbar>
      </AppBar>
    </>
  );
}

