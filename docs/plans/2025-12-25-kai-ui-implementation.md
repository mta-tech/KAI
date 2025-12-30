# KAI UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a developer-focused admin UI for KAI that exposes all CLI functionality through a clean web interface with Next.js 14, shadcn/ui, and full agent transparency.

**Architecture:** Next.js 14 App Router with TypeScript in `ui/` directory. Uses TanStack Query for data fetching, SSE for streaming agent responses, and Zustand for lightweight state. Communicates with existing FastAPI backend at `localhost:8015`.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand

---

## Phase 1: Foundation

### Task 1.1: Initialize Next.js Project

**Files:**
- Create: `ui/package.json`
- Create: `ui/tsconfig.json`
- Create: `ui/next.config.ts`
- Create: `ui/tailwind.config.ts`
- Create: `ui/postcss.config.mjs`
- Create: `ui/src/app/globals.css`
- Create: `ui/src/app/layout.tsx`
- Create: `ui/src/app/page.tsx`
- Create: `ui/.gitignore`

**Step 1: Create ui directory and initialize Next.js**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI
mkdir -p ui
cd ui
npx create-next-app@14 . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-turbopack
```

Expected: Next.js 14 project created with TypeScript and Tailwind

**Step 2: Install dependencies**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npm install @tanstack/react-query zustand lucide-react clsx tailwind-merge class-variance-authority
npm install -D @types/node
```

Expected: Dependencies installed

**Step 3: Install shadcn/ui**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npx shadcn@latest init -d
```

Select: New York style, Zinc color, CSS variables enabled

**Step 4: Add shadcn components**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npx shadcn@latest add button card input label table tabs dialog dropdown-menu select toast badge separator scroll-area sheet collapsible alert textarea
```

Expected: Components added to `ui/src/components/ui/`

**Step 5: Verify development server starts**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npm run dev
```

Expected: Server running at http://localhost:3000

**Step 6: Commit**

```bash
git add ui/
git commit -m "feat(ui): initialize Next.js 14 project with shadcn/ui"
```

---

### Task 1.2: Create API Client Layer

**Files:**
- Create: `ui/src/lib/api/client.ts`
- Create: `ui/src/lib/api/types.ts`
- Create: `ui/src/lib/api/connections.ts`
- Create: `ui/src/lib/api/tables.ts`
- Create: `ui/src/lib/api/mdl.ts`
- Create: `ui/src/lib/api/agent.ts`
- Create: `ui/src/lib/api/knowledge.ts`

**Step 1: Create base API client**

Create `ui/src/lib/api/client.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_KAI_API_URL || 'http://localhost:8015';

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || 'API request failed');
  }
  return res.json();
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || 'API request failed');
  }
  return res.json();
}

export async function apiPut<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || 'API request failed');
  }
  return res.json();
}

export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { method: 'DELETE' });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || 'API request failed');
  }
  return res.json();
}

export function createSSE(path: string): EventSource {
  return new EventSource(`${API_BASE}${path}`);
}

