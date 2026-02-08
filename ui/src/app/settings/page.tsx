'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import {
  Settings,
  Search,
  Save,
  RotateCcw,
  Check,
  Settings as GeneralIcon,
  Palette,
  Database,
  MessageSquare,
  Bell,
  Shield,
  Keyboard,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ConnectionManager } from '@/components/settings/connection-manager';
import { LLMConfig } from '@/components/settings/llm-config';
import { DangerZone } from '@/components/settings/danger-zone';

type SettingsSection = 'general' | 'appearance' | 'connections' | 'chat' | 'notifications' | 'privacy' | 'shortcuts';

interface Section {
  id: SettingsSection;
  name: string;
  icon: typeof Settings;
  description: string;
}

const sections: Section[] = [
  {
    id: 'general',
    name: 'General',
    icon: GeneralIcon,
    description: 'Basic application settings',
  },
  {
    id: 'appearance',
    name: 'Appearance',
    icon: Palette,
    description: 'Theme and display options',
  },
  {
    id: 'connections',
    name: 'Connections',
    icon: Database,
    description: 'Database connection defaults',
  },
  {
    id: 'chat',
    name: 'Chat',
    icon: MessageSquare,
    description: 'AI chat behavior settings',
  },
  {
    id: 'notifications',
    name: 'Notifications',
    icon: Bell,
    description: 'Alert and notification preferences',
  },
  {
    id: 'privacy',
    name: 'Privacy',
    icon: Shield,
    description: 'Data and security settings',
  },
  {
    id: 'shortcuts',
    name: 'Shortcuts',
    icon: Keyboard,
    description: 'Keyboard shortcut configuration',
  },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState<SettingsSection>('general');
  const [searchQuery, setSearchQuery] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const currentSection = sections.find((s) => s.id === activeSection)!;
  const { icon: Icon } = currentSection;

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate save operation
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    setHasChanges(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  const handleReset = () => {
    // Reset to defaults
    setHasChanges(false);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="h-6 w-6 text-muted-foreground" />
            <div>
              <h1 className="text-2xl font-semibold">Settings</h1>
              <p className="text-sm text-muted-foreground">
                Manage your application preferences
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {hasChanges && (
              <>
                <Button variant="outline" size="sm" onClick={handleReset}>
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                  disabled={isSaving}
                  className={cn(saveSuccess && 'bg-green-600 hover:bg-green-700')}
                >
                  {isSaving ? (
                    'Saving...'
                  ) : saveSuccess ? (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Saved
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
              </>
            )}
            {hasChanges && (
              <Badge variant="secondary" className="ml-2">
                Unsaved changes
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Navigation */}
        <div className="w-64 border-r bg-muted/10">
          {/* Search */}
          <div className="p-4 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search settings..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Navigation */}
          <ScrollArea className="flex-1">
            <nav className="p-2 space-y-1" aria-label="Settings navigation">
              {sections
                .filter((s) =>
                  !searchQuery ||
                  s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                  s.description.toLowerCase().includes(searchQuery.toLowerCase())
                )
                .map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={cn(
                      'w-full flex items-start gap-3 rounded-md px-3 py-2 text-left transition-colors',
                      activeSection === section.id
                        ? 'bg-primary/10 text-primary'
                        : 'hover:bg-muted/50'
                    )}
                    aria-current={activeSection === section.id ? 'page' : undefined}
                  >
                    <section.icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{section.name}</p>
                      <p className="text-xs text-muted-foreground truncate">
                        {section.description}
                      </p>
                    </div>
                  </button>
                ))}
            </nav>
          </ScrollArea>
        </div>

        {/* Settings Content */}
        <ScrollArea className="flex-1">
          <div className="p-6 max-w-3xl">
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <Icon className="h-6 w-6 text-muted-foreground" />
                <h2 className="text-xl font-semibold">{currentSection.name}</h2>
              </div>
              <p className="text-muted-foreground">{currentSection.description}</p>
            </div>

            <Separator className="mb-6" />

            {/* Settings Sections */}
            {activeSection === 'general' && <GeneralSettings onChange={() => setHasChanges(true)} />}
            {activeSection === 'appearance' && <AppearanceSettings onChange={() => setHasChanges(true)} />}
            {activeSection === 'connections' && <ConnectionManager />}
            {activeSection === 'chat' && <LLMConfig />}
            {activeSection === 'notifications' && <NotificationSettings onChange={() => setHasChanges(true)} />}
            {activeSection === 'privacy' && <DangerZone />}
            {activeSection === 'shortcuts' && <ShortcutSettings onChange={() => setHasChanges(true)} />}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}

// Settings Section Components

function GeneralSettings({ onChange }: { onChange: () => void }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Application</CardTitle>
          <CardDescription>Basic application preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Language</Label>
              <p className="text-sm text-muted-foreground">Select your preferred language</p>
            </div>
            <Select defaultValue="en" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="id">Bahasa Indonesia</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Timezone</Label>
              <p className="text-sm text-muted-foreground">Set your timezone</p>
            </div>
            <Select defaultValue="auto" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto-detect</SelectItem>
                <SelectItem value="utc">UTC</SelectItem>
                <SelectItem value="est">Eastern Time</SelectItem>
                <SelectItem value="pst">Pacific Time</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Data & Storage</CardTitle>
          <CardDescription>Manage your data preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Auto-save drafts</Label>
              <p className="text-sm text-muted-foreground">Automatically save work in progress</p>
            </div>
            <Switch defaultChecked onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Clear cache on exit</Label>
              <p className="text-sm text-muted-foreground">Remove cached data when closing</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function AppearanceSettings({ onChange }: { onChange: () => void }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Theme</CardTitle>
          <CardDescription>Customize the appearance</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Color Theme</Label>
              <p className="text-sm text-muted-foreground">Choose your preferred color scheme</p>
            </div>
            <Select defaultValue="system" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="system">System</SelectItem>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Accent Color</Label>
              <p className="text-sm text-muted-foreground">Primary color for the UI</p>
            </div>
            <Select defaultValue="indigo" onValueChange={onChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="indigo">Indigo</SelectItem>
                <SelectItem value="blue">Blue</SelectItem>
                <SelectItem value="green">Green</SelectItem>
                <SelectItem value="purple">Purple</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Compact Mode</Label>
              <p className="text-sm text-muted-foreground">Use smaller spacing</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Display</CardTitle>
          <CardDescription>Additional display options</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Show animations</Label>
              <p className="text-sm text-muted-foreground">Enable UI animations</p>
            </div>
            <Switch defaultChecked onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Reduce motion</Label>
              <p className="text-sm text-muted-foreground">Minimize animations for accessibility</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function NotificationSettings({ onChange }: { onChange: () => void }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Desktop Notifications</CardTitle>
          <CardDescription>Manage system notifications</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Enable notifications</Label>
              <p className="text-sm text-muted-foreground">Show desktop notifications</p>
            </div>
            <Switch defaultChecked onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Sound</Label>
              <p className="text-sm text-muted-foreground">Play sound for notifications</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Notification Types</CardTitle>
          <CardDescription>Choose what to notify you about</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Query completion</Label>
              <p className="text-sm text-muted-foreground">Notify when queries finish</p>
            </div>
            <Switch defaultChecked onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Errors</Label>
              <p className="text-sm text-muted-foreground">Notify on errors</p>
            </div>
            <Switch defaultChecked onCheckedChange={onChange} />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>System updates</Label>
              <p className="text-sm text-muted-foreground">Notify about updates</p>
            </div>
            <Switch onCheckedChange={onChange} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ShortcutSettings({ onChange }: { onChange: () => void }) {
  const shortcuts = [
    { key: '?', description: 'Open keyboard shortcuts' },
    { key: 'Cmd + K', description: 'Command palette' },
    { key: 'Cmd + /', description: 'Focus search' },
    { key: 'Esc', description: 'Close modal/drawer' },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Keyboard Shortcuts</CardTitle>
          <CardDescription>Customize keyboard shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {shortcuts.map((shortcut) => (
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
