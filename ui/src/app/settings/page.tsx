'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
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
import { GeneralSettings } from '@/components/settings/general-settings';
import { AppearanceSettings } from '@/components/settings/appearance-settings';
import { NotificationSettings } from '@/components/settings/notification-settings';
import { ShortcutSettings } from '@/components/settings/shortcut-settings';

type SettingsSection = 'general' | 'appearance' | 'connections' | 'chat' | 'notifications' | 'privacy' | 'shortcuts';

interface Section {
  id: SettingsSection;
  name: string;
  icon: typeof Settings;
  description: string;
}

const sections: Section[] = [
  { id: 'general', name: 'General', icon: GeneralIcon, description: 'Basic application settings' },
  { id: 'appearance', name: 'Appearance', icon: Palette, description: 'Theme and display options' },
  { id: 'connections', name: 'Connections', icon: Database, description: 'Database connection defaults' },
  { id: 'chat', name: 'Chat', icon: MessageSquare, description: 'AI chat behavior settings' },
  { id: 'notifications', name: 'Notifications', icon: Bell, description: 'Alert and notification preferences' },
  { id: 'privacy', name: 'Privacy', icon: Shield, description: 'Data and security settings' },
  { id: 'shortcuts', name: 'Shortcuts', icon: Keyboard, description: 'Keyboard shortcut configuration' },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState<SettingsSection>('general');
  const [searchQuery, setSearchQuery] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const currentSection = sections.find((s) => s.id === activeSection)!;
  const { icon: Icon } = currentSection;
  const markChanged = () => setHasChanges(true);

  const handleSave = async () => {
    setIsSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    setHasChanges(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  const handleReset = () => setHasChanges(false);

  const filteredSections = sections.filter((s) =>
    !searchQuery ||
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="h-6 w-6 text-muted-foreground" />
            <div>
              <h1 className="text-2xl font-semibold">Settings</h1>
              <p className="text-sm text-muted-foreground">Manage your application preferences</p>
            </div>
          </div>
          {hasChanges && (
            <div className="flex items-center gap-2">
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
                {isSaving ? 'Saving...' : saveSuccess ? (
                  <><Check className="h-4 w-4 mr-2" />Saved</>
                ) : (
                  <><Save className="h-4 w-4 mr-2" />Save Changes</>
                )}
              </Button>
              <Badge variant="secondary" className="ml-2">Unsaved changes</Badge>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Navigation */}
        <div className="w-64 border-r bg-muted/10">
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
          <ScrollArea className="flex-1">
            <nav className="p-2 space-y-1" aria-label="Settings navigation">
              {filteredSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={cn(
                    'w-full flex items-start gap-3 rounded-md px-3 py-2 text-left transition-colors',
                    activeSection === section.id
                      ? 'bg-primary/10 text-primary'
                      : 'hover:bg-muted/50',
                  )}
                  aria-current={activeSection === section.id ? 'page' : undefined}
                >
                  <section.icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{section.name}</p>
                    <p className="text-xs text-muted-foreground truncate">{section.description}</p>
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

            {activeSection === 'general' && <GeneralSettings onChange={markChanged} />}
            {activeSection === 'appearance' && <AppearanceSettings onChange={markChanged} />}
            {activeSection === 'connections' && <ConnectionManager />}
            {activeSection === 'chat' && <LLMConfig />}
            {activeSection === 'notifications' && <NotificationSettings onChange={markChanged} />}
            {activeSection === 'privacy' && <DangerZone />}
            {activeSection === 'shortcuts' && <ShortcutSettings onChange={markChanged} />}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