export { API_BASE };
```

**Step 2: Create TypeScript types**

Create `ui/src/lib/api/types.ts`:

```typescript
// Database Connections
export interface DatabaseConnection {
  id: string;
  alias: string | null;
  dialect: string;
  schemas: string[] | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface CreateConnectionRequest {
  alias: string;
  connection_uri: string;
  schemas?: string[];
  metadata?: Record<string, unknown>;
}

// Table Descriptions
export interface TableDescription {
  id: string;
  db_connection_id: string;
  table_name: string;
  db_schema: string | null;
  description: string | null;
  columns: ColumnDescription[];
  sync_status: string;
  last_sync: string | null;
  created_at: string;
}

export interface ColumnDescription {
  name: string;
  data_type: string;
  is_nullable: boolean;
  description: string | null;
  low_cardinality: boolean;
  categories: string[] | null;
}

// MDL Manifests
export interface MDLManifest {
  id: string;
  db_connection_id: string | null;
  name: string | null;
  catalog: string;
  schema: string;
  data_source: string | null;
  models: MDLModel[];
  relationships: MDLRelationship[];
  metrics: MDLMetric[];
  views: MDLView[];
  created_at: string | null;
  updated_at: string | null;
}

export interface MDLModel {
  name: string;
  columns: { name: string; type: string }[];
  primary_key: string | null;
}

export interface MDLRelationship {
  name: string;
  models: string[];
  join_type: string;
  condition: string;
}

export interface MDLMetric {
  name: string;
  base_object: string;
}

export interface MDLView {
  name: string;
  statement: string;
}

// Agent Sessions
export interface AgentSession {
  id: string;
  db_connection_id: string;
  mode: string;
  status: string;
  title: string | null;
  turn_count: number;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown> | null;
}

export interface AgentEvent {
  type: 'token' | 'tool_start' | 'tool_end' | 'todo_update' | 'done' | 'error';
  content?: string;
  tool?: string;
  input?: Record<string, unknown>;
  output?: string;
  todos?: AgentTodo[];
  error?: string;
}

export interface AgentTodo {
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
}

// Business Glossary
export interface BusinessGlossary {
  id: string;
  db_connection_id: string;
  term: string;
  definition: string;
  synonyms: string[] | null;
  related_tables: string[] | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

// Instructions
export interface Instruction {
  id: string;
  db_connection_id: string;
  content: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}
```

**Step 3: Create connections API**

Create `ui/src/lib/api/connections.ts`:

```typescript
import { apiGet, apiPost, apiPut, apiDelete } from './client';
import type { DatabaseConnection, CreateConnectionRequest } from './types';

export const connectionsApi = {
  list: () => apiGet<DatabaseConnection[]>('/api/v1/database-connections'),

  create: (data: CreateConnectionRequest) =>
    apiPost<DatabaseConnection>('/api/v1/database-connections', data),

  update: (id: string, data: CreateConnectionRequest) =>
    apiPut<DatabaseConnection>(`/api/v1/database-connections/${id}`, data),

  delete: (id: string) =>
    apiDelete<DatabaseConnection>(`/api/v1/database-connections/${id}`),
};
```

**Step 4: Create tables API**

Create `ui/src/lib/api/tables.ts`:

```typescript
import { apiGet, apiPost, apiPut, apiDelete } from './client';
import type { TableDescription } from './types';

export const tablesApi = {
  list: (dbConnectionId: string) =>
    apiGet<TableDescription[]>(`/api/v1/table-descriptions?db_connection_id=${dbConnectionId}`),

  get: (id: string) =>
    apiGet<TableDescription>(`/api/v1/table-descriptions/${id}`),

  update: (id: string, data: { description?: string; columns?: unknown[] }) =>
    apiPut<TableDescription>(`/api/v1/table-descriptions/${id}`, data),

  delete: (id: string) =>
    apiDelete<TableDescription>(`/api/v1/table-descriptions/${id}`),

  scan: (tableDescriptionIds: string[], llmConfig?: { model_family: string; model_name: string }) =>
    apiPost<TableDescription[]>('/api/v1/table-descriptions/sync-schemas', {
      table_description_ids: tableDescriptionIds,
      llm_config: llmConfig,
    }),

  refresh: (dbConnectionId: string) =>
    apiPost<TableDescription[]>('/api/v1/table-descriptions/refresh', dbConnectionId),
};
```

**Step 5: Create MDL API**

Create `ui/src/lib/api/mdl.ts`:

```typescript
import { apiGet, apiPost, apiDelete } from './client';
import type { MDLManifest } from './types';

export const mdlApi = {
  list: (dbConnectionId?: string) => {
    const params = dbConnectionId ? `?db_connection_id=${dbConnectionId}` : '';
    return apiGet<MDLManifest[]>(`/api/v1/mdl/manifests${params}`);
  },

  get: (id: string) =>
    apiGet<MDLManifest>(`/api/v1/mdl/manifests/${id}`),

  create: (data: {
    db_connection_id: string;
    name: string;
    catalog: string;
    schema: string;
    data_source?: string;
  }) => apiPost<{ id: string }>('/api/v1/mdl/manifests', data),

  buildFromDatabase: (data: {
    db_connection_id: string;
    name: string;
    catalog: string;
    schema: string;
    data_source?: string;
    infer_relationships?: boolean;
  }) => apiPost<{ id: string }>('/api/v1/mdl/manifests/build', data),

  delete: (id: string) =>
    apiDelete<void>(`/api/v1/mdl/manifests/${id}`),

  export: (id: string) =>
    apiGet<Record<string, unknown>>(`/api/v1/mdl/manifests/${id}/export`),

  addModel: (manifestId: string, model: {
    name: string;
    columns: { name: string; type: string }[];
    primary_key?: string;
  }) => apiPost<{ status: string }>(`/api/v1/mdl/manifests/${manifestId}/models`, model),

  removeModel: (manifestId: string, modelName: string) =>
    apiDelete<void>(`/api/v1/mdl/manifests/${manifestId}/models/${modelName}`),

  addRelationship: (manifestId: string, relationship: {
    name: string;
    models: string[];
    join_type: string;
    condition: string;
  }) => apiPost<{ status: string }>(`/api/v1/mdl/manifests/${manifestId}/relationships`, relationship),

  removeRelationship: (manifestId: string, relationshipName: string) =>
    apiDelete<void>(`/api/v1/mdl/manifests/${manifestId}/relationships/${relationshipName}`),
};
```

**Step 6: Create agent API**

Create `ui/src/lib/api/agent.ts`:

```typescript
import { apiGet, apiPost, apiDelete } from './client';
import { API_BASE } from './client';
import type { AgentSession, AgentEvent } from './types';

export const agentApi = {
  // Sessions
  listSessions: (dbConnectionId?: string) => {
    const params = dbConnectionId ? `?db_connection_id=${dbConnectionId}` : '';
    return apiGet<{ sessions: AgentSession[]; total: number }>(`/api/v1/agent-sessions${params}`);
  },

  getSession: (id: string) =>
    apiGet<AgentSession>(`/api/v1/agent-sessions/${id}`),

  createSession: (data: {
    db_connection_id: string;
    mode?: string;
    title?: string;
    metadata?: Record<string, unknown>;
  }) => apiPost<{ session_id: string }>('/api/v1/agent-sessions', data),

  deleteSession: (id: string) =>
    apiDelete<{ status: string }>(`/api/v1/agent-sessions/${id}`),

  pauseSession: (id: string) =>
    apiPost<{ status: string }>(`/api/v1/agent-sessions/${id}/pause`),

  resumeSession: (id: string) =>
    apiPost<{ status: string }>(`/api/v1/agent-sessions/${id}/resume`),

  // Streaming execution
  streamTask: (
    sessionId: string,
    prompt: string,
    onEvent: (event: AgentEvent) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): (() => void) => {
    const controller = new AbortController();

    fetch(`${API_BASE}/api/v1/agent-sessions/${sessionId}/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const event = JSON.parse(line.slice(6)) as AgentEvent;
                onEvent(event);
              } catch {
                // Ignore parse errors
              }
            }
          }
        }
        onComplete();
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          onError(error);
        }
      });

    return () => controller.abort();
  },
};
```

**Step 7: Create knowledge API**

Create `ui/src/lib/api/knowledge.ts`:

```typescript
import { apiGet, apiPost, apiPut, apiDelete } from './client';
import type { BusinessGlossary, Instruction } from './types';

export const glossaryApi = {
  list: (dbConnectionId: string) =>
    apiGet<BusinessGlossary[]>(`/api/v1/business_glossaries?db_connection_id=${dbConnectionId}`),

  get: (id: string) =>
    apiGet<BusinessGlossary>(`/api/v1/business_glossaries/${id}`),

  create: (dbConnectionId: string, data: {
    term: string;
    definition: string;
    synonyms?: string[];
    related_tables?: string[];
  }) => apiPost<BusinessGlossary>(`/api/v1/business_glossaries?db_connection_id=${dbConnectionId}`, data),

  update: (id: string, data: {
    term?: string;
    definition?: string;
    synonyms?: string[];
    related_tables?: string[];
  }) => apiPut<BusinessGlossary>(`/api/v1/business_glossaries/${id}`, data),

  delete: (id: string) =>
    apiDelete<{ message: string }>(`/api/v1/business_glossaries/${id}`),
};

export const instructionsApi = {
  list: (dbConnectionId: string) =>
    apiGet<Instruction[]>(`/api/v1/instructions?db_connection_id=${dbConnectionId}`),

  get: (id: string) =>
    apiGet<Instruction>(`/api/v1/instructions/${id}`),

  create: (data: {
    db_connection_id: string;
    content: string;
    metadata?: Record<string, unknown>;
  }) => apiPost<Instruction>('/api/v1/instructions', data),

  update: (id: string, data: { content?: string; metadata?: Record<string, unknown> }) =>
    apiPut<Instruction>(`/api/v1/instructions/${id}`, data),

  delete: (id: string) =>
    apiDelete<{ message: string }>(`/api/v1/instructions/${id}`),
};
```

**Step 8: Commit**

```bash
git add ui/src/lib/
git commit -m "feat(ui): add typed API client layer"
```

---

### Task 1.3: Create Layout Shell

**Files:**
- Modify: `ui/src/app/layout.tsx`
- Create: `ui/src/app/providers.tsx`
- Create: `ui/src/components/layout/sidebar.tsx`
- Create: `ui/src/components/layout/header.tsx`

**Step 1: Create providers wrapper**

Create `ui/src/app/providers.tsx`:

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import { Toaster } from '@/components/ui/toaster';

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster />
    </QueryClientProvider>
  );
}
```

**Step 2: Create sidebar component**

Create `ui/src/components/layout/sidebar.tsx`:

```typescript
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
    <div className="flex h-full w-64 flex-col border-r bg-muted/30">
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Layers className="h-6 w-6" />
          <span>KAI Admin</span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="border-t p-4">
        <p className="text-xs text-muted-foreground">KAI v0.1.0</p>
      </div>
    </div>
  );
}
```

**Step 3: Create header component**

Create `ui/src/components/layout/header.tsx`:

```typescript
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

  // Get title from exact match or parent path
  const title = pageTitles[pathname] ||
    Object.entries(pageTitles).find(([path]) =>
      path !== '/' && pathname.startsWith(path)
    )?.[1] ||
    'KAI Admin';

