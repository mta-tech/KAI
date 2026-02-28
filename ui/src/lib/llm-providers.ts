export interface LLMProviderOption {
  id: string;
  name: string;
  models: { id: string; label: string }[];
}

export const LLM_PROVIDERS: LLMProviderOption[] = [
  {
    id: 'google',
    name: 'Google',
    models: [
      { id: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash' },
      { id: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
      { id: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash' },
    ],
  },
  {
    id: 'openai',
    name: 'OpenAI',
    models: [
      { id: 'gpt-4o', label: 'GPT-4o' },
      { id: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
      { id: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    ],
  },
  {
    id: 'ollama',
    name: 'Ollama',
    models: [
      { id: 'llama3', label: 'Llama 3' },
      { id: 'mistral', label: 'Mistral' },
      { id: 'codellama', label: 'Code Llama' },
    ],
  },
  {
    id: 'openrouter',
    name: 'OpenRouter',
    models: [
      { id: 'anthropic/claude-3', label: 'Claude 3' },
      { id: 'openai/gpt-4', label: 'GPT-4' },
      { id: 'google/gemini-pro', label: 'Gemini Pro' },
    ],
  },
];

export const DEFAULT_MODEL = 'gemini-2.0-flash';

export function getAllModels(): { id: string; label: string; provider: string }[] {
  return LLM_PROVIDERS.flatMap((p) =>
    p.models.map((m) => ({ ...m, provider: p.name }))
  );
}
