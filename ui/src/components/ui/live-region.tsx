'use client';

import { useEffect, useRef } from 'react';

interface LiveRegionProps {
  children: React.ReactNode;
  politeness?: 'polite' | 'assertive';
  role?: 'status' | 'alert';
  className?: string;
}

/**
 * LiveRegion component for announcing dynamic content to screen readers
 * 
 * @param politeness - 'polite' waits for user to be idle, 'assertive' interrupts immediately
 * @param role - 'status' for general updates, 'alert' for important/critical updates
 */
export function LiveRegion({
  children,
  politeness = 'polite',
  role = 'status',
  className = '',
}: LiveRegionProps) {
  const announcerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!announcerRef.current) return;

    // Clear and update the live region content
    announcerRef.current.textContent = '';
    
    // Use setTimeout to ensure screen readers pick up the content change
    const timeoutId = setTimeout(() => {
      if (announcerRef.current) {
        announcerRef.current.textContent = typeof children === 'string' ? children : '';
      }
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [children]);

  return (
    <div
      ref={announcerRef}
      role={role}
      aria-live={politeness}
      aria-atomic="true"
      className={className}
    >
      {children}
    </div>
  );
}

/**
 * Hook to announce messages to screen readers
 */
export function useAnnouncer() {
  const announcerRef = useRef<(message: string, politeness?: 'polite' | 'assertive') => void>();

  useEffect(() => {
    // Create a hidden live region for announcements
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('role', 'status');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    document.body.appendChild(liveRegion);

    announcerRef.current = (message: string, politeness: 'polite' | 'assertive' = 'polite') => {
      if (politeness === 'assertive') {
        liveRegion.setAttribute('role', 'alert');
        liveRegion.setAttribute('aria-live', 'assertive');
      } else {
        liveRegion.setAttribute('role', 'status');
        liveRegion.setAttribute('aria-live', 'polite');
      }
      liveRegion.textContent = '';
      setTimeout(() => {
        liveRegion.textContent = message;
      }, 100);
    };

    return () => {
      document.body.removeChild(liveRegion);
    };
  }, []);

  return announcerRef;
}