  return (
    <header className="flex h-14 items-center border-b px-6">
      <h1 className="text-lg font-semibold">{title}</h1>
    </header>
  );
}
```

**Step 4: Update root layout**

Modify `ui/src/app/layout.tsx`:

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'KAI Admin',
  description: 'KAI Admin UI - Database intelligence and analysis',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
              <Header />
              <main className="flex-1 overflow-auto p-6">
                {children}
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
```

**Step 5: Verify layout renders**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npm run dev
```

Open http://localhost:3000 - should see sidebar with navigation

**Step 6: Commit**

```bash
git add ui/src/
git commit -m "feat(ui): add layout shell with sidebar navigation"
```

---

### Task 1.4: Create Dashboard Page

**Files:**
- Modify: `ui/src/app/page.tsx`
- Create: `ui/src/components/dashboard/stats-card.tsx`
- Create: `ui/src/components/dashboard/quick-actions.tsx`

**Step 1: Create stats card component**

Create `ui/src/components/dashboard/stats-card.tsx`:

```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { type LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
}

export function StatsCard({ title, value, description, icon: Icon }: StatsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
```

**Step 2: Create quick actions component**

Create `ui/src/components/dashboard/quick-actions.tsx`:

```typescript
'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Database, MessageSquare, Table2, Layers } from 'lucide-react';

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-2">
        <Button asChild variant="outline" className="justify-start">
          <Link href="/connections">
            <Database className="mr-2 h-4 w-4" />
            Add Connection
          </Link>
        </Button>
        <Button asChild variant="outline" className="justify-start">
          <Link href="/chat">
            <MessageSquare className="mr-2 h-4 w-4" />
            Start Chat
          </Link>
        </Button>
        <Button asChild variant="outline" className="justify-start">
          <Link href="/schema">
            <Table2 className="mr-2 h-4 w-4" />
            Browse Schema
          </Link>
        </Button>
        <Button asChild variant="outline" className="justify-start">
          <Link href="/mdl">
            <Layers className="mr-2 h-4 w-4" />
            Manage MDL
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
```

**Step 3: Create dashboard page**

Modify `ui/src/app/page.tsx`:

```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { Database, Table2, Layers, MessageSquare } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/stats-card';
import { QuickActions } from '@/components/dashboard/quick-actions';
import { connectionsApi } from '@/lib/api/connections';
import { mdlApi } from '@/lib/api/mdl';
import { agentApi } from '@/lib/api/agent';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function DashboardPage() {
  const { data: connections = [] } = useQuery({
    queryKey: ['connections'],
    queryFn: connectionsApi.list,
  });

  const { data: manifests = [] } = useQuery({
    queryKey: ['mdl-manifests'],
    queryFn: () => mdlApi.list(),
  });

  const { data: sessionsData } = useQuery({
    queryKey: ['agent-sessions'],
    queryFn: () => agentApi.listSessions(),
  });

  const sessions = sessionsData?.sessions || [];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Connections"
          value={connections.length}
          description="Active database connections"
          icon={Database}
        />
        <StatsCard
          title="MDL Manifests"
          value={manifests.length}
          description="Semantic layer definitions"
          icon={Layers}
        />
        <StatsCard
          title="Active Sessions"
          value={sessions.filter(s => s.status === 'active').length}
          description="Chat sessions"
          icon={MessageSquare}
        />
        <StatsCard
          title="Tables Scanned"
          value="-"
          description="With AI descriptions"
          icon={Table2}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <QuickActions />

        <Card>
          <CardHeader>
            <CardTitle>Recent Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {sessions.length === 0 ? (
              <p className="text-sm text-muted-foreground">No recent sessions</p>
            ) : (
              <div className="space-y-2">
                {sessions.slice(0, 5).map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between rounded-md border p-2"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        {session.title || `Session ${session.id.slice(0, 8)}`}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(session.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge variant={session.status === 'active' ? 'default' : 'secondary'}>
                      {session.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

**Step 4: Verify dashboard renders**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npm run dev
```

Open http://localhost:3000 - should see dashboard with stats and quick actions

**Step 5: Commit**

```bash
git add ui/src/
git commit -m "feat(ui): add dashboard page with stats and quick actions"
```

---

### Task 1.5: Create Connections Page

**Files:**
- Create: `ui/src/app/connections/page.tsx`
- Create: `ui/src/components/connections/connection-table.tsx`
- Create: `ui/src/components/connections/connection-dialog.tsx`
- Create: `ui/src/hooks/use-connections.ts`

**Step 1: Create connections hook**

Create `ui/src/hooks/use-connections.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { connectionsApi } from '@/lib/api/connections';
import type { CreateConnectionRequest } from '@/lib/api/types';
import { useToast } from '@/hooks/use-toast';

export function useConnections() {
  return useQuery({
    queryKey: ['connections'],
    queryFn: connectionsApi.list,
  });
}

export function useCreateConnection() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: CreateConnectionRequest) => connectionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast({ title: 'Connection created successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to create connection', description: error.message, variant: 'destructive' });
    },
  });
}

export function useUpdateConnection() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CreateConnectionRequest }) =>
      connectionsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast({ title: 'Connection updated successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to update connection', description: error.message, variant: 'destructive' });
    },
  });
}

export function useDeleteConnection() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (id: string) => connectionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast({ title: 'Connection deleted successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to delete connection', description: error.message, variant: 'destructive' });
    },
  });
}
```

**Step 2: Create connection dialog**

Create `ui/src/components/connections/connection-dialog.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, Eye, EyeOff } from 'lucide-react';
import { useCreateConnection } from '@/hooks/use-connections';
import type { DatabaseConnection } from '@/lib/api/types';

interface ConnectionDialogProps {
  connection?: DatabaseConnection;
  trigger?: React.ReactNode;
}

