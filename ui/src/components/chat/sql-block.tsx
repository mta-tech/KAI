'use client';

import { useState } from 'react';
import { Check, Copy, Database, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SqlBlockProps {
  sql: string;
  className?: string;
  isStreaming?: boolean;
}

export function SqlBlock({ sql, className, isStreaming }: SqlBlockProps) {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Truncate SQL for mobile display
  const sqlLines = sql.split('\n');
  const isLongSql = sqlLines.length > 5;
  const displaySql = isLongSql && !isExpanded
    ? sqlLines.slice(0, 5).join('\n') + '\n...'
    : sql;

  return (
    <div className={cn(
      'rounded-lg border bg-slate-950 text-slate-50 overflow-hidden',
      'transition-all duration-200',
      isStreaming && 'border-emerald-500/50',
      className
    )}>
      <div className="flex items-center justify-between px-3 py-2 sm:px-4 sm:py-2 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-1.5 sm:gap-2 text-sm text-slate-400">
          <Database className={cn(
            "h-3.5 w-3.5 sm:h-4 sm:w-4",
            isStreaming && "text-emerald-400 animate-pulse"
          )} />
          <span className="text-xs sm:text-sm">SQL Query</span>
          {isStreaming && (
            <span className="flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {isLongSql && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              onClick={() => setIsExpanded(!isExpanded)}
              aria-label={isExpanded ? 'Collapse' : 'Expand'}
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="h-3 w-3 mr-1" />
                  <span className="hidden sm:inline">Show less</span>
                </>
              ) : (
                <>
                  <ChevronDown className="h-3 w-3 mr-1" />
                  <span className="hidden sm:inline">Show more</span>
                </>
              )}
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            onClick={handleCopy}
            disabled={isStreaming}
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 mr-1" />
                <span className="hidden sm:inline">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3 mr-1" />
                <span className="hidden sm:inline">Copy</span>
              </>
            )}
          </Button>
        </div>
      </div>
      <pre className={cn(
        "p-3 sm:p-4 overflow-x-auto text-xs sm:text-sm relative",
        !isExpanded && isLongSql && "max-h-[150px]"
      )}>
        {isStreaming && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-emerald-500/5 to-transparent animate-shimmer" />
          </div>
        )}
        <code className="language-sql">{displaySql}</code>
      </pre>
    </div>
  );
}
