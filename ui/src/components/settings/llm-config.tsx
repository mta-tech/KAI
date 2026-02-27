'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { LoadingButton } from '@/components/ui/loading-button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import {
  Settings2,
  Key,
  TestTube,
  Check,
  X,
  Eye,
  EyeOff,
  Sparkles,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

interface LLMProvider {
  id: string;
  name: string;
  icon: string;
  apiKey?: string;
  models: string[];
  defaultModel: string;
  enabled: boolean;
}

const availableProviders: Omit<LLMProvider, 'apiKey' | 'enabled'>[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    icon: '🤖',
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    defaultModel: 'gpt-4',
  },
  {
    id: 'google',
    name: 'Google Gemini',
    icon: '✨',
    models: ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash'],
    defaultModel: 'gemini-2.0-flash',
  },
  {
    id: 'ollama',
    name: 'Ollama',
    icon: '🦙',
    models: ['llama3', 'mistral', 'codellama', 'phi3'],
    defaultModel: 'llama3',
  },
  {
    id: 'openrouter',
    name: 'OpenRouter',
    icon: '🔀',
    models: ['anthropic/claude-3', 'openai/gpt-4', 'google/gemini-pro'],
    defaultModel: 'anthropic/claude-3',
  },
];

export function LLMConfig() {
  const { toast } = useToast();
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<LLMProvider | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);

  // Load saved providers on mount
  useState(() => {
    loadProviders();
  });

  const loadProviders = async () => {
    try {
      const response = await api.get<{ providers: LLMProvider[] }>('/config/llm');
      setProviders(response?.providers || []);
    } catch (error) {
      console.error('Failed to load LLM config:', error);
    }
  };

  const handleConfigure = (provider: Omit<LLMProvider, 'enabled' | 'apiKey'>) => {
    setSelectedProvider(provider as LLMProvider);
    setApiKey('');
    setSelectedModel(provider.defaultModel);
    setTestResult(null);
  };

  const handleTest = async () => {
    if (!selectedProvider || !apiKey) {
      toast({
        title: 'API key required',
        description: 'Please enter an API key to test.',
        variant: 'destructive',
      });
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      await api.post('/config/llm/test', {
        provider: selectedProvider.id,
        api_key: apiKey,
        model: selectedModel,
      });
      setTestResult('success');
      toast({
        title: 'Test successful',
        description: `Connected to ${selectedProvider.name} successfully!`,
      });
    } catch (error) {
      setTestResult('error');
      toast({
        title: 'Test failed',
        description: 'Could not connect to the LLM provider. Please check your API key.',
        variant: 'destructive',
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    if (!selectedProvider || !apiKey) {
      toast({
        title: 'Missing information',
        description: 'Please enter an API key.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await api.put('/config/llm', {
        provider_id: selectedProvider.id,
        api_key: apiKey,
        default_model: selectedModel,
      });

      // Update local state
      setProviders((prev) =>
        prev.map((p) =>
          p.id === selectedProvider.id
            ? { ...p, apiKey: '****', enabled: true, defaultModel: selectedModel }
            : p
        )
      );

      toast({
        title: 'Configuration saved',
        description: `${selectedProvider.name} has been configured.`,
      });
      setSelectedProvider(null);
      setApiKey('');
      setTestResult(null);
    } catch (error) {
      toast({
        title: 'Save failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    }
  };

  const handleToggleProvider = async (providerId: string, enabled: boolean) => {
    try {
      await api.put('/config/llm/toggle', {
        provider_id: providerId,
        enabled,
      });
      setProviders((prev) =>
        prev.map((p) => (p.id === providerId ? { ...p, enabled } : p))
      );
    } catch (error) {
      toast({
        title: 'Failed to toggle provider',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (providerId: string) => {
    if (!confirm('Are you sure you want to remove this provider configuration?')) {
      return;
    }

    try {
      await api.delete(`/config/llm/${providerId}`);
      setProviders((prev) => prev.map((p) => (p.id === providerId ? { ...p, apiKey: undefined, enabled: false } : p)));
      toast({
        title: 'Configuration removed',
        description: 'The provider configuration has been deleted.',
      });
    } catch (error) {
      toast({
        title: 'Delete failed',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>LLM Providers</CardTitle>
          <CardDescription>
            Configure AI providers for natural language querying
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {availableProviders.map((provider) => {
              const configured = providers.find((p) => p.id === provider.id);
              const isEnabled = configured?.enabled || false;
              const hasApiKey = !!configured?.apiKey;

              return (
                <Card key={provider.id} className={cn(!isEnabled && 'opacity-60')}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{provider.icon}</span>
                        <div>
                          <CardTitle className="text-base">{provider.name}</CardTitle>
                          {hasApiKey && (
                            <Badge variant="secondary" className="text-xs">
                              Configured
                            </Badge>
                          )}
                        </div>
                      </div>
                      <Switch
                        checked={isEnabled}
                        onCheckedChange={(checked) => handleToggleProvider(provider.id, checked)}
                      />
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <Label className="text-xs text-muted-foreground">Model</Label>
                      <p className="text-sm font-medium">
                        {configured?.defaultModel || provider.defaultModel}
                      </p>
                    </div>

                    {hasApiKey ? (
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1"
                          onClick={() => handleConfigure({ ...provider, ...configured })}
                        >
                          <Settings2 className="h-4 w-4 mr-2" />
                          Configure
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(provider.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => handleConfigure(provider)}
                      >
                        <Key className="h-4 w-4 mr-2" />
                        Setup API Key
                      </Button>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Configuration Dialog */}
      {selectedProvider && (
        <Dialog open={!!selectedProvider} onOpenChange={(open) => !open && setSelectedProvider(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <span className="text-2xl">{selectedProvider.icon}</span>
                Configure {selectedProvider.name}
              </DialogTitle>
              <DialogDescription>
                Enter your API key and select the default model
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="api-key">API Key</Label>
                <div className="relative">
                  <Input
                    id="api-key"
                    type={showApiKey ? 'text' : 'password'}
                    placeholder="sk-..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="pr-20 font-mono text-sm"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowApiKey(!showApiKey)}
                  >
                    {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  Your API key will be encrypted and stored securely.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="model">Model</Label>
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger id="model">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {selectedProvider.models.map((model) => (
                      <SelectItem key={model} value={model}>
                        {model}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={handleTest}
                disabled={isTesting || !apiKey}
              >
                <TestTube className="h-4 w-4 mr-2" />
                {isTesting ? 'Testing...' : 'Test Connection'}
              </Button>

              {testResult === 'success' && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <Check className="h-4 w-4" />
                  API key is valid! You can now save the configuration.
                </div>
              )}

              {testResult === 'error' && (
                <div className="flex items-center gap-2 text-sm text-red-600">
                  <X className="h-4 w-4" />
                  API key is invalid or the service is unreachable.
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setSelectedProvider(null)}
                >
                  Cancel
                </Button>
                <LoadingButton
                  className="flex-1"
                  onClick={handleSave}
                  disabled={!apiKey || testResult !== 'success'}
                  loadingText="Saving..."
                >
                  Save Configuration
                </LoadingButton>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Tips Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Getting Started
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>• Get an API key from your LLM provider's dashboard</p>
          <p>• Test your API key before saving to ensure it works</p>
          <p>• You can configure multiple providers and switch between them</p>
          <p>• API keys are encrypted and stored securely</p>
          <p>• Toggle providers on/off to switch between them quickly</p>
        </CardContent>
      </Card>
    </div>
  );
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}
