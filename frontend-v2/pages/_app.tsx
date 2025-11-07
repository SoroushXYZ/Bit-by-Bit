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
            main: '#1976d2',
          },
          secondary: {
            main: '#dc004e',
          },
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

