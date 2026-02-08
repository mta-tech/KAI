'use client';

import Link from 'next/link';
import { Layers } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LogoProps {
  /**
   * Additional CSS classes to apply to the logo container
   */
  className?: string;
  
  /**
   * Whether to show the full text or just the icon
   */
  showText?: boolean;
  
  /**
   * Size variant for the logo
   */
  size?: 'sm' | 'md' | 'lg';
}

/**
 * KAI Logo component
 * 
 * Uses the primary brand color (Deep Indigo) consistently across the app.
 * The logo consists of an icon with the KAI branding.
 */
export function Logo({ className, showText = true, size = 'md' }: LogoProps) {
  const sizeClasses = {
    sm: 'h-7 w-7',
    md: 'h-8 w-8',
    lg: 'h-10 w-10',
  };
  
  const iconSizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };
  
  const textSizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  return (
    <Link
      href="/"
      className={cn('flex items-center gap-2 font-semibold', className)}
      aria-label="KAI Admin Home"
    >
      {/* Logo icon - uses primary brand color */}
      <div className={cn(
        'flex items-center justify-center rounded-lg bg-primary text-primary-foreground transition-colors',
        sizeClasses[size]
      )}>
        <Layers className={iconSizes[size]} aria-hidden="true" />
      </div>
      
      {/* Logo text */}
      {showText && (
        <span className={cn('font-mono tracking-tight', textSizes[size])}>
          KAI_ADMIN
        </span>
      )}
    </Link>
  );
}

/**
 * Compact logo variant for use in tight spaces
 */
export function LogoCompact({ className }: Pick<LogoProps, 'className'>) {
  return (
    <Link
      href="/"
      className={cn('flex items-center gap-2 font-semibold', className)}
      aria-label="KAI Admin Home"
    >
      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <Layers className="h-4 w-4" aria-hidden="true" />
      </div>
    </Link>
  );
}

/**
 * Logo mark (icon only) for use in favicon-like contexts
 */
export function LogoMark({ className, size = 'md' }: Pick<LogoProps, 'className' | 'size'>) {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };
  
  const iconSizes = {
    sm: 'h-3.5 w-3.5',
    md: 'h-5 w-5',
    lg: 'h-7 w-7',
  };

  return (
    <div className={cn('flex items-center justify-center rounded-lg bg-primary text-primary-foreground', sizeClasses[size], className)}>
      <Layers className={iconSizes[size]} aria-hidden="true" />
    </div>
  );
}
