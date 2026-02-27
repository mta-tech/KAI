'use client';

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { LLM_PROVIDERS } from '@/lib/llm-providers';

interface ModelSelectorProps {
  value: string;
  onChange: (model: string) => void;
  disabled?: boolean;
}

export function ModelSelector({ value, onChange, disabled }: ModelSelectorProps) {
  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger
        className="h-9 w-auto min-w-[130px] max-w-[180px] text-xs border-0 bg-muted/50 hover:bg-muted focus:ring-0 focus:ring-offset-0"
        aria-label="Select AI model"
      >
        <SelectValue placeholder="Select model" />
      </SelectTrigger>
      <SelectContent>
        {LLM_PROVIDERS.map((provider) => (
          <SelectGroup key={provider.id}>
            <SelectLabel className="text-xs text-muted-foreground">{provider.name}</SelectLabel>
            {provider.models.map((model) => (
              <SelectItem key={model.id} value={model.id} className="text-xs">
                {model.label}
              </SelectItem>
            ))}
          </SelectGroup>
        ))}
      </SelectContent>
    </Select>
  );
}
