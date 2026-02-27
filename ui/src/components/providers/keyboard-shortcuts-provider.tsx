'use client';

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useKeyboardShortcuts } from '@/lib/hooks/use-keyboard-shortcuts';
import { KeyboardShortcutsModal } from '@/components/ui/keyboard-shortcuts-modal';
import { useState } from 'react';

const globalShortcuts = [
  {
    key: '?',
    description: 'Show keyboard shortcuts',
    action: () => {
      // This will be handled by the component state
      const event = new CustomEvent('toggle-shortcuts');
      window.dispatchEvent(event);
    },
    category: 'General',
  },
  {
    key: 'k',
    description: 'Go to Knowledge Base',
    action: () => {
      // Navigate to knowledge page
    },
    metaKey: true,
    shiftKey: true,
    category: 'Navigation',
  },
  {
    key: 'c',
    description: 'Go to Chat',
    action: () => {
      // Navigate to chat page
    },
    metaKey: true,
    shiftKey: true,
    category: 'Navigation',
  },
  {
    key: 'd',
    description: 'Go to Dashboard',
    action: () => {
      // Navigate to dashboard page
    },
    metaKey: true,
    shiftKey: true,
    category: 'Navigation',
  },
  {
    key: 's',
    description: 'Go to Schema',
    action: () => {
      // Navigate to schema page
    },
    metaKey: true,
    shiftKey: true,
    category: 'Navigation',
  },
  {
    key: 'Escape',
    description: 'Close modal or return to home',
    action: () => {
      // Handle escape key globally
    },
    category: 'General',
  },
];

export function KeyboardShortcutsProvider() {
  const router = useRouter();
  const pathname = usePathname();
  const [shortcutsModalOpen, setShortcutsModalOpen] = useState(false);

  // Update shortcuts with router actions
  useEffect(() => {
    globalShortcuts[1].action = () => router.push('/knowledge');
    globalShortcuts[2].action = () => router.push('/chat');
    globalShortcuts[3].action = () => router.push('/');
    globalShortcuts[4].action = () => router.push('/schema');
    globalShortcuts[5].action = () => {
      if (pathname !== '/') {
        router.push('/');
      }
    };
  }, [router, pathname]);

  // Listen for toggle shortcuts event
  useEffect(() => {
    const handleToggleShortcuts = () => {
      setShortcutsModalOpen(prev => !prev);
    };
    window.addEventListener('toggle-shortcuts', handleToggleShortcuts);
    return () => window.removeEventListener('toggle-shortcuts', handleToggleShortcuts);
  }, []);

  useKeyboardShortcuts(globalShortcuts);

  return (
    <KeyboardShortcutsModal
      shortcuts={globalShortcuts}
      open={shortcutsModalOpen}
      onOpenChange={setShortcutsModalOpen}
    />
  );
}
