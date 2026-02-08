/**
 * Design Tokens for KAI
 * 
 * This file defines the design token system for the application.
 * Tokens are organized by category: colors, spacing, typography, shadows, and border radius.
 * 
 * Primary Color: Deep Indigo (#6366f1)
 * - HSL: 239 84% 67%
 */

// ============================================================================
// COLOR TOKENS
// ============================================================================

/**
 * Brand Colors
 * Primary: Deep Indigo (#6366f1)
 */
export const colorTokens = {
  // Primary - Deep Indigo
  primary: {
    DEFAULT: '239 84% 67%', // #6366f1
    foreground: '0 0% 100%',
    hover: '239 84% 60%',
    active: '239 84% 55%',
    disabled: '239 20% 80%',
  },

  // Secondary
  secondary: {
    DEFAULT: '0 0% 96.1%',
    foreground: '0 0% 9%',
    hover: '0 0% 90%',
    active: '0 0% 85%',
  },

  // Accent
  accent: {
    DEFAULT: '239 30% 95%',
    foreground: '239 84% 67%',
    hover: '239 30% 90%',
  },

  // Destructive/Error
  destructive: {
    DEFAULT: '0 84.2% 60.2%',
    foreground: '0 0% 98%',
    hover: '0 84.2% 55%',
  },

  // Success
  success: {
    DEFAULT: '142 76% 36%',
    foreground: '0 0% 100%',
    hover: '142 76% 32%',
  },

  // Warning
  warning: {
    DEFAULT: '38 92% 50%',
    foreground: '0 0% 100%',
    hover: '38 92% 45%',
  },

  // Info
  info: {
    DEFAULT: '199 89% 48%',
    foreground: '0 0% 100%',
    hover: '199 89% 43%',
  },
} as const;

/**
 * Neutral Colors (Base grays)
 */
export const neutralTokens = {
  white: '0 0% 100%',
  black: '0 0% 0%',

  // Gray scale
  gray: {
    50: '210 20% 98%',
    100: '210 20% 96%',
    200: '214 18% 92%',
    300: '213 16% 85%',
    400: '215 15% 75%',
    500: '215 14% 60%',
    600: '215 13% 45%',
    700: '215 12% 35%',
    800: '215 11% 25%',
    900: '215 10% 15%',
    950: '215 9% 10%',
  },
} as const;

/**
 * Semantic Colors (Light mode)
 */
export const lightTokens = {
  background: '0 0% 100%',
  foreground: '0 0% 3.9%',
  card: '0 0% 100%',
  cardForeground: '0 0% 3.9%',
  popover: '0 0% 100%',
  popoverForeground: '0 0% 3.9%',
  muted: '210 20% 96%',
  mutedForeground: '215 14% 45%',
  border: '214 18% 92%',
  input: '214 18% 92%',
  ring: '239 84% 67%',
} as const;

/**
 * Semantic Colors (Dark mode)
 */
export const darkTokens = {
  background: '215 9% 10%',
  foreground: '210 20% 98%',
  card: '215 9% 10%',
  cardForeground: '210 20% 98%',
  popover: '215 9% 10%',
  popoverForeground: '210 20% 98%',
  muted: '215 12% 25%',
  mutedForeground: '215 10% 65%',
  border: '215 12% 25%',
  input: '215 12% 25%',
  ring: '239 84% 67%',
} as const;

/**
 * Chart Colors (for data visualization)
 */
export const chartTokens = {
  1: '239 84% 67%', // Primary
  2: '173 58% 39%',
  3: '197 37% 24%',
  4: '43 74% 66%',
  5: '27 87% 67%',
} as const;

// ============================================================================
// SPACING TOKENS
// ============================================================================

/**
 * Spacing Scale (4px base unit)
 */
