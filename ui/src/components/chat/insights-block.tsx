'use client';

import { Lightbulb, TrendingUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { cn } from '@/lib/utils';

interface InsightsBlockProps {
  insights: string;
  className?: string;
}

export function InsightsBlock({ insights, className }: InsightsBlockProps) {
  return (
    <div className={cn('rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30 overflow-hidden', className)}>
      <div className="flex items-center gap-2 px-4 py-2 bg-amber-100 dark:bg-amber-900/30 border-b border-amber-200 dark:border-amber-800">
        <Lightbulb className="h-4 w-4 text-amber-600 dark:text-amber-400" />
        <span className="text-sm font-medium text-amber-800 dark:text-amber-300">Key Insights</span>
      </div>
      <div className="p-4 prose prose-sm dark:prose-invert max-w-none prose-amber">
        <ReactMarkdown>{insights}</ReactMarkdown>
      </div>
    </div>
  );
}

interface ChartRecommendationsBlockProps {
  recommendations: string;
  className?: string;
}

export function ChartRecommendationsBlock({ recommendations, className }: ChartRecommendationsBlockProps) {
  return (
    <div className={cn('rounded-lg border border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950/30 overflow-hidden', className)}>
      <div className="flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 border-b border-blue-200 dark:border-blue-800">
        <TrendingUp className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        <span className="text-sm font-medium text-blue-800 dark:text-blue-300">Visualization Recommendations</span>
      </div>
      <div className="p-4 prose prose-sm dark:prose-invert max-w-none prose-blue">
        <ReactMarkdown>{recommendations}</ReactMarkdown>
      </div>
    </div>
  );
}
