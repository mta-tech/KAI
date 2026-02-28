import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  getResolvedTheme: () => 'light' | 'dark';
}

/**
 * Check if code is running in browser environment
 */
function isBrowser(): boolean {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
}

/**
 * Theme store for managing application theme
 * Persists user preference across sessions
 */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      setTheme: (theme: Theme) => set({ theme }),
      getResolvedTheme: () => {
        const { theme } = get();
        if (theme === 'system') {
          if (!isBrowser()) return 'light'; // Default to light on server
          return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return theme;
      },
    }),
    {
      name: 'kai-theme-storage',
    }
  )
);

/**
 * Hook to get the current resolved theme (light or dark)
 * This accounts for system preference when theme is set to 'system'
 */
export function useTheme() {
  const store = useThemeStore();

  // Get the actual theme (resolve 'system' to 'light' or 'dark')
  // Default to 'light' during SSR
  const resolvedTheme = isBrowser() ? store.getResolvedTheme() : 'light';

  return {
    theme: store.theme,
    resolvedTheme,
    setTheme: store.setTheme,
    isDark: resolvedTheme === 'dark',
    isLight: resolvedTheme === 'light',
  };
}

/**
 * Initialize theme on app mount
 * This should be called once in the root layout
 * Only runs in browser environment
 */
export function initializeTheme() {
  // Only run in browser
  if (!isBrowser()) {
    return () => {}; // No-op cleanup function for SSR
  }

  const store = useThemeStore.getState();
  const root = document.documentElement;

  // Apply the theme class to the root element
  const resolvedTheme = store.getResolvedTheme();

  if (resolvedTheme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }

  // Listen for system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  const handleChange = () => {
    const { theme } = useThemeStore.getState();
    if (theme === 'system') {
      const newTheme = mediaQuery.matches ? 'dark' : 'light';
      if (newTheme === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  };

  mediaQuery.addEventListener('change', handleChange);

  // Return cleanup function
  return () => {
    mediaQuery.removeEventListener('change', handleChange);
  };
}
