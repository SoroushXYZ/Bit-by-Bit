import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  useTheme,
  IconButton,
  Tooltip,
  alpha,
} from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';
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
            <Tooltip title="View on GitHub">
              <IconButton
                component="a"
                href="https://github.com/SoroushXYZ/Bit-by-Bit"
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  color: 'text.primary',
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  },
                }}
              >
                <GitHubIcon />
              </IconButton>
            </Tooltip>
            <ThemeToggle />
          </Box>
        </Toolbar>
      </AppBar>
    </>
  );
}

