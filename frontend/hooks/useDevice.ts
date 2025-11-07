import { useMediaQuery, useTheme } from '@mui/material';

/**
 * Hook to detect if the current device is mobile
 * Uses Material UI's breakpoint system (default: 'md' = 900px)
 */
export function useDevice() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return {
    isMobile,
    isDesktop: !isMobile,
  };
}

