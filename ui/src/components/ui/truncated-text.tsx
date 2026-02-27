'use client';

import * as React from 'react';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface TruncatedTextProps {
  children: React.ReactNode;
  className?: string;
  tooltipClassName?: string;
  maxLength?: number;
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
}

/**
 * TruncatedText component that shows a tooltip with full content on hover.
 * Automatically truncates text that exceeds the container width or maxLength.
 *
 * On mobile devices, the tooltip is shown on long press to avoid interfering with scrolling.
 */
export function TruncatedText({
  children,
  className,
  tooltipClassName,
  maxLength,
  side = 'top',
  align = 'center',
}: TruncatedTextProps) {
  const [isTruncated, setIsTruncated] = React.useState(false);
  const textRef = React.useRef<HTMLDivElement>(null);
  const [isMobile, setIsMobile] = React.useState(false);
  const [longPressTimer, setLongPressTimer] = React.useState<NodeJS.Timeout | null>(null);
  const [showMobileTooltip, setShowMobileTooltip] = React.useState(false);

  // Check if we're on mobile
  React.useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768 || 'ontouchstart' in window);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Check if text is truncated
  const checkTruncation = React.useCallback(() => {
    if (textRef.current) {
      const { scrollWidth, clientWidth } = textRef.current;
      const isOverflowing = scrollWidth > clientWidth;
      const hasMaxLength = maxLength && String(children).length > maxLength;
      setIsTruncated(isOverflowing || hasMaxLength || false);
    }
  }, [children, maxLength]);

  React.useEffect(() => {
    // Check truncation after render and on resize
    checkTruncation();
    window.addEventListener('resize', checkTruncation);
    return () => window.removeEventListener('resize', checkTruncation);
  }, [checkTruncation]);

  // Get display text
  const displayText = maxLength && String(children).length > maxLength
    ? `${String(children).slice(0, maxLength)}...`
    : children;

  // Mobile long press handlers
  const handleTouchStart = () => {
    if (isMobile && isTruncated) {
      const timer = setTimeout(() => {
        setShowMobileTooltip(true);
      }, 500); // 500ms long press
      setLongPressTimer(timer);
    }
  };

  const handleTouchEnd = () => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }
    if (showMobileTooltip) {
      setShowMobileTooltip(false);
    }
  };

  const handleTouchMove = () => {
    // Cancel long press if user scrolls
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }
  };

  if (!isTruncated && (!maxLength || String(children).length <= maxLength)) {
    return (
      <span ref={textRef} className={className}>
        {children}
      </span>
    );
  }

  return (
    <Tooltip open={isMobile ? showMobileTooltip : undefined}>
      <TooltipTrigger asChild>
        <span
          ref={textRef}
          className={cn('block truncate', className)}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          onTouchMove={handleTouchMove}
        >
          {displayText}
        </span>
      </TooltipTrigger>
      <TooltipContent
        side={side}
        align={align}
        className={cn('max-w-xs', tooltipClassName)}
      >
        <p className="break-words">{String(children)}</p>
      </TooltipContent>
    </Tooltip>
  );
}

interface TruncatedCellProps extends TruncatedTextProps {
  header?: string;
}

/**
 * TruncatedCell component for table cells with automatic tooltip.
 * Wraps content in a table cell structure with optional header.
 */
export function TruncatedCell({
  children,
  header,
  className,
  tooltipClassName,
  side,
  align,
}: TruncatedCellProps) {
  return (
    <div className="min-w-0">
      {header && (
        <p className="text-xs font-medium text-muted-foreground mb-1 truncate">
          {header}
        </p>
      )}
      <TruncatedText
        className={cn('text-sm', className)}
        tooltipClassName={tooltipClassName}
        side={side}
        align={align}
      >
        {children}
      </TruncatedText>
    </div>
  );
}
