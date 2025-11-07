import { IconButton, Tooltip, Box } from '@mui/material';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import BrightnessAutoIcon from '@mui/icons-material/BrightnessAuto';
import { useThemeContext } from '@/contexts/ThemeContext';
import { useTheme } from '@mui/material/styles';

/**
 * Theme toggle button component
 * Cycles through: light -> dark -> system -> light
 */
export default function ThemeToggle() {
  const { mode, resolvedMode, toggleTheme, mounted } = useThemeContext();
  const theme = useTheme();

  // Don't render until mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <IconButton
        disabled
        sx={{
          color: 'text.secondary',
          width: 40,
          height: 40,
        }}
      >
        <BrightnessAutoIcon />
      </IconButton>
    );
  }

  // Show icon based on resolved mode (what user actually sees)
  const getIcon = () => {
    return resolvedMode === 'dark' ? <DarkModeIcon /> : <LightModeIcon />;
  };

  // Tooltip shows what will happen when clicked
  const getTooltip = () => {
    if (mode === 'system') {
      return `Currently following system (${resolvedMode}). Click to switch to ${resolvedMode === 'light' ? 'dark' : 'light'} mode`;
    }
    return `Switch to ${resolvedMode === 'light' ? 'dark' : 'light'} mode`;
  };

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    toggleTheme();
  };

  return (
    <Tooltip title={getTooltip()} arrow>
      <IconButton
        onClick={handleClick}
        color="inherit"
        aria-label="Toggle theme"
        sx={{
          color: 'text.secondary',
          '&:hover': {
            color: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        {getIcon()}
      </IconButton>
    </Tooltip>
  );
}

