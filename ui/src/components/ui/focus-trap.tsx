'use client';

import { useEffect, useRef } from 'react';
import { useFocusTrap } from '@/lib/hooks/use-focus-trap';

interface FocusTrapProps {
  children: React.ReactNode;
  enabled?: boolean;
  className?: string;
}

/**
 * Component that traps keyboard focus within its children
 * Useful for modals, dialogs, and dropdowns
 */
export function FocusTrap({ children, enabled = true, className = '' }: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const previousActiveElementRef = useRef<HTMLElement | null>(null);

  // Use the focus trap hook
  useFocusTrap(enabled && containerRef.current !== null);

  useEffect(() => {
    if (!enabled) return;

    // Store the element that had focus before the trap was activated
    previousActiveElementRef.current = document.activeElement as HTMLElement;

    return () => {
      // Restore focus to the previous element when the trap is deactivated
      if (previousActiveElementRef.current) {
        previousActiveElementRef.current.focus();
      }
    };
  }, [enabled]);

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  );
}