export const spacingTokens = {
  0: '0',
  px: '1px',
  0.5: '0.125rem', // 2px
  1: '0.25rem',    // 4px
  1.5: '0.375rem', // 6px
  2: '0.5rem',     // 8px
  2.5: '0.625rem', // 10px
  3: '0.75rem',    // 12px
  3.5: '0.875rem', // 14px
  4: '1rem',       // 16px
  5: '1.25rem',    // 20px
  6: '1.5rem',     // 24px
  7: '1.75rem',    // 28px
  8: '2rem',       // 32px
  9: '2.25rem',    // 36px
  10: '2.5rem',    // 40px
  11: '2.75rem',   // 44px
  12: '3rem',      // 48px
  14: '3.5rem',    // 56px
  16: '4rem',      // 64px
  20: '5rem',      // 80px
  24: '6rem',      // 96px
  28: '7rem',      // 112px
  32: '8rem',      // 128px
  36: '9rem',      // 144px
  40: '10rem',     // 160px
  44: '11rem',     // 176px
  48: '12rem',     // 192px
  52: '13rem',     // 208px
  56: '14rem',     // 224px
  60: '15rem',     // 240px
  64: '16rem',     // 256px
  72: '18rem',     // 288px
  80: '20rem',     // 320px
  96: '24rem',     // 384px
} as const;

// ============================================================================
// TYPOGRAPHY TOKENS
// ============================================================================

/**
 * Font Families
 */
export const fontFamilyTokens = {
  sans: [
    'Inter',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'Oxygen',
    'Ubuntu',
    'Cantarell',
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    'sans-serif',
  ],
  mono: [
    'ui-monospace',
    'SFMono-Regular',
    'Monaco',
    'Consolas',
    'Liberation Mono',
    'Courier New',
    'monospace',
  ],
} as const;

/**
 * Font Sizes
 */
export const fontSizeTokens = {
  xs: ['0.75rem', { lineHeight: '1rem' }],     // 12px
  sm: ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
  base: ['1rem', { lineHeight: '1.5rem' }],     // 16px
  lg: ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
  xl: ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
  '2xl': ['1.5rem', { lineHeight: '2rem' }],    // 24px
  '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
  '4xl': ['2.25rem', { lineHeight: '2.5rem' }], // 36px
  '5xl': ['3rem', { lineHeight: '1' }],         // 48px
  '6xl': ['3.75rem', { lineHeight: '1' }],      // 60px
  '7xl': ['4.5rem', { lineHeight: '1' }],       // 72px
  '8xl': ['6rem', { lineHeight: '1' }],         // 96px
  '9xl': ['8rem', { lineHeight: '1' }],         // 128px
} as const;

/**
 * Font Weights
 */
export const fontWeightTokens = {
  thin: '100',
  extralight: '200',
  light: '300',
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
  black: '900',
} as const;

/**
 * Letter Spacing
 */
export const letterSpacingTokens = {
  tighter: '-0.05em',
  tight: '-0.025em',
  normal: '0em',
  wide: '0.025em',
  wider: '0.05em',
  widest: '0.1em',
} as const;

/**
 * Line Heights
 */
export const lineHeightTokens = {
  none: '1',
  tight: '1.25',
  snug: '1.375',
  normal: '1.5',
  relaxed: '1.625',
  loose: '2',
} as const;

// ============================================================================
// BORDER RADIUS TOKENS
// ============================================================================

/**
 * Border Radius Scale
 */
export const borderRadiusTokens = {
  none: '0',
  sm: '0.125rem',   // 2px
  DEFAULT: '0.25rem', // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',
} as const;

// ============================================================================
// SHADOW TOKENS
// ============================================================================

/**
 * Shadow Scale
 */
export const shadowTokens = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
  none: '0 0 #0000',
} as const;

// ============================================================================
// ANIMATION TOKENS
// ============================================================================

/**
 * Animation Durations
 */
export const durationTokens = {
  75: '75ms',
  100: '100ms',
  150: '150ms',
  200: '200ms',
  300: '300ms',
  500: '500ms',
  700: '700ms',
  1000: '1000ms',
} as const;

/**
 * Animation Easing
 */
export const easingTokens = {
  linear: 'linear',
  in: 'cubic-bezier(0.4, 0, 1, 1)',
  out: 'cubic-bezier(0, 0, 0.2, 1)',
  'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
} as const;

