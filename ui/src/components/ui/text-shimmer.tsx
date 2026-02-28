"use client";

import { cn } from '@/lib/utils';

interface TextShimmerProps {
  /** The text to display with shimmer effect */
  text?: string;
  /** Additional CSS classes */
  className?: string;
  /** Children to render (overrides text prop) */
  children?: React.ReactNode;
}

/**
 * TextShimmer component displays text with a shimmer animation effect.
 * Used primarily for loading states like "Thinking..." indicators.
 */
export function TextShimmer({
  text = 'Thinking',
  className,
  children
}: TextShimmerProps) {
  return (
    <div className={cn(className)}>
      <span className="text-sm text-shimmer">
        {children ?? text}
      </span>
    </div>
  );
}
