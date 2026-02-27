'use client';

import { CornerDownRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FollowUpSuggestionsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}

export function FollowUpSuggestions({ suggestions, onSelect }: FollowUpSuggestionsProps) {
  if (suggestions.length === 0) return null;

  return (
    <div
      className="flex flex-col gap-1 mt-2"
      role="group"
      aria-label="Follow-up suggestions"
    >
      {suggestions.map((suggestion, index) => (
        <Button
          key={index}
          variant="ghost"
          onClick={() => onSelect(suggestion)}
          className="justify-start gap-2 px-3 py-2 text-left rounded-lg h-auto text-sm hover:bg-muted/80"
          aria-label={`Follow-up: ${suggestion}`}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onSelect(suggestion);
            }
          }}
        >
          <CornerDownRight className="h-4 w-4 text-muted-foreground opacity-50 shrink-0" />
          <span className="line-clamp-2 text-left">{suggestion}</span>
        </Button>
      ))}
    </div>
  );
}