// ============================================================================
// Z-INDEX TOKENS
// ============================================================================

/**
 * Z-Index Scale
 */
export const zIndexTokens = {
  hide: -1,
  base: 0,
  dropdown: 10,
  sticky: 20,
  fixed: 30,
  modalBackdrop: 40,
  modal: 50,
  popover: 60,
  tooltip: 70,
} as const;

// ============================================================================
// BREAKPOINT TOKENS
// ============================================================================

/**
 * Breakpoints (in pixels)
 */
export const breakpointTokens = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ============================================================================
// EXPORT ALL TOKENS
// ============================================================================

export const designTokens = {
  colors: {
    brand: colorTokens,
    neutral: neutralTokens,
    light: lightTokens,
    dark: darkTokens,
    chart: chartTokens,
  },
  spacing: spacingTokens,
  typography: {
    fontFamily: fontFamilyTokens,
    fontSize: fontSizeTokens,
    fontWeight: fontWeightTokens,
    letterSpacing: letterSpacingTokens,
    lineHeight: lineHeightTokens,
  },
  borderRadius: borderRadiusTokens,
  shadows: shadowTokens,
  animation: {
    duration: durationTokens,
    easing: easingTokens,
  },
  zIndex: zIndexTokens,
  breakpoints: breakpointTokens,
} as const;

// ============================================================================
// TAILWIND CONFIG UTILITIES
// ============================================================================

/**
 * CSS Variables for light mode
 */
export const lightModeVars = {
  '--background': lightTokens.background,
  '--foreground': lightTokens.foreground,
  '--card': lightTokens.card,
  '--card-foreground': lightTokens.cardForeground,
  '--popover': lightTokens.popover,
  '--popover-foreground': lightTokens.popoverForeground,
  '--primary': colorTokens.primary.DEFAULT,
  '--primary-foreground': colorTokens.primary.foreground,
  '--secondary': colorTokens.secondary.DEFAULT,
  '--secondary-foreground': colorTokens.secondary.foreground,
  '--muted': lightTokens.muted,
  '--muted-foreground': lightTokens.mutedForeground,
  '--accent': colorTokens.accent.DEFAULT,
  '--accent-foreground': colorTokens.accent.foreground,
  '--destructive': colorTokens.destructive.DEFAULT,
  '--destructive-foreground': colorTokens.destructive.foreground,
  '--border': lightTokens.border,
  '--input': lightTokens.input,
  '--ring': lightTokens.ring,
  '--chart-1': chartTokens['1'],
  '--chart-2': chartTokens['2'],
  '--chart-3': chartTokens['3'],
  '--chart-4': chartTokens['4'],
  '--chart-5': chartTokens['5'],
  '--radius': borderRadiusTokens.DEFAULT,
} as const;

/**
 * CSS Variables for dark mode
 */
export const darkModeVars = {
  '--background': darkTokens.background,
  '--foreground': darkTokens.foreground,
  '--card': darkTokens.card,
  '--card-foreground': darkTokens.cardForeground,
  '--popover': darkTokens.popover,
  '--popover-foreground': darkTokens.popoverForeground,
  '--primary': colorTokens.primary.DEFAULT,
  '--primary-foreground': '215 9% 10%',
  '--secondary': '215 12% 25%',
  '--secondary-foreground': darkTokens.foreground,
  '--muted': darkTokens.muted,
  '--muted-foreground': darkTokens.mutedForeground,
  '--accent': '239 30% 20%',
  '--accent-foreground': colorTokens.primary.DEFAULT,
  '--destructive': '0 62.8% 30.6%',
  '--destructive-foreground': darkTokens.foreground,
  '--border': darkTokens.border,
  '--input': darkTokens.input,
  '--ring': darkTokens.ring,
  '--chart-1': '220 70% 50%',
  '--chart-2': '160 60% 45%',
  '--chart-3': '30 80% 55%',
  '--chart-4': '280 65% 60%',
  '--chart-5': '340 75% 55%',
  '--radius': borderRadiusTokens.DEFAULT,
} as const;
