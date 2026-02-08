'use client';

import Link from 'next/link';

/**
 * Skip link component for keyboard navigation
 * Allows users to skip to main content, bypassing navigation
 */
export function SkipLink() {
  return (
    <Link
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:font-medium focus:shadow-lg"
    >
      Skip to main content
    </Link>
  );
}
