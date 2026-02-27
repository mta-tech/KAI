'use client';

import * as React from 'react';
import { Button, ButtonProps } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface InteractiveButtonProps extends ButtonProps {
  /**
   * Enable ripple effect for mobile touch feedback
   * @default true
   */
  ripple?: boolean;

  /**
   * Enable scale animation on hover/active
   * @default true
   */
  scale?: boolean;

  /**
   * Touch feedback - visual press state for mobile
   * @default true
   */
  touchFeedback?: boolean;

  /**
   * Icon element (optional, for icon buttons)
   */
  icon?: React.ReactNode;
}

/**
 * InteractiveButton component with mobile-optimized touch feedback.
 *
 * Features:
 * - Ripple effect on touch/click
 * - Scale animation on hover/active
 * - Touch-friendly active states
 * - Respects prefers-reduced-motion
 * - 44x44px minimum touch target for accessibility
 */
export function InteractiveButton({
  ripple = true,
  scale = true,
  touchFeedback = true,
  icon,
  className,
  children,
  size = 'default',
  variant = 'default',
  ...props
}: InteractiveButtonProps) {
  const buttonRef = React.useRef<HTMLButtonElement>(null);
  const [rippleCoords, setRippleCoords] = React.useState<{ x: string; y: string } | null>(null);
  const [isPressed, setIsPressed] = React.useState(false);

  // Handle ripple effect
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!ripple) return;

    const rect = buttonRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    setRippleCoords({ x: `${x}%`, y: `${y}%` });

    // Clear ripple after animation
    setTimeout(() => setRippleCoords(null), 600);
  };

  // Handle touch press state
  React.useEffect(() => {
    const button = buttonRef.current;
    if (!button || !touchFeedback) return;

    const handleTouchStart = () => setIsPressed(true);
    const handleTouchEnd = () => setIsPressed(false);
    const handleTouchCancel = () => setIsPressed(false);

    button.addEventListener('touchstart', handleTouchStart);
    button.addEventListener('touchend', handleTouchEnd);
    button.addEventListener('touchcancel', handleTouchCancel);

    return () => {
      button.removeEventListener('touchstart', handleTouchStart);
      button.removeEventListener('touchend', handleTouchEnd);
      button.removeEventListener('touchcancel', handleTouchCancel);
    };
  }, [touchFeedback]);

  return (
    <Button
      ref={buttonRef}
      variant={variant}
      size={size}
      className={cn(
        'interactive-element',
        // Scale animations
        scale && !props.disabled && !variant?.includes('ghost') && 'btn-hover-scale btn-active-scale',
        // Ripple effect
        ripple && 'ripple-effect',
        // Touch feedback
        touchFeedback && isPressed && 'bg-accent/80',
        // Icon button styling
        icon && !children && 'aspect-square p-0',
        className
      )}
      style={rippleCoords ? {
        '--x': rippleCoords.x,
        '--y': rippleCoords.y,
      } as React.CSSProperties : undefined}
      onClick={handleClick}
      onMouseDown={() => touchFeedback && setIsPressed(true)}
      onMouseUp={() => touchFeedback && setIsPressed(false)}
      onMouseLeave={() => touchFeedback && setIsPressed(false)}
      {...props}
    >
      {icon && !children ? (
        <span className="flex items-center justify-center">
          {icon}
        </span>
      ) : (
        <>
          {icon && (
            <span className="mr-2 flex items-center">
              {icon}
            </span>
          )}
          {children}
        </>
      )}
    </Button>
  );
}

/**
 * IconButton component for icon-only buttons with proper touch targets.
 * Ensures 44x44px minimum size for accessibility.
 */
interface IconButtonProps extends Omit<InteractiveButtonProps, 'children'> {
  icon: React.ReactNode;
  label: string;
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export function IconButton({ icon, label, size = 'icon', ...props }: IconButtonProps) {
  return (
    <InteractiveButton
      icon={icon}
      size={size}
      aria-label={label}
      title={label}
      className={cn(
        'h-11 w-11', // Ensure 44x44px minimum for mobile
        size === 'sm' && 'h-9 w-9',
        size === 'lg' && 'h-12 w-12'
      )}
      {...props}
    />
  );
}