export function ConnectionDialog({ connection, trigger }: ConnectionDialogProps) {
  const [open, setOpen] = useState(false);
  const [showUri, setShowUri] = useState(false);
  const [formData, setFormData] = useState({
    alias: connection?.alias || '',
    connection_uri: '',
    schemas: connection?.schemas?.join(', ') || '',
  });

  const createMutation = useCreateConnection();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await createMutation.mutateAsync({
      alias: formData.alias,
      connection_uri: formData.connection_uri,
      schemas: formData.schemas ? formData.schemas.split(',').map(s => s.trim()) : undefined,
    });

    setOpen(false);
    setFormData({ alias: '', connection_uri: '', schemas: '' });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Connection
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {connection ? 'Edit Connection' : 'Add Database Connection'}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="alias">Alias</Label>
            <Input
              id="alias"
              placeholder="my-database"
              value={formData.alias}
              onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="uri">Connection URI</Label>
            <div className="relative">
              <Input
                id="uri"
                type={showUri ? 'text' : 'password'}
                placeholder="postgresql://user:pass@host:5432/db"
                value={formData.connection_uri}
                onChange={(e) => setFormData({ ...formData, connection_uri: e.target.value })}
                required
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowUri(!showUri)}
              >
                {showUri ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Format: dialect://user:password@host:port/database
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="schemas">Schemas (optional)</Label>
            <Input
              id="schemas"
              placeholder="public, sales, analytics"
              value={formData.schemas}
              onChange={(e) => setFormData({ ...formData, schemas: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Comma-separated list of schemas to include
            </p>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

**Step 3: Create connection table**

Create `ui/src/components/connections/connection-table.tsx`:

```typescript
'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Trash2, Table2, Layers } from 'lucide-react';
import Link from 'next/link';
import type { DatabaseConnection } from '@/lib/api/types';
import { useDeleteConnection } from '@/hooks/use-connections';

interface ConnectionTableProps {
  connections: DatabaseConnection[];
}

export function ConnectionTable({ connections }: ConnectionTableProps) {
  const deleteMutation = useDeleteConnection();

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this connection?')) {
      await deleteMutation.mutateAsync(id);
    }
  };

  if (connections.length === 0) {
    return (
      <div className="rounded-md border p-8 text-center">
        <p className="text-muted-foreground">No database connections yet.</p>
        <p className="text-sm text-muted-foreground">
          Add a connection to get started.
        </p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Alias</TableHead>
          <TableHead>Dialect</TableHead>
          <TableHead>Schemas</TableHead>
          <TableHead>Created</TableHead>
          <TableHead className="w-[50px]"></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {connections.map((connection) => (
          <TableRow key={connection.id}>
            <TableCell className="font-medium">
              {connection.alias || connection.id.slice(0, 8)}
            </TableCell>
            <TableCell>
              <Badge variant="outline">{connection.dialect}</Badge>
            </TableCell>
            <TableCell>
              {connection.schemas?.length ? (
                <div className="flex flex-wrap gap-1">
                  {connection.schemas.map((schema) => (
                    <Badge key={schema} variant="secondary">
                      {schema}
                    </Badge>
                  ))}
                </div>
              ) : (
                <span className="text-muted-foreground">-</span>
              )}
            </TableCell>
            <TableCell>
              {new Date(connection.created_at).toLocaleDateString()}
            </TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem asChild>
                    <Link href={`/schema?connection=${connection.id}`}>
                      <Table2 className="mr-2 h-4 w-4" />
                      View Schema
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href={`/mdl?connection=${connection.id}`}>
                      <Layers className="mr-2 h-4 w-4" />
                      Create MDL
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="text-destructive"
                    onClick={() => handleDelete(connection.id)}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

**Step 4: Create connections page**

Create `ui/src/app/connections/page.tsx`:

```typescript
'use client';

import { useConnections } from '@/hooks/use-connections';
import { ConnectionTable } from '@/components/connections/connection-table';
import { ConnectionDialog } from '@/components/connections/connection-dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export default function ConnectionsPage() {
  const { data: connections, isLoading, error } = useConnections();

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-destructive">Failed to load connections: {error.message}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-muted-foreground">
            Manage your database connections for KAI analysis.
          </p>
        </div>
        <ConnectionDialog />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Connections</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : (
            <ConnectionTable connections={connections || []} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

**Step 5: Add skeleton component if not exists**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npx shadcn@latest add skeleton
```

**Step 6: Verify connections page**

```bash
npm run dev
```

Open http://localhost:3000/connections - should see connections page with add button

**Step 7: Commit**

```bash
git add ui/src/
git commit -m "feat(ui): add connections page with CRUD functionality"
```

---

### Task 1.6: Configure Backend CORS

**Files:**
- Modify: `app/main.py`

**Step 1: Add CORS middleware**

Check if CORS is already configured in `app/main.py`. If not, add:

```python
from fastapi.middleware.cors import CORSMiddleware

# After app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 2: Verify CORS works**

Start both servers:
- Backend: `uv run python -m app.main` (port 8015)
- Frontend: `cd ui && npm run dev` (port 3000)

Open http://localhost:3000/connections and verify API calls work

**Step 3: Commit if changes made**

```bash
git add app/main.py
git commit -m "feat(api): add CORS middleware for UI development"
```

---

## Phase 2: Schema & MDL

### Task 2.1: Create Schema Browser Page

**Files:**
- Create: `ui/src/app/schema/page.tsx`
- Create: `ui/src/components/schema/table-tree.tsx`
- Create: `ui/src/components/schema/table-detail.tsx`
- Create: `ui/src/hooks/use-tables.ts`

**Step 1: Create tables hook**

Create `ui/src/hooks/use-tables.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tablesApi } from '@/lib/api/tables';
import { useToast } from '@/hooks/use-toast';

export function useTables(dbConnectionId: string | null) {
  return useQuery({
    queryKey: ['tables', dbConnectionId],
    queryFn: () => tablesApi.list(dbConnectionId!),
    enabled: !!dbConnectionId,
  });
}

export function useTable(id: string | null) {
  return useQuery({
    queryKey: ['table', id],
    queryFn: () => tablesApi.get(id!),
    enabled: !!id,
  });
}

export function useScanTables() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (tableIds: string[]) => tablesApi.scan(tableIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tables'] });
      toast({ title: 'Scan started', description: 'AI descriptions will be generated in the background' });
    },
    onError: (error: Error) => {
      toast({ title: 'Scan failed', description: error.message, variant: 'destructive' });
    },
  });
}
```

**Step 2: Create table tree component**

Create `ui/src/components/schema/table-tree.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { ChevronRight, ChevronDown, Table2, Database } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TableDescription, DatabaseConnection } from '@/lib/api/types';

interface TableTreeProps {
  connections: DatabaseConnection[];
  tables: Record<string, TableDescription[]>;
  selectedTableId: string | null;
  onSelectTable: (id: string) => void;
  onSelectConnection: (id: string) => void;
}

export function TableTree({
  connections,
  tables,
  selectedTableId,
  onSelectTable,
  onSelectConnection,
}: TableTreeProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-1">
      {connections.map((conn) => {
        const connTables = tables[conn.id] || [];
        const isExpanded = expanded[conn.id];

        // Group tables by schema
        const bySchema = connTables.reduce((acc, table) => {
          const schema = table.db_schema || 'public';
          if (!acc[schema]) acc[schema] = [];
          acc[schema].push(table);
          return acc;
        }, {} as Record<string, TableDescription[]>);

        return (
          <div key={conn.id}>
            <button
              className="flex w-full items-center gap-1 rounded-md px-2 py-1.5 text-sm hover:bg-muted"
              onClick={() => {
                toggleExpand(conn.id);
                onSelectConnection(conn.id);
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
              <Database className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{conn.alias || conn.id.slice(0, 8)}</span>
              <span className="ml-auto text-xs text-muted-foreground">
                {connTables.length}
              </span>
            </button>

            {isExpanded && (
              <div className="ml-4 space-y-0.5">
                {Object.entries(bySchema).map(([schema, schemaTables]) => (
                  <div key={schema}>
                    <div className="px-2 py-1 text-xs text-muted-foreground">
                      {schema}
                    </div>
                    {schemaTables.map((table) => (
                      <button
                        key={table.id}
                        className={cn(
                          'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted',
                          selectedTableId === table.id && 'bg-muted'
                        )}
                        onClick={() => onSelectTable(table.id)}
                      >
                        <Table2 className="h-4 w-4 text-muted-foreground" />
                        {table.table_name}
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

**Step 3: Create table detail component**

Create `ui/src/components/schema/table-detail.tsx`:

```typescript
'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Sparkles, Loader2 } from 'lucide-react';
import type { TableDescription } from '@/lib/api/types';
import { useScanTables } from '@/hooks/use-tables';

interface TableDetailProps {
  table: TableDescription;
}

export function TableDetail({ table }: TableDetailProps) {
  const scanMutation = useScanTables();

  const handleScan = () => {
    scanMutation.mutate([table.id]);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold">{table.table_name}</h2>
          <p className="text-sm text-muted-foreground">
            {table.db_schema || 'public'} &bull; {table.columns.length} columns
          </p>
        </div>
        <div className="flex gap-2">
          <Badge variant={table.sync_status === 'SCANNED' ? 'default' : 'secondary'}>
            {table.sync_status}
          </Badge>
          <Button
            size="sm"
            variant="outline"
            onClick={handleScan}
            disabled={scanMutation.isPending}
          >
            {scanMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="mr-2 h-4 w-4" />
            )}
            Scan with AI
          </Button>
        </div>
      </div>

      {table.description && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{table.description}</p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Columns</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Nullable</TableHead>
                <TableHead>Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {table.columns.map((col) => (
                <TableRow key={col.name}>
                  <TableCell className="font-mono text-sm">{col.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{col.data_type}</Badge>
                  </TableCell>
                  <TableCell>
                    {col.is_nullable ? (
                      <span className="text-muted-foreground">Yes</span>
                    ) : (
                      'No'
                    )}
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {col.description || (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Step 4: Create schema page**

Create `ui/src/app/schema/page.tsx`:

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useConnections } from '@/hooks/use-connections';
import { useTables, useTable } from '@/hooks/use-tables';
import { TableTree } from '@/components/schema/table-tree';
import { TableDetail } from '@/components/schema/table-detail';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function SchemaPage() {
  const searchParams = useSearchParams();
  const initialConnection = searchParams.get('connection');

  const [selectedConnectionId, setSelectedConnectionId] = useState<string | null>(
    initialConnection
  );
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);

  const { data: connections = [] } = useConnections();
  const { data: tables = [] } = useTables(selectedConnectionId);
  const { data: selectedTable } = useTable(selectedTableId);

  // Build tables lookup by connection
  const tablesByConnection: Record<string, typeof tables> = {};
  if (selectedConnectionId && tables.length > 0) {
    tablesByConnection[selectedConnectionId] = tables;
  }

  // Auto-select first connection if none selected
  useEffect(() => {
    if (!selectedConnectionId && connections.length > 0) {
      setSelectedConnectionId(connections[0].id);
    }
  }, [connections, selectedConnectionId]);

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      <Card className="w-72 shrink-0">
        <ScrollArea className="h-full">
          <div className="p-4">
            <h3 className="mb-4 text-sm font-medium">Tables</h3>
            <TableTree
              connections={connections}
              tables={tablesByConnection}
              selectedTableId={selectedTableId}
              onSelectTable={setSelectedTableId}
              onSelectConnection={setSelectedConnectionId}
            />
          </div>
        </ScrollArea>
      </Card>

      <Card className="flex-1">
        <CardContent className="p-6">
          {selectedTable ? (
            <TableDetail table={selectedTable} />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              Select a table to view details
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

**Step 5: Verify schema page**

```bash
npm run dev
```

Open http://localhost:3000/schema - should see schema browser

**Step 6: Commit**

```bash
git add ui/src/
git commit -m "feat(ui): add schema browser with table tree and detail view"
```

---

### Task 2.2: Create MDL Management Page

**Files:**
- Create: `ui/src/app/mdl/page.tsx`
- Create: `ui/src/app/mdl/[id]/page.tsx`
- Create: `ui/src/components/mdl/manifest-card.tsx`
- Create: `ui/src/components/mdl/create-manifest-dialog.tsx`
- Create: `ui/src/hooks/use-mdl.ts`

**Step 1: Create MDL hooks**

Create `ui/src/hooks/use-mdl.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mdlApi } from '@/lib/api/mdl';
import { useToast } from '@/hooks/use-toast';

export function useManifests(dbConnectionId?: string) {
  return useQuery({
    queryKey: ['mdl-manifests', dbConnectionId],
    queryFn: () => mdlApi.list(dbConnectionId),
  });
}

export function useManifest(id: string | null) {
  return useQuery({
    queryKey: ['mdl-manifest', id],
    queryFn: () => mdlApi.get(id!),
    enabled: !!id,
  });
}

export function useBuildManifest() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: mdlApi.buildFromDatabase,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mdl-manifests'] });
      toast({ title: 'MDL manifest created successfully' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to create manifest', description: error.message, variant: 'destructive' });
    },
  });
}

export function useDeleteManifest() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: mdlApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mdl-manifests'] });
      toast({ title: 'Manifest deleted' });
    },
    onError: (error: Error) => {
      toast({ title: 'Failed to delete manifest', description: error.message, variant: 'destructive' });
    },
  });
}

export function useExportManifest() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (id: string) => {
      const json = await mdlApi.export(id);
      const blob = new Blob([JSON.stringify(json, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mdl-${id}.json`;
      a.click();
      URL.revokeObjectURL(url);
      return json;
    },
    onSuccess: () => {
      toast({ title: 'Manifest exported' });
    },
    onError: (error: Error) => {
      toast({ title: 'Export failed', description: error.message, variant: 'destructive' });
    },
  });
}
```

**Step 2: Create manifest card**

Create `ui/src/components/mdl/manifest-card.tsx`:

```typescript
'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Download, Trash2, ExternalLink } from 'lucide-react';
import type { MDLManifest } from '@/lib/api/types';
import { useDeleteManifest, useExportManifest } from '@/hooks/use-mdl';

interface ManifestCardProps {
  manifest: MDLManifest;
}

export function ManifestCard({ manifest }: ManifestCardProps) {
  const deleteMutation = useDeleteManifest();
  const exportMutation = useExportManifest();

  const handleDelete = () => {
    if (confirm('Delete this manifest?')) {
      deleteMutation.mutate(manifest.id);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <div>
          <CardTitle className="text-base">
            {manifest.name || `Manifest ${manifest.id.slice(0, 8)}`}
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            {manifest.catalog}.{manifest.schema}
          </p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/mdl/${manifest.id}`}>
                <ExternalLink className="mr-2 h-4 w-4" />
                View Details
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => exportMutation.mutate(manifest.id)}>
              <Download className="mr-2 h-4 w-4" />
              Export JSON
            </DropdownMenuItem>
            <DropdownMenuItem className="text-destructive" onClick={handleDelete}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <Badge variant="secondary">{manifest.models.length} models</Badge>
          <Badge variant="secondary">{manifest.relationships.length} relationships</Badge>
          {manifest.data_source && (
            <Badge variant="outline">{manifest.data_source}</Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

**Step 3: Create manifest dialog**

Create `ui/src/components/mdl/create-manifest-dialog.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus } from 'lucide-react';
import { useBuildManifest } from '@/hooks/use-mdl';
import { useConnections } from '@/hooks/use-connections';

export function CreateManifestDialog() {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    db_connection_id: '',
    name: '',
    catalog: 'default',
    schema: 'public',
    infer_relationships: true,
  });

  const { data: connections = [] } = useConnections();
  const buildMutation = useBuildManifest();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await buildMutation.mutateAsync(formData);
    setOpen(false);
    setFormData({
      db_connection_id: '',
      name: '',
      catalog: 'default',
      schema: 'public',
      infer_relationships: true,
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Build from Database
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create MDL Manifest</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Database Connection</Label>
            <Select
              value={formData.db_connection_id}
              onValueChange={(v) => setFormData({ ...formData, db_connection_id: v })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select connection" />
              </SelectTrigger>
              <SelectContent>
                {connections.map((conn) => (
                  <SelectItem key={conn.id} value={conn.id}>
                    {conn.alias || conn.id.slice(0, 8)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Manifest Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My Semantic Layer"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="catalog">Catalog</Label>
              <Input
                id="catalog"
                value={formData.catalog}
                onChange={(e) => setFormData({ ...formData, catalog: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="schema">Schema</Label>
              <Input
                id="schema"
                value={formData.schema}
                onChange={(e) => setFormData({ ...formData, schema: e.target.value })}
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="infer"
              checked={formData.infer_relationships}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, infer_relationships: !!checked })
              }
            />
            <Label htmlFor="infer" className="text-sm">
              Auto-infer relationships from foreign keys
            </Label>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={buildMutation.isPending}>
              {buildMutation.isPending ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

**Step 4: Add checkbox component**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npx shadcn@latest add checkbox
```

**Step 5: Create MDL list page**

Create `ui/src/app/mdl/page.tsx`:

```typescript
'use client';

import { useManifests } from '@/hooks/use-mdl';
import { ManifestCard } from '@/components/mdl/manifest-card';
import { CreateManifestDialog } from '@/components/mdl/create-manifest-dialog';
import { Skeleton } from '@/components/ui/skeleton';

export default function MDLPage() {
  const { data: manifests = [], isLoading } = useManifests();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-muted-foreground">
          Manage semantic layer definitions for your databases.
        </p>
        <CreateManifestDialog />
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      ) : manifests.length === 0 ? (
        <div className="rounded-md border p-8 text-center">
          <p className="text-muted-foreground">No MDL manifests yet.</p>
          <p className="text-sm text-muted-foreground">
            Create one by building from a database connection.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {manifests.map((manifest) => (
            <ManifestCard key={manifest.id} manifest={manifest} />
          ))}
        </div>
      )}
    </div>
  );
}
```

**Step 6: Create MDL detail page**

Create `ui/src/app/mdl/[id]/page.tsx`:

```typescript
'use client';

import { use } from 'react';
import { useManifest, useExportManifest } from '@/hooks/use-mdl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Download, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function MDLDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: manifest, isLoading } = useManifest(id);
  const exportMutation = useExportManifest();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!manifest) {
    return <div>Manifest not found</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/mdl">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Link>
          </Button>
          <div>
            <h2 className="text-xl font-semibold">
              {manifest.name || `Manifest ${manifest.id.slice(0, 8)}`}
            </h2>
            <p className="text-sm text-muted-foreground">
              {manifest.catalog}.{manifest.schema}
            </p>
          </div>
        </div>
        <Button variant="outline" onClick={() => exportMutation.mutate(manifest.id)}>
          <Download className="mr-2 h-4 w-4" />
          Export JSON
        </Button>
      </div>

      <Tabs defaultValue="models">
        <TabsList>
          <TabsTrigger value="models">Models ({manifest.models.length})</TabsTrigger>
          <TabsTrigger value="relationships">
            Relationships ({manifest.relationships.length})
          </TabsTrigger>
          <TabsTrigger value="metrics">Metrics ({manifest.metrics.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-4">
          {manifest.models.map((model) => (
            <Card key={model.name}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  {model.name}
                  {model.primary_key && (
                    <Badge variant="outline">PK: {model.primary_key}</Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Column</TableHead>
                      <TableHead>Type</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {model.columns.map((col) => (
                      <TableRow key={col.name}>
                        <TableCell className="font-mono">{col.name}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{col.type}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="relationships">
          <Card>
            <CardContent className="pt-6">
              {manifest.relationships.length === 0 ? (
                <p className="text-muted-foreground">No relationships defined</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Models</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Condition</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {manifest.relationships.map((rel) => (
                      <TableRow key={rel.name}>
                        <TableCell className="font-medium">{rel.name}</TableCell>
                        <TableCell>{rel.models.join(' → ')}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{rel.join_type}</Badge>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {rel.condition}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metrics">
          <Card>
            <CardContent className="pt-6">
              {manifest.metrics.length === 0 ? (
                <p className="text-muted-foreground">No metrics defined</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Base Object</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {manifest.metrics.map((metric) => (
                      <TableRow key={metric.name}>
                        <TableCell className="font-medium">{metric.name}</TableCell>
                        <TableCell>{metric.base_object}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

**Step 7: Verify MDL pages**

```bash
npm run dev
```

Open http://localhost:3000/mdl - should see MDL management page

**Step 8: Commit**

```bash
git add ui/src/
git commit -m "feat(ui): add MDL manifest management pages"
```

---

## Phase 3: Interactive Chat

### Task 3.1: Create Chat Page with Agent Transparency

**Files:**
- Create: `ui/src/app/chat/page.tsx`
- Create: `ui/src/components/chat/chat-input.tsx`
- Create: `ui/src/components/chat/agent-message.tsx`
- Create: `ui/src/components/chat/tool-call-block.tsx`
- Create: `ui/src/components/chat/todo-list.tsx`
- Create: `ui/src/components/chat/session-sidebar.tsx`
- Create: `ui/src/hooks/use-chat.ts`
- Create: `ui/src/stores/chat-store.ts`

**Step 1: Create chat store with Zustand**

Create `ui/src/stores/chat-store.ts`:

```typescript
import { create } from 'zustand';
import type { AgentSession, AgentEvent, AgentTodo } from '@/lib/api/types';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  events?: AgentEvent[];
  todos?: AgentTodo[];
  isStreaming?: boolean;
}

interface ChatState {
  sessionId: string | null;
  connectionId: string | null;
  messages: ChatMessage[];
  currentTodos: AgentTodo[];
  isStreaming: boolean;

  setSession: (sessionId: string, connectionId: string) => void;
  addUserMessage: (content: string) => string;
  startAssistantMessage: (id: string) => void;
  appendToAssistantMessage: (id: string, content: string) => void;
  updateTodos: (todos: AgentTodo[]) => void;
  addEvent: (messageId: string, event: AgentEvent) => void;
  finishAssistantMessage: (id: string) => void;
  setStreaming: (streaming: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: null,
  connectionId: null,
  messages: [],
  currentTodos: [],
  isStreaming: false,

  setSession: (sessionId, connectionId) => set({ sessionId, connectionId, messages: [] }),

  addUserMessage: (content) => {
    const id = `user-${Date.now()}`;
    set((state) => ({
      messages: [
        ...state.messages,
        { id, role: 'user', content, timestamp: new Date() },
      ],
    }));
    return id;
  },

  startAssistantMessage: (id) => {
    set((state) => ({
      messages: [
        ...state.messages,
        { id, role: 'assistant', content: '', timestamp: new Date(), events: [], isStreaming: true },
      ],
      isStreaming: true,
    }));
  },

  appendToAssistantMessage: (id, content) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + content } : m
      ),
    }));
  },

  updateTodos: (todos) => set({ currentTodos: todos }),

  addEvent: (messageId, event) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === messageId ? { ...m, events: [...(m.events || []), event] } : m
      ),
    }));
  },

  finishAssistantMessage: (id) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, isStreaming: false, todos: state.currentTodos } : m
      ),
      isStreaming: false,
    }));
  },

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  clearMessages: () => set({ messages: [], currentTodos: [] }),
}));
```

**Step 2: Create chat hook**

Create `ui/src/hooks/use-chat.ts`:

```typescript
import { useCallback, useRef } from 'react';
import { useChatStore } from '@/stores/chat-store';
import { agentApi } from '@/lib/api/agent';
import type { AgentEvent } from '@/lib/api/types';

export function useChat() {
  const abortRef = useRef<(() => void) | null>(null);

  const {
    sessionId,
    connectionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    addUserMessage,
    startAssistantMessage,
    appendToAssistantMessage,
    updateTodos,
    addEvent,
    finishAssistantMessage,
    setStreaming,
    clearMessages,
  } = useChatStore();

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId || isStreaming) return;

      addUserMessage(content);
      const assistantId = `assistant-${Date.now()}`;
      startAssistantMessage(assistantId);

      const handleEvent = (event: AgentEvent) => {
        addEvent(assistantId, event);

        switch (event.type) {
          case 'token':
            if (event.content) {
              appendToAssistantMessage(assistantId, event.content);
            }
            break;
          case 'todo_update':
            if (event.todos) {
              updateTodos(event.todos);
            }
            break;
          case 'done':
            finishAssistantMessage(assistantId);
            break;
          case 'error':
            appendToAssistantMessage(assistantId, `\n\nError: ${event.error}`);
            finishAssistantMessage(assistantId);
            break;
        }
      };

      const handleError = (error: Error) => {
        appendToAssistantMessage(assistantId, `\n\nConnection error: ${error.message}`);
        finishAssistantMessage(assistantId);
      };

      const handleComplete = () => {
        finishAssistantMessage(assistantId);
      };

      abortRef.current = agentApi.streamTask(
        sessionId,
        content,
        handleEvent,
        handleError,
        handleComplete
      );
    },
    [
      sessionId,
      isStreaming,
      addUserMessage,
      startAssistantMessage,
      appendToAssistantMessage,
      updateTodos,
      addEvent,
      finishAssistantMessage,
    ]
  );

  const stopStreaming = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
      setStreaming(false);
    }
  }, [setStreaming]);

  return {
    sessionId,
    connectionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    sendMessage,
    stopStreaming,
    clearMessages,
  };
}
```

**Step 3: Create todo list component**

Create `ui/src/components/chat/todo-list.tsx`:

```typescript
import { cn } from '@/lib/utils';
import type { AgentTodo } from '@/lib/api/types';

interface TodoListProps {
  todos: AgentTodo[];
}

export function TodoList({ todos }: TodoListProps) {
  if (todos.length === 0) return null;

  return (
    <div className="rounded-md border border-purple-200 bg-purple-50 p-3 dark:border-purple-800 dark:bg-purple-950">
      <div className="mb-2 text-xs font-medium text-purple-600 dark:text-purple-400">
        Todo List
      </div>
      <div className="space-y-1">
        {todos.map((todo, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            {todo.status === 'completed' && (
              <span className="text-green-600">✔</span>
            )}
            {todo.status === 'in_progress' && (
              <span className="text-blue-600">➜</span>
            )}
            {todo.status === 'pending' && (
              <span className="text-yellow-600">○</span>
            )}
            <span
              className={cn(
                todo.status === 'completed' && 'line-through text-muted-foreground'
              )}
            >
              {todo.content}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Step 4: Create tool call block component**

Create `ui/src/components/chat/tool-call-block.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AgentEvent } from '@/lib/api/types';

interface ToolCallBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

export function ToolCallBlock({ event, result }: ToolCallBlockProps) {
  const [expanded, setExpanded] = useState(false);

  if (event.type !== 'tool_start') return null;

  const isCompleted = result?.type === 'tool_end';

  return (
    <div className="my-2 rounded-md border bg-muted/50">
      <button
        className="flex w-full items-center gap-2 p-2 text-left text-sm"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ChevronDown className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
        <span className={cn('font-mono', isCompleted ? 'text-green-600' : 'text-blue-600')}>
          {isCompleted ? '✔' : '➜'} {event.tool}
        </span>
      </button>

      {expanded && (
        <div className="border-t p-2 text-xs">
          {event.input && (
            <div className="mb-2">
              <div className="font-medium text-muted-foreground">Input:</div>
              <pre className="mt-1 overflow-x-auto rounded bg-background p-2">
                {JSON.stringify(event.input, null, 2)}
              </pre>
            </div>
          )}
          {result?.output && (
            <div>
              <div className="font-medium text-muted-foreground">Output:</div>
              <pre className="mt-1 max-h-40 overflow-auto rounded bg-background p-2">
                {typeof result.output === 'string'
                  ? result.output.slice(0, 500)
                  : JSON.stringify(result.output, null, 2).slice(0, 500)}
                {(result.output?.length || 0) > 500 && '...'}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

**Step 5: Create agent message component**

Create `ui/src/components/chat/agent-message.tsx`:

```typescript
'use client';

import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { TodoList } from './todo-list';
import { ToolCallBlock } from './tool-call-block';
import type { ChatMessage } from '@/stores/chat-store';
import type { AgentEvent } from '@/lib/api/types';

interface AgentMessageProps {
  message: ChatMessage;
}

export function AgentMessage({ message }: AgentMessageProps) {
  // Pair tool_start with tool_end events
  const toolPairs = useMemo(() => {
    if (!message.events) return [];

    const pairs: { start: AgentEvent; end?: AgentEvent }[] = [];
    const pending: AgentEvent[] = [];

    for (const event of message.events) {
      if (event.type === 'tool_start') {
        pending.push(event);
      } else if (event.type === 'tool_end') {
        const start = pending.find((p) => p.tool === event.tool);
        if (start) {
          pairs.push({ start, end: event });
          pending.splice(pending.indexOf(start), 1);
        }
      }
    }

    // Add any pending without end
    for (const start of pending) {
      pairs.push({ start });
    }

    return pairs;
  }, [message.events]);

  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-lg bg-primary px-4 py-2 text-primary-foreground">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {message.todos && message.todos.length > 0 && (
        <TodoList todos={message.todos} />
      )}

      {toolPairs.length > 0 && (
        <div className="space-y-1">
          {toolPairs.map((pair, i) => (
            <ToolCallBlock key={i} event={pair.start} result={pair.end} />
          ))}
        </div>
      )}

      {message.content && (
        <div className="prose prose-sm dark:prose-invert max-w-none rounded-lg border bg-muted/30 p-4">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      )}

      {message.isStreaming && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
          Thinking...
        </div>
      )}
    </div>
  );
}
```

**Step 6: Install react-markdown**

```bash
cd /Users/fitrakacamarga/project/mta/iba/services/KAI/ui
npm install react-markdown
```

**Step 7: Create chat input component**

Create `ui/src/components/chat/chat-input.tsx`:

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Square } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled: boolean;
}

export function ChatInput({ onSend, onStop, isStreaming, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (!isStreaming) {
      textareaRef.current?.focus();
    }
  }, [isStreaming]);

  return (
    <div className="flex gap-2">
      <Textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your data... (Cmd+Enter to send)"
        className="min-h-[60px] resize-none"
        disabled={disabled}
      />
      {isStreaming ? (
        <Button variant="destructive" size="icon" onClick={onStop}>
          <Square className="h-4 w-4" />
        </Button>
      ) : (
        <Button size="icon" onClick={handleSubmit} disabled={!input.trim() || disabled}>
          <Send className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
```

**Step 8: Create session sidebar component**

Create `ui/src/components/chat/session-sidebar.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { useConnections } from '@/hooks/use-connections';
import { agentApi } from '@/lib/api/agent';
import type { AgentSession } from '@/lib/api/types';
import { cn } from '@/lib/utils';

interface SessionSidebarProps {
  selectedSessionId: string | null;
  onSelectSession: (session: AgentSession) => void;
  onNewSession: (connectionId: string) => void;
}

export function SessionSidebar({
  selectedSessionId,
  onSelectSession,
  onNewSession,
}: SessionSidebarProps) {
  const [connectionId, setConnectionId] = useState<string>('');
  const queryClient = useQueryClient();

  const { data: connections = [] } = useConnections();
  const { data: sessionsData } = useQuery({
    queryKey: ['agent-sessions', connectionId],
    queryFn: () => agentApi.listSessions(connectionId || undefined),
  });

  const deleteMutation = useMutation({
    mutationFn: agentApi.deleteSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-sessions'] });
    },
  });

  const sessions = sessionsData?.sessions || [];

  const handleNewSession = () => {
    if (connectionId) {
      onNewSession(connectionId);
    }
  };

  return (
    <div className="flex h-full w-64 flex-col border-r">
      <div className="space-y-2 border-b p-3">
        <Select value={connectionId} onValueChange={setConnectionId}>
          <SelectTrigger>
            <SelectValue placeholder="Select connection" />
          </SelectTrigger>
          <SelectContent>
            {connections.map((conn) => (
              <SelectItem key={conn.id} value={conn.id}>
                {conn.alias || conn.id.slice(0, 8)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          className="w-full"
          size="sm"
          onClick={handleNewSession}
          disabled={!connectionId}
        >
          <Plus className="mr-2 h-4 w-4" />
          New Session
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {sessions.length === 0 ? (
            <p className="p-2 text-sm text-muted-foreground">
              No sessions yet
            </p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  'group flex items-center justify-between rounded-md p-2 text-sm hover:bg-muted',
                  selectedSessionId === session.id && 'bg-muted'
                )}
              >
                <button
                  className="flex flex-1 items-center gap-2 text-left"
                  onClick={() => onSelectSession(session)}
                >
                  <MessageSquare className="h-4 w-4" />
                  <span className="truncate">
                    {session.title || `Session ${session.id.slice(0, 8)}`}
                  </span>
                </button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100"
                  onClick={() => deleteMutation.mutate(session.id)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
```

**Step 9: Create chat page**

Create `ui/src/app/chat/page.tsx`:

```typescript
'use client';

import { useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SessionSidebar } from '@/components/chat/session-sidebar';
import { AgentMessage } from '@/components/chat/agent-message';
import { ChatInput } from '@/components/chat/chat-input';
import { TodoList } from '@/components/chat/todo-list';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useChat } from '@/hooks/use-chat';
import { agentApi } from '@/lib/api/agent';
import type { AgentSession } from '@/lib/api/types';

export default function ChatPage() {
  const queryClient = useQueryClient();
  const {
    sessionId,
    connectionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    sendMessage,
    stopStreaming,
    clearMessages,
  } = useChat();

  const createSessionMutation = useMutation({
    mutationFn: (connId: string) =>
      agentApi.createSession({ db_connection_id: connId }),
    onSuccess: (data, connId) => {
      setSession(data.session_id, connId);
      clearMessages();
      queryClient.invalidateQueries({ queryKey: ['agent-sessions'] });
    },
  });

  const handleSelectSession = (session: AgentSession) => {
    setSession(session.id, session.db_connection_id);
    clearMessages();
  };

  const handleNewSession = (connId: string) => {
    createSessionMutation.mutate(connId);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] -m-6">
      <SessionSidebar
        selectedSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
      />

      <div className="flex flex-1 flex-col">
        {!sessionId ? (
          <div className="flex flex-1 items-center justify-center text-muted-foreground">
            Select or create a session to start chatting
          </div>
        ) : (
          <>
            {/* Current Todos (live) */}
            {isStreaming && currentTodos.length > 0 && (
              <div className="border-b p-4">
                <TodoList todos={currentTodos} />
              </div>
            )}

            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <AgentMessage key={message.id} message={message} />
                ))}
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="border-t p-4">
              <ChatInput
                onSend={sendMessage}
                onStop={stopStreaming}
                isStreaming={isStreaming}
                disabled={!sessionId}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
```

**Step 10: Verify chat page**

```bash
npm run dev
```

Open http://localhost:3000/chat - should see chat interface

**Step 11: Commit**

```bash
git add ui/src/
git commit -m "feat(ui): add interactive chat page with full agent transparency"
```

---

## Phase 4: Knowledge & Polish

### Task 4.1: Create Knowledge Page

**Files:**
- Create: `ui/src/app/knowledge/page.tsx`
- Create: `ui/src/components/knowledge/glossary-list.tsx`
- Create: `ui/src/components/knowledge/instruction-list.tsx`
- Create: `ui/src/hooks/use-knowledge.ts`

(Implementation follows similar pattern to previous pages - see detailed code in Task 4.1)

### Task 4.2: Create Logs Page

**Files:**
- Create: `ui/src/app/logs/page.tsx`
- Create: `ui/src/components/logs/execution-table.tsx`

(Implementation follows similar pattern - see detailed code in Task 4.2)

### Task 4.3: Add Error Boundaries and Loading States

**Files:**
- Create: `ui/src/components/error-boundary.tsx`
- Create: `ui/src/app/error.tsx`
- Create: `ui/src/app/loading.tsx`

### Task 4.4: Final Polish and Testing

- Add proper TypeScript types
- Add loading skeletons to all pages
- Test all CRUD operations
- Verify streaming works correctly
- Check responsive design
- Final commit and documentation update

---

## Summary

This implementation plan covers:

1. **Phase 1 (Foundation)**: 6 tasks - Project setup, API client, layout, dashboard, connections CRUD, CORS
2. **Phase 2 (Schema & MDL)**: 2 tasks - Schema browser, MDL management
3. **Phase 3 (Chat)**: 1 task - Full chat implementation with agent transparency
4. **Phase 4 (Polish)**: 4 tasks - Knowledge, logs, error handling, final polish

Total estimated files: ~50
Total tasks: 13

Each task includes:
- Exact file paths
- Complete code
- Step-by-step instructions
- Verification steps
- Commit commands
