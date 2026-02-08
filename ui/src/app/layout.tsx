import type { Metadata } from 'next';
import localFont from 'next/font/local';
import { Suspense } from 'react';
import './globals.css';
import { Providers } from './providers';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';
import { SkipLink } from '@/components/layout/skip-link';
import { KeyboardShortcutsProvider } from '@/components/providers/keyboard-shortcuts-provider';
import { PageLoadingFallback } from '@/components/streaming-fallback';
import { ErrorBoundary } from '@/components/error-boundary';
import { CommandPalette } from '@/components/ui/command-palette';
import { PageTransition } from '@/components/ui/page-transition';

const geistSans = localFont({
  src: './fonts/GeistVF.woff',
  variable: '--font-geist-sans',
  weight: '100 900',
});
const geistMono = localFont({
  src: './fonts/GeistMonoVF.woff',
  variable: '--font-geist-mono',
  weight: '100 900',
});

export const metadata: Metadata = {
  title: 'KAI Admin',
  description: 'KAI Admin UI - Database intelligence and analysis',
  manifest: '/manifest.json',
  themeColor: '#6366f1',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'KAI',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <Providers>
          <KeyboardShortcutsProvider />
          <SkipLink />
          <CommandPalette />
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
              <Header />
              <main className="flex-1 overflow-hidden" aria-labelledby="page-title" id="main-content">
                <ErrorBoundary>
                  <Suspense fallback={<PageLoadingFallback />}>
                    <PageTransition>
                      {children}
                    </PageTransition>
                  </Suspense>
                </ErrorBoundary>
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
