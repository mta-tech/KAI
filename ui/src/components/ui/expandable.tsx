"use client";

import { ChevronRight } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

type ExpandableVariant = 'inline' | 'bordered';

interface ExpandableProps {
  /** The title to display in the header */
  title: ReactNode;
  /** Optional badge to show next to the title */
  badge?: ReactNode;
  /** The content to show when expanded */
  children: ReactNode;
  /** Whether the component is expanded */
  expanded: boolean;
  /** Callback when expanded state changes */
  onExpandedChange: (expanded: boolean) => void;
  /** Whether the expandable is disabled */
  disabled?: boolean;
  /** Whether to show loading state (shimmer effect) */
  isLoading?: boolean;
  /** Custom leading icon (defaults to ChevronRight) */
  leadingIcon?: ReactNode;
  /** Content to show on the right side of the header */
  trailingContent?: ReactNode;
  /** Visual variant */
  variant?: ExpandableVariant;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Expandable - A collapsible component with inline or bordered variants.
 * Used for tool calls, data blocks, and other expandable content.
 */
export function Expandable({
  title,
  badge,
  children,
  expanded,
  onExpandedChange,
  disabled = false,
  isLoading = false,
  leadingIcon,
  trailingContent,
  variant = 'inline',
  className,
}: ExpandableProps) {
  const canExpand = !disabled;
  const isBordered = variant === 'bordered';

  const icon = leadingIcon ?? (
    <ChevronRight
      size={12}
      className={cn('transition-transform duration-200', expanded && 'rotate-90')}
    />
  );

  return (
    <Collapsible
      open={expanded}
      onOpenChange={canExpand ? onExpandedChange : undefined}
      className={cn(
        isBordered && 'border border-border rounded-xl overflow-hidden bg-muted/30',
        className
      )}
    >
      {isBordered ? (
        <div
          className={cn(
            'flex items-center justify-between gap-2 py-2 px-3',
            canExpand && 'cursor-pointer'
          )}
          onClick={() => canExpand && onExpandedChange(!expanded)}
          onKeyDown={(e) => {
            if (canExpand && (e.key === 'Enter' || e.key === ' ')) {
              e.preventDefault();
              onExpandedChange(!expanded);
            }
          }}
          role="button"
          tabIndex={canExpand ? 0 : -1}
          aria-expanded={expanded}
        >
          <div
            className={cn(
              'flex flex-1 items-baseline gap-2 overflow-hidden transition-opacity duration-150',
              expanded ? 'opacity-100' : 'opacity-70',
              canExpand && !expanded
                ? 'hover:opacity-90'
                : ''
            )}
          >
            <div className="size-3 flex items-center justify-center shrink-0 self-center">
              {icon}
            </div>
            <span
              className={cn(
                'flex-1 font-medium truncate min-w-0 text-sm',
                isLoading && 'text-shimmer'
              )}
            >
              {title}
            </span>
            {badge && (
              <span className="text-xs opacity-50 shrink-0">{badge}</span>
            )}
          </div>
          {trailingContent}
        </div>
      ) : (
        <CollapsibleTrigger
          className={cn(
            'select-none flex items-center gap-2 min-w-0 overflow-hidden text-ellipsis whitespace-nowrap transition-opacity duration-150 py-0 hover:no-underline',
            expanded ? 'opacity-100' : 'opacity-50',
            canExpand && !expanded
              ? 'cursor-pointer hover:opacity-75'
              : canExpand
                ? 'cursor-pointer'
                : ''
          )}
        >
          <div className="size-3 flex items-center justify-center shrink-0">
            {icon}
          </div>
          <span className={cn('text-sm', isLoading && 'text-shimmer')}>
            {title}
          </span>
          {badge && <span className="text-xs opacity-50">{badge}</span>}
        </CollapsibleTrigger>
      )}

      <CollapsibleContent className={cn('pb-0', !isBordered && 'pt-1.5')}>
        {isBordered ? (
          <div className="border-t border-border">{children}</div>
        ) : (
          <div className="pl-5 bg-muted/30 relative">
            <div className="h-full border-l border-l-border absolute top-0 left-[6px]" />
            <div>{children}</div>
          </div>
        )}
      </CollapsibleContent>
    </Collapsible>
  );
}
