'use client';

import { usePathname } from 'next/navigation';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useSidebarStore } from '@/stores/sidebar-store';
import { CommandTrigger } from '@/components/ui/command-palette';
import { ThemeToggle } from '@/components/ui/theme-toggle';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/connections': 'Database Connections',
  '/schema': 'Schema Browser',
  '/mdl': 'MDL Semantic Layer',
  '/chat': 'Interactive Chat',
  '/knowledge': 'Knowledge Base',
  '/logs': 'Execution Logs',
};

export function Header() {
  const pathname = usePathname();
  const { open, isMobile } = useSidebarStore();

  const title = pageTitles[pathname] ||
    Object.entries(pageTitles).find(([path]) =>
      path !== '/' && pathname.startsWith(path)
    )?.[1] ||
    'KAI Admin';

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background/50 px-6 backdrop-blur-sm sticky top-0 z-10 transition-all" role="banner">
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden h-11 w-11"
        onClick={open}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <nav className="flex items-center gap-2 text-sm font-medium text-muted-foreground" aria-label="Breadcrumb navigation">
         <span className="hover:text-foreground transition-colors cursor-default">Admin</span>
         <span className="text-muted-foreground/40" aria-hidden="true">/</span>
      </nav>
      <h1 className="text-lg font-semibold tracking-tight text-foreground" id="page-title">{title}</h1>

      <div className="ml-auto flex items-center gap-2">
        <CommandTrigger className="hidden md:flex" />
        <ThemeToggle />
      </div>
    </header>
  );
}
