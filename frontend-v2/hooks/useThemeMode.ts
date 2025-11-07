import { useState, useEffect, useRef } from 'react';

export type ThemeMode = 'light' | 'dark' | 'system';

const THEME_STORAGE_KEY = 'bitbybit-theme-mode';

/**
 * Hook to manage theme mode with system preference detection
 * Handles SSR properly to prevent hydration mismatches
 */
export function useThemeMode() {
  const [mounted, setMounted] = useState(false);
  const [mode, setMode] = useState<ThemeMode>('system');
  const [resolvedMode, setResolvedMode] = useState<'light' | 'dark'>('light');
  const resolvedModeRef = useRef<'light' | 'dark'>('light');

  // Initialize on mount (client-side only)
  useEffect(() => {
    setMounted(true);
    
    // Get stored preference or default to system
    const stored = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null;
    const initialMode = stored && ['light', 'dark', 'system'].includes(stored) 
      ? stored 
      : 'system';
    
    setMode(initialMode);
    
    // Set initial resolved mode
    if (initialMode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const initialResolved = mediaQuery.matches ? 'dark' : 'light';
      setResolvedMode(initialResolved);
      resolvedModeRef.current = initialResolved;
    } else {
      setResolvedMode(initialMode);
      resolvedModeRef.current = initialMode;
    }
  }, []);

  // Update resolved mode when mode changes
  useEffect(() => {
    if (!mounted) return;
    
    if (mode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const updateResolvedMode = () => {
        const newResolved = mediaQuery.matches ? 'dark' : 'light';
        setResolvedMode(newResolved);
        resolvedModeRef.current = newResolved;
      };

      // Set initial value
      updateResolvedMode();

      // Listen for system theme changes
      mediaQuery.addEventListener('change', updateResolvedMode);
      return () => mediaQuery.removeEventListener('change', updateResolvedMode);
    } else {
      setResolvedMode(mode);
      resolvedModeRef.current = mode;
    }
  }, [mode, mounted]);

  // Save to localStorage when mode changes
  useEffect(() => {
    if (mounted) {
      localStorage.setItem(THEME_STORAGE_KEY, mode);
    }
  }, [mode, mounted]);

  const toggleTheme = () => {
    setMode((current) => {
      // If currently on system, switch to the opposite of current resolved mode
      if (current === 'system') {
        // Use ref to get the current resolved mode (always up to date)
        return resolvedModeRef.current === 'light' ? 'dark' : 'light';
      }
      // Otherwise, just toggle between light and dark
      return current === 'light' ? 'dark' : 'light';
    });
  };

  const setThemeMode = (newMode: ThemeMode) => {
    setMode(newMode);
  };

  return {
    mode,
    resolvedMode,
    mounted, // Expose mounted state for components that need it
    toggleTheme,
    setThemeMode,
  };
}
