import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Container,
  useTheme,
  alpha,
  IconButton,
  Tooltip,
} from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';
import { useRouter } from 'next/router';
import ThemeToggle from '@/components/theme/ThemeToggle';

/**
 * Desktop-optimized navbar with horizontal navigation
 */
export default function DesktopNavbar() {
  const router = useRouter();
  const theme = useTheme();

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
              fontFamily: '"Press Start 2P", monospace',
              fontWeight: 400,
              fontSize: '1.25rem',
              letterSpacing: '0.05em',
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

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flex: 1, justifyContent: 'flex-end' }}>
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
      </Container>
    </AppBar>
  );
}

