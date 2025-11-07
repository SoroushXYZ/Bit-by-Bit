import type { AppProps } from 'next/app';
import { ThemeProvider as MUIThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { useMemo } from 'react';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { useThemeContext } from '@/contexts/ThemeContext';
import '@/styles/globals.css';

function ThemedApp({ Component, pageProps }: AppProps) {
  const { resolvedMode } = useThemeContext();

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: resolvedMode,
          primary: {
            main: resolvedMode === 'dark' ? '#90caf9' : '#1976d2',
            light: resolvedMode === 'dark' ? '#e3f2fd' : '#42a5f5',
            dark: resolvedMode === 'dark' ? '#42a5f5' : '#1565c0',
          },
          secondary: {
            main: resolvedMode === 'dark' ? '#f48fb1' : '#dc004e',
            light: resolvedMode === 'dark' ? '#fce4ec' : '#ff5983',
            dark: resolvedMode === 'dark' ? '#c2185b' : '#9a0036',
          },
          background: {
            default: resolvedMode === 'dark' ? '#121212' : '#f5f5f5',
            paper: resolvedMode === 'dark' ? '#1e1e1e' : '#ffffff',
          },
          text: {
            primary: resolvedMode === 'dark' ? '#ffffff' : 'rgba(0, 0, 0, 0.87)',
            secondary: resolvedMode === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)',
          },
          divider: resolvedMode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        },
        transitions: {
          duration: {
            shortest: 150,
            shorter: 200,
            short: 250,
            standard: 300,
            complex: 375,
            enteringScreen: 225,
            leavingScreen: 195,
          },
          easing: {
            easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
            easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
            easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
            sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
          },
        },
        components: {
          MuiCssBaseline: {
            styleOverrides: {
              body: {
                transition: 'background-color 0.3s ease, color 0.3s ease',
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                transition: 'background-color 0.3s ease, color 0.3s ease',
              },
            },
          },
          MuiAppBar: {
            styleOverrides: {
              root: {
                transition: 'background-color 0.3s ease, color 0.3s ease',
              },
            },
          },
          MuiButton: {
            styleOverrides: {
              root: {
                transition: 'background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease',
              },
            },
          },
          MuiIconButton: {
            styleOverrides: {
              root: {
                transition: 'background-color 0.3s ease, color 0.3s ease',
              },
            },
          },
          MuiTypography: {
            styleOverrides: {
              root: {
                transition: 'color 0.3s ease',
              },
            },
          },
        },
      }),
    [resolvedMode]
  );

  return (
    <MUIThemeProvider theme={theme}>
      <CssBaseline />
      <Component {...pageProps} />
    </MUIThemeProvider>
  );
}

export default function App(props: AppProps) {
  return (
    <ThemeProvider>
      <ThemedApp {...props} />
    </ThemeProvider>
  );
}

