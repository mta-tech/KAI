'use client';

import { useEffect, useRef } from 'react';

export interface KeyboardShortcut {
  key: string;
  description: string;
  action: () => void;
  metaKey?: boolean;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  category?: string;
}

interface KeyboardShortcutsMap {
  [key: string]: KeyboardShortcut;
}

/**
 * Hook to register global keyboard shortcuts
 * 
 * @param shortcuts - Map of keyboard shortcuts
 * @param enabled - Whether shortcuts are enabled
 */
export function useKeyboardShortcuts(
  shortcuts: KeyboardShortcut[],
  enabled: boolean = true
) {
  const shortcutsRef = useRef<KeyboardShortcutsMap>({});

  useEffect(() => {
    if (!enabled) return;

    // Build shortcuts map for easy lookup
    shortcutsRef.current = shortcuts.reduce((acc, shortcut) => {
      const keyCombo = buildKeyCombo(shortcut);
      acc[keyCombo] = shortcut;
      return acc;
    }, {} as KeyboardShortcutsMap);

    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger shortcuts when user is typing in an input
      const target = e.target as HTMLElement;
      const isInputElement = 
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable;

      if (isInputElement && e.key !== 'Escape') {
        return;
      }

      // Check if this key combination matches any shortcut
      const keyCombo = buildKeyCombo({
        key: e.key,
        metaKey: e.metaKey,
        ctrlKey: e.ctrlKey,
        shiftKey: e.shiftKey,
        altKey: e.altKey,
      } as KeyboardShortcut);

      const shortcut = shortcutsRef.current[keyCombo];
      if (shortcut) {
        e.preventDefault();
        shortcut.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts, enabled]);
}

/**
 * Build a unique key combination string for a keyboard event
 */
function buildKeyCombo(shortcut: Pick<KeyboardShortcut, 'key' | 'metaKey' | 'ctrlKey' | 'shiftKey' | 'altKey'>): string {
  const parts: string[] = [];
  if (shortcut.metaKey) parts.push('meta');
  if (shortcut.ctrlKey) parts.push('ctrl');
  if (shortcut.shiftKey) parts.push('shift');
  if (shortcut.altKey) parts.push('alt');
  parts.push(shortcut.key.toLowerCase());
  return parts.join('+');
}

/**
 * Format a keyboard shortcut for display
 */
export function formatShortcut(shortcut: Pick<KeyboardShortcut, 'key' | 'metaKey' | 'ctrlKey' | 'shiftKey' | 'altKey'>): string {
  const parts: string[] = [];
  if (shortcut.metaKey) parts.push('⌘');
  if (shortcut.ctrlKey) parts.push('Ctrl');
  if (shortcut.shiftKey) parts.push('Shift');
  if (shortcut.altKey) parts.push('Alt');
  parts.push(formatKey(shortcut.key));
  return parts.join(' + ');
}

/**
 * Format a single key for display
 */
function formatKey(key: string): string {
  const keyMap: Record<string, string> = {
    ' ': 'Space',
    'arrowup': '↑',
    'arrowdown': '↓',
    'arrowleft': '←',
    'arrowright': '→',
    'escape': 'Esc',
    'enter': 'Enter',
    'tab': 'Tab',
    'backspace': 'Backspace',
    'delete': 'Delete',
  };
  return keyMap[key.toLowerCase()] || key.toUpperCase();
}
