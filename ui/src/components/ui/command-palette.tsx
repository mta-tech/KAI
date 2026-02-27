'use client';

import * as React from 'react';
import { Command } from 'cmdk';
import { Search, FileText, Database, Settings, Layers, MessageSquare, BookOpen, Home, ScrollText } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useSidebarStore } from '@/stores/sidebar-store';
import { cn } from '@/lib/utils';
import type { KeyboardShortcut } from '@/lib/hooks/use-keyboard-shortcuts';
import { formatShortcut } from '@/lib/hooks/use-keyboard-shortcuts';

export interface CommandItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
  keywords?: string[];
  shortcut?: Omit<KeyboardShortcut, 'action'>;
  category?: string;
}

interface CommandPaletteProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

const categories = {
  navigation: 'Navigation',
  chat: 'Chat',
  knowledge: 'Knowledge',
  settings: 'Settings',
  utilities: 'Utilities',
} as const;

export function CommandPalette({ open: controlledOpen, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();
  const { open: openSidebar, close: closeSidebar } = useSidebarStore();
  const [internalOpen, setInternalOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');
  const inputRef = React.useRef<HTMLInputElement>(null);
  const listRef = React.useRef<HTMLDivElement>(null);

  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = onOpenChange || setInternalOpen;

  // Define all available commands
  const commands: CommandItem[] = React.useMemo(() => [
    // Navigation commands
    {
      id: 'nav-dashboard',
      label: 'Go to Dashboard',
      icon: Home,
      action: () => router.push('/'),
      keywords: ['home', 'dashboard', 'main'],
      category: categories.navigation,
    },
    {
      id: 'nav-connections',
      label: 'Go to Connections',
      icon: Database,
      action: () => router.push('/connections'),
      keywords: ['database', 'connections', 'db'],
      category: categories.navigation,
    },
    {
      id: 'nav-schema',
      label: 'Go to Schema Browser',
      icon: FileText,
      action: () => router.push('/schema'),
      keywords: ['schema', 'tables', 'browse'],
      category: categories.navigation,
    },
    {
      id: 'nav-mdl',
      label: 'Go to MDL Semantic Layer',
      icon: Layers,
      action: () => router.push('/mdl'),
      keywords: ['mdl', 'semantic', 'layer'],
      category: categories.navigation,
    },
    {
      id: 'nav-chat',
      label: 'Go to Interactive Chat',
      icon: MessageSquare,
      action: () => router.push('/chat'),
      keywords: ['chat', 'ai', 'query'],
      category: categories.navigation,
    },
    {
      id: 'nav-knowledge',
      label: 'Go to Knowledge Base',
      icon: BookOpen,
      action: () => router.push('/knowledge'),
      keywords: ['knowledge', 'docs', 'documentation'],
      category: categories.navigation,
    },
    {
      id: 'nav-logs',
      label: 'Go to Execution Logs',
      icon: ScrollText,
      action: () => router.push('/logs'),
      keywords: ['logs', 'history', 'execution'],
      category: categories.navigation,
    },
    // Utility commands
    {
      id: 'util-toggle-sidebar',
      label: 'Toggle Sidebar',
      icon: Layers,
      action: () => {
        if (window.innerWidth < 768) {
          openSidebar();
        }
      },
      keywords: ['sidebar', 'menu', 'toggle', 'navigation'],
      category: categories.utilities,
    },
    {
      id: 'util-shortcuts',
      label: 'Show Keyboard Shortcuts',
      icon: Search,
      action: () => {
        setOpen(false);
        // Trigger keyboard shortcuts modal
        window.dispatchEvent(new CustomEvent('open-keyboard-shortcuts'));
      },
      keywords: ['shortcuts', 'keyboard', 'help', 'keys'],
      category: categories.utilities,
    },
  ], [router, openSidebar]);

  // Register keyboard shortcut for opening command palette
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K to open command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(!open);
      }
      // Escape to close
      if (e.key === 'Escape' && open) {
        e.preventDefault();
        setOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, setOpen]);

  // Focus input when opened
  React.useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);

  // Filter commands based on search
  const filteredCommands = React.useMemo(() => {
    if (!search) return commands;

    const searchLower = search.toLowerCase();
    return commands.filter((command) => {
      const labelMatch = command.label.toLowerCase().includes(searchLower);
      const keywordMatch = command.keywords?.some((keyword) =>
        keyword.toLowerCase().includes(searchLower)
      );
      const categoryMatch = command.category?.toLowerCase().includes(searchLower);
      return labelMatch || keywordMatch || categoryMatch;
    });
  }, [commands, search]);

  // Group commands by category
  const groupedCommands = React.useMemo(() => {
    const groups: Record<string, CommandItem[]> = {};
    filteredCommands.forEach((command) => {
      const category = command.category || 'Other';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(command);
    });
    return groups;
  }, [filteredCommands]);

  const handleSelect = (command: CommandItem) => {
    command.action();
    setOpen(false);
    setSearch('');
  };

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] px-4"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => setOpen(false)}
        aria-hidden="true"
      />

      {/* Command Palette */}
      <div className="relative w-full max-w-lg overflow-hidden rounded-lg border bg-background shadow-lg">
        {/* Search Input */}
        <div className="flex items-center border-b px-3">
          <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
          <Command.Input
            ref={inputRef}
            value={search}
            onValueChange={setSearch}
            placeholder="Type a command or search..."
            className="flex h-12 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
          />
          <kbd className="ml-2 hidden h-5 shrink-0 items-center gap-1 rounded border bg-muted px-2 text-[10px] font-medium opacity-50 sm:inline-flex">
            <span className="text-xs">⌘</span>K
          </kbd>
        </div>

        {/* Commands List */}
        <Command.List
          ref={listRef}
          className="max-h-[300px] overflow-y-auto overflow-x-hidden p-2"
        >
          {!filteredCommands.length ? (
            <div className="py-6 text-center text-sm text-muted-foreground">
              No commands found.
            </div>
          ) : (
            <>
              {Object.entries(groupedCommands).map(([category, categoryCommands]) => (
                <Command.Group key={category} heading={category}>
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                    {category}
                  </div>
                  {categoryCommands.map((command) => (
                    <Command.Item
                      key={command.id}
                      onSelect={() => handleSelect(command)}
                      className="relative flex cursor-pointer select-none items-center rounded-md px-2 py-2 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                    >
                      <command.icon className="mr-2 h-4 w-4" />
                      <span className="flex-1">{command.label}</span>
                      {command.shortcut && (
                        <kbd className="ml-2 text-xs text-muted-foreground">
                          {formatShortcut(command.shortcut)}
                        </kbd>
                      )}
                    </Command.Item>
                  ))}
                </Command.Group>
              ))}
            </>
          )}
        </Command.List>

        {/* Footer */}
        <div className="flex items-center justify-between border-t p-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <kbd className="rounded border bg-muted px-1.5 py-0.5">↑↓</kbd>
            <span>to navigate</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="rounded border bg-muted px-1.5 py-0.5">↵</kbd>
            <span>to select</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="rounded border bg-muted px-1.5 py-0.5">esc</kbd>
            <span>to close</span>
          </div>
        </div>
      </div>
    </Command.Dialog>
  );
}

// Mobile trigger button
interface CommandTriggerProps {
  className?: string;
}

export function CommandTrigger({ className }: CommandTriggerProps) {
  const [open, setOpen] = React.useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className={cn(
          'inline-flex items-center gap-2 rounded-md border bg-background px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground',
          className
        )}
      >
        <Search className="h-4 w-4" />
        <span>Search...</span>
        <kbd className="ml-auto hidden rounded border bg-muted px-1.5 py-0.5 text-xs lg:inline-block">
          ⌘K
        </kbd>
      </button>
      <CommandPalette open={open} onOpenChange={setOpen} />
    </>
  );
}
