'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Keyboard } from 'lucide-react';
import type { KeyboardShortcut } from '@/lib/hooks/use-keyboard-shortcuts';
import { formatShortcut } from '@/lib/hooks/use-keyboard-shortcuts';

interface KeyboardShortcutsModalProps {
  shortcuts: KeyboardShortcut[];
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

/**
 * Modal displaying all available keyboard shortcuts
 * Press ? to open
 */
export function KeyboardShortcutsModal({
  shortcuts,
  open: controlledOpen,
  onOpenChange,
}: KeyboardShortcutsModalProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = onOpenChange || setInternalOpen;

  // Group shortcuts by category
  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    const category = shortcut.category || 'General';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(shortcut);
    return acc;
  }, {} as Record<string, KeyboardShortcut[]>);

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        className="fixed bottom-4 right-4 z-40 opacity-50 hover:opacity-100"
        onClick={() => setOpen(true)}
        aria-label="Open keyboard shortcuts"
      >
        <Keyboard className="h-4 w-4" />
        <span className="ml-2">?</span>
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Keyboard Shortcuts</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 max-h-[60vh] overflow-y-auto">
            {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
              <div key={category}>
                <h3 className="text-sm font-semibold text-muted-foreground mb-2">
                  {category}
                </h3>
                <div className="space-y-2">
                  {categoryShortcuts.map((shortcut, index) => (
                    <div
                      key={`${category}-${index}`}
                      className="flex items-center justify-between text-sm"
                    >
                      <span className="text-foreground">{shortcut.description}</span>
                      <kbd className="px-2 py-1 text-xs font-semibold text-muted-foreground bg-muted rounded">
                        {formatShortcut(shortcut)}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <div className="pt-4 border-t text-xs text-muted-foreground">
              <p>Tip: Press <kbd className="px-1 py-0.5 bg-muted rounded">Esc</kbd> to close this modal</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

interface KeyboardShortcutProps extends KeyboardShortcut {
  category?: string;
}
