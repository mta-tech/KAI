'use client';

import { useEffect } from 'react';
import { initializeTheme } from '@/lib/stores/theme-store';

/**
 * ThemeProvider component
 * Initializes the theme on app mount and handles system theme changes
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Initialize theme and set up system preference listener
    const cleanup = initializeTheme();
    
    return cleanup;
  }, []);

  return <>{children}</>;
}
