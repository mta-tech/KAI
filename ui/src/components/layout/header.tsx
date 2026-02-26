'use client';

import { usePathname } from 'next/navigation';

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

  const title = pageTitles[pathname] ||
    Object.entries(pageTitles).find(([path]) =>
      path !== '/' && pathname.startsWith(path)
    )?.[1] ||
    'KAI Admin';

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background/50 px-6 backdrop-blur-sm sticky top-0 z-10 transition-all">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
         <span className="hover:text-foreground transition-colors cursor-default">Admin</span>
         <span className="text-muted-foreground/40">/</span>
      </div>
      <h1 className="text-lg font-semibold tracking-tight text-foreground">{title}</h1>
      
      <div className="ml-auto flex items-center gap-2">
      </div>
    </header>
  );
}
