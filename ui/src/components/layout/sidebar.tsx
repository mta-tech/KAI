'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import {
  LayoutDashboard,
  Database,
  Table2,
  Layers,
  MessageSquare,
  BookOpen,
  ScrollText,
  Settings,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Sheet,
  SheetContent,
} from '@/components/ui/sheet';
import { useSidebarStore } from '@/stores/sidebar-store';
import { Button } from '@/components/ui/button';
import { Logo } from '@/components/logo';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Connections', href: '/connections', icon: Database },
  { name: 'Schema', href: '/schema', icon: Table2 },
  { name: 'MDL', href: '/mdl', icon: Layers },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Knowledge', href: '/knowledge', icon: BookOpen },
  { name: 'Logs', href: '/logs', icon: ScrollText },
  { name: 'Settings', href: '/settings', icon: Settings },
];

function SidebarContent({ pathname }: { pathname: string }) {
  return (
    <>
      <div className="flex h-14 items-center justify-between border-b px-6">
        <div onClick={() => useSidebarStore.getState().close()} className="cursor-pointer">
          <Logo />
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden h-11 w-11"
          onClick={() => useSidebarStore.getState().close()}
          aria-label="Close sidebar"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>
      <nav className="flex-1 space-y-1 p-3 overflow-y-auto" aria-label="Primary navigation">
        {navigation.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={() => useSidebarStore.getState().close()}
              className={cn(
                'group flex items-center gap-3 rounded-md px-3 py-3 text-sm font-medium transition-all duration-200 ease-in-out min-h-[44px]',
                isActive
                  ? 'bg-primary/5 text-primary shadow-sm ring-1 ring-primary/10'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground hover:translate-x-1'
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              <item.icon className={cn("h-4 w-4 transition-colors", isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground")} aria-hidden="true" />
              {item.name}
              {isActive && (
                <div className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" aria-hidden="true" />
              )}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4 bg-muted/10" role="contentinfo" aria-label="Version information">
        <div className="flex items-center justify-between">
          <p className="text-xs font-mono text-muted-foreground">v0.1.0-beta</p>
          <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" title="System Online" aria-label="System online" />
        </div>
      </div>
    </>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const { isOpen, close, isMobile } = useSidebarStore();
  const [isMounted, setIsMounted] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true);

    // Check if mobile on mount and resize
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      useSidebarStore.getState().setMobile(mobile);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  if (!isMounted) {
    return null;
  }

  return (
    <>
      {/* Desktop Sidebar - always visible on md+ screens */}
      <div
        className="hidden md:flex h-full w-64 flex-col border-r bg-card/50 backdrop-blur-xl transition-all duration-300"
        role="navigation"
        aria-label="Main navigation"
      >
        <SidebarContent pathname={pathname} />
      </div>

      {/* Mobile Sidebar - shown as Sheet */}
      {isMobile && (
        <Sheet open={isOpen} onOpenChange={(open) => !open && close()}>
          <SheetContent
            side="left"
            className="md:hidden w-[min(280px,85vw)] max-w-[320px] p-0"
            onPointerDownOutside={(e) => {
              e.preventDefault();
              close();
            }}
            onEscapeKeyDown={close}
            aria-label="Mobile navigation"
          >
            <div className="flex h-full flex-col">
              <SidebarContent pathname={pathname} />
            </div>
          </SheetContent>
        </Sheet>
      )}
    </>
  );
}
