'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Database,
  Table2,
  Layers,
  MessageSquare,
  BookOpen,
  ScrollText,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Connections', href: '/connections', icon: Database },
  { name: 'Schema', href: '/schema', icon: Table2 },
  { name: 'MDL', href: '/mdl', icon: Layers },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Knowledge', href: '/knowledge', icon: BookOpen },
  { name: 'Logs', href: '/logs', icon: ScrollText },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col border-r bg-card/50 backdrop-blur-xl transition-all duration-300">
      <div className="flex h-14 items-center border-b px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Layers className="h-5 w-5" />
          </div>
          <span className="font-mono tracking-tight">KAI_ADMIN</span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {navigation.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'group flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-in-out',
                isActive
                  ? 'bg-primary/5 text-primary shadow-sm ring-1 ring-primary/10'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground hover:translate-x-1'
              )}
            >
              <item.icon className={cn("h-4 w-4 transition-colors", isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground")} />
              {item.name}
              {isActive && (
                <div className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" />
              )}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4 bg-muted/10">
        <div className="flex items-center justify-between">
            <p className="text-xs font-mono text-muted-foreground">v0.1.0-beta</p>
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" title="System Online" />
        </div>
      </div>
    </div>
  );
}
