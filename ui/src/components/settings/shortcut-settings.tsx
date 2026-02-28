'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';

const SHORTCUTS = [
  { key: '?', description: 'Open keyboard shortcuts' },
  { key: 'Cmd + K', description: 'Command palette' },
  { key: 'Cmd + /', description: 'Focus search' },
  { key: 'Esc', description: 'Close modal/drawer' },
];

interface ShortcutSettingsProps {
  onChange: () => void;
}

export function ShortcutSettings({ onChange }: ShortcutSettingsProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Keyboard Shortcuts</CardTitle>
          <CardDescription>Customize keyboard shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {SHORTCUTS.map((shortcut) => (
              <div key={shortcut.key} className="flex items-center justify-between py-2">
                <span className="text-sm">{shortcut.description}</span>
                <kbd className="px-2 py-1 text-xs font-mono bg-muted rounded">
                  {shortcut.key}
                </kbd>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Shortcut Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Enable vim mode</Label>
              <p className="text-sm text-muted-foreground">Use vim keybindings in text inputs</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Modifier key</Label>
              <p className="text-sm text-muted-foreground">Primary modifier for shortcuts</p>
            </div>
            <Select defaultValue="cmd" onValueChange={onChange}>
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cmd">Command</SelectItem>
                <SelectItem value="ctrl">Control</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
