'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-primary/10', className)}
      {...props}
    />
  );
}

/**
 * Enhanced skeleton component with shimmer effect and mobile optimization.
 * Respects prefers-reduced-motion for accessibility.
 */
interface EnhancedSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'shimmer' | 'pulse';
  width?: string | number;
  height?: string | number;
  count?: number;
}

export function EnhancedSkeleton({
  variant = 'default',
  width,
  height,
  count = 1,
  className,
  style,
  ...props
}: EnhancedSkeletonProps) {
  const items = React.useMemo(() => Array.from({ length: count }), [count]);

  // Check for reduced motion preference
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState(false);

  React.useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Don't animate if user prefers reduced motion
  if (prefersReducedMotion) {
    return (
      <div
        className={cn('bg-muted/50 rounded-md', className)}
        style={{ width, height, ...style }}
        {...props}
      />
    );
  }

  if (variant === 'shimmer') {
    return (
      <div className={cn('relative overflow-hidden bg-muted/50 rounded-md', className)} style={{ width, height, ...style }} {...props}>
        <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
      </div>
    );
  }

  if (variant === 'pulse') {
    return (
      <div
        className={cn('animate-pulse bg-muted/50 rounded-md', className)}
        style={{ width, height, ...style }}
        {...props}
      />
    );
  }

  return (
    <>
      {items.map((_, i) => (
        <Skeleton
          key={i}
          className={cn(i > 0 && 'mt-2', className)}
          style={{ width, height }}
          {...props}
        />
      ))}
    </>
  );
}

/**
 * SkeletonCard - Card-shaped skeleton with header, content, and footer.
 * Optimized for mobile with responsive sizing.
 */
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('rounded-lg border bg-card p-4 space-y-4', className)}>
      {/* Header */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-3 w-1/3" />
      </div>

      {/* Content */}
      <div className="space-y-3">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-5/6" />
        <Skeleton className="h-12 w-4/6" />
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center pt-4">
        <Skeleton className="h-8 w-20 rounded-md" />
        <Skeleton className="h-8 w-8 rounded-full" />
      </div>
    </div>
  );
}

/**
 * SkeletonList - List item skeleton with icon and text.
 * Great for mobile navigation and menu items.
 */
export function SkeletonList({ count = 5, className }: { count?: number; className?: string }) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          {/* Avatar/Icon */}
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />

          {/* Text content */}
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>

          {/* Action */}
          <Skeleton className="h-8 w-8 rounded-md flex-shrink-0" />
        </div>
      ))}
    </div>
  );
}

/**
 * SkeletonTable - Table skeleton with header and rows.
 * Mobile-optimized with responsive layout.
 */
export function SkeletonTable({
  rows = 5,
  columns = 4,
  className
}: {
  rows?: number;
  columns?: number;
  className?: string;
}) {
  return (
    <div className={cn('w-full space-y-4', className)}>
      {/* Header */}
      <div className="flex gap-4 border-b pb-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={`h-${i}`} className="h-4 flex-1" />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={`row-${i}`} className="flex gap-4">
          {Array.from({ length: columns }).map((_, j) => (
            <Skeleton key={`cell-${i}-${j}`} className="h-12 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

/**
 * SkeletonChat - Chat-specific skeleton with message bubbles.
 * Optimized for mobile chat interfaces.
 */
export function SkeletonChat({ className }: { className?: string }) {
  return (
    <div className={cn('space-y-4 p-4', className)}>
      {/* Received message */}
      <div className="flex gap-3 max-w-[85%]">
        <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-16 w-48 rounded-lg" />
        </div>
      </div>

      {/* Sent message */}
      <div className="flex gap-3 max-w-[85%] ml-auto justify-end">
        <div className="space-y-2">
          <Skeleton className="h-4 w-24 ml-auto" />
          <Skeleton className="h-20 w-56 rounded-lg" />
        </div>
        <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
      </div>

      {/* Typing indicator */}
      <div className="flex gap-3 max-w-[85%]">
        <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
        <div className="flex gap-1">
          <Skeleton className="h-2 w-2 rounded-full" />
          <Skeleton className="h-2 w-2 rounded-full" />
          <Skeleton className="h-2 w-2 rounded-full" />
        </div>
      </div>
    </div>
  );
}

/**
 * SkeletonAvatar - Avatar skeleton with mobile sizing.
 */
export function SkeletonAvatar({
  size = 'default',
  className
}: {
  size?: 'sm' | 'default' | 'lg';
  className?: string;
}) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    default: 'h-10 w-10',
    lg: 'h-12 w-12',
  };

  return (
    <Skeleton
      className={cn('rounded-full flex-shrink-0', sizeClasses[size], className)}
    />
  );
}

/**
 * SkeletonText - Text skeleton with configurable lines and width.
 * Useful for paragraphs and headings.
 */
export function SkeletonText({
  lines = 3,
  width,
  className
}: {
  lines?: number;
  width?: string | number;
  className?: string;
}) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={cn(
            'h-4',
            width && i === 0 ? 'w-full' : '',
            typeof width === 'number' ? `${width}px` : width,
            !width && i === lines - 1 ? 'w-2/3' : '',
            !width && i !== lines - 1 && i !== 0 ? 'w-full' : ''
          )}
        />
      ))}
    </div>
  );
}

/**
 * SkeletonForm - Form skeleton with inputs and buttons.
 * Mobile-optimized form loading state.
 */
export function SkeletonForm({ className }: { className?: string }) {
  return (
    <div className={cn('space-y-6 p-4', className)}>
      {/* Field 1 */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
      </div>

      {/* Field 2 */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-10 w-full" />
      </div>

      {/* Field 3 - textarea */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-24 w-full" />
      </div>

      {/* Actions */}
      <div className="flex gap-4 pt-4">
        <Skeleton className="h-10 w-24 rounded-md" />
        <Skeleton className="h-10 w-20 rounded-md" />
      </div>
    </div>
  );
}

/**
 * SkeletonDashboard - Dashboard-specific skeleton with cards and stats.
 * Optimized for mobile dashboard loading.
 */
export function SkeletonDashboard({ className }: { className?: string }) {
  return (
    <div className={cn('space-y-6 p-4', className)}>
      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-8 w-full" />
          </div>
        ))}
      </div>

      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );
}

export { Skeleton };
