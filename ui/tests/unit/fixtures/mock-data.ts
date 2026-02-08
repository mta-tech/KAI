/**
 * Mock data fixtures for unit tests
 */

import { vi } from 'vitest';
import { ReactElement } from 'react';

// =============================================================================
// API Response Fixtures
// =============================================================================

export const mockConnection = {
  id: 'conn-123',
  alias: 'test-database',
  dialect: 'postgresql',
  database_type: 'postgresql',
  created_at: '2024-01-01T00:00:00Z',
  status: 'active',
  schemas: ['public', 'analytics'],
};

export const mockConnections = [
  mockConnection,
  {
    id: 'conn-456',
    alias: 'analytics-db',
    dialect: 'postgresql',
    database_type: 'postgresql',
    created_at: '2024-01-02T00:00:00Z',
    status: 'active',
    schemas: ['public'],
  },
];

export const mockTable = {
  id: 'table-123',
  table_name: 'users',
  db_schema: 'public',
  db_connection_id: 'conn-123',
  description: 'User accounts table',
  sync_status: 'SCANNED' as const,
  columns: [
    {
      name: 'id',
      data_type: 'integer',
      is_nullable: false,
      description: 'Primary key',
    },
    {
      name: 'email',
      data_type: 'varchar(255)',
      is_nullable: false,
      description: 'User email address',
    },
    {
      name: 'created_at',
      data_type: 'timestamp',
      is_nullable: false,
      description: 'Creation timestamp',
    },
  ],
  created_at: '2024-01-01T00:00:00Z',
};

export const mockTables = [mockTable];

export const mockSession = {
  id: 'session-123',
  session_id: 'session-123',
  title: 'Test Session',
  created_at: '2024-01-01T00:00:00Z',
  status: 'active' as const,
  db_connection_id: 'conn-123',
  messages: [],
};

export const mockSessions = {
  sessions: [mockSession],
};

export const mockMessage = {
  id: 'msg-123',
  role: 'assistant' as const,
  content: 'Test response',
  timestamp: '2024-01-01T00:00:00Z',
};

export const mockInstruction = {
  id: 'instr-123',
  db_connection_id: 'conn-123',
  condition: 'When analyzing sales data',
  rules: 'Always show currency with 2 decimal places',
  is_default: false,
  metadata: {},
  created_at: '2024-01-01T00:00:00Z',
};

export const mockGlossary = {
  id: 'gloss-123',
  db_connection_id: 'conn-123',
  term: 'Active User',
  definition: 'A user who has logged in within the last 30 days',
  synonyms: ['Engaged User'],
  related_tables: ['users', 'sessions'],
  metadata: {},
  created_at: '2024-01-01T00:00:00Z',
};

export const mockMDLManifest = {
  id: 'mdl-123',
  name: 'sales_metrics',
  catalog: 'production',
  schema: 'public',
  data_source: 'conn-123',
  created_at: '2024-01-01T00:00:00Z',
  db_connection_id: 'conn-123',
  status: 'active',
  models: [],
  relationships: [],
  metrics: [],
};

// =============================================================================
// Error Fixtures
// =============================================================================

export const mockNetworkError = new Error('Network error');
export const mockValidationError = { message: 'Validation failed', code: 400 };
export const mockNotFoundError = { message: 'Resource not found', code: 404 };

// =============================================================================
// Component Props Fixtures
// =============================================================================

export const mockButtonProps = {
  children: 'Click me',
  onClick: vi.fn(),
};

export const mockInputProps = {
  placeholder: 'Enter text',
  value: '',
  onChange: vi.fn(),
};

export const mockDialogProps = {
  open: true,
  onOpenChange: vi.fn(),
  children: 'Dialog content' as unknown as ReactElement,
};

// =============================================================================
// Test Context Fixtures
// =============================================================================

export const mockQueryClient = {
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
  },
};

export const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  prefetch: vi.fn(),
  pathname: '/',
  query: {},
  asPath: '/',
};

export const mockSearchParams = new URLSearchParams();

// =============================================================================
// SSE Event Fixtures
// =============================================================================

export const mockChunkEvent = {
  type: 'chunk' as const,
  chunk_type: 'text' as const,
  content: 'Test response text',
};

export const mockToolStartEvent = {
  type: 'tool_start' as const,
  tool: 'sql_query',
  input: { query: 'SELECT * FROM users' },
};

export const mockToolEndEvent = {
  type: 'tool_end' as const,
  tool: 'sql_query',
  output: 'Query completed successfully',
};

export const mockTodoUpdateEvent = {
  type: 'todo_update' as const,
  todos: [
    {
      content: 'Analyze data',
      status: 'completed' as const,
    },
  ],
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Create a mock response object
 */
export function createMockResponse<T>(data: T, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
    text: async () => JSON.stringify(data),
  } as Response;
}

/**
 * Create a mock fetch function
 */
export function createMockFetch(responses: Record<string, any>) {
  return vi.fn(async (url: string) => {
    const key = Object.keys(responses).find(k => url.includes(k));
    if (key) {
      return createMockResponse(responses[key]);
    }
    return createMockResponse({ error: 'Not found' }, 404);
  });
}

/**
 * Create a delay promise for testing async operations
 */
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Create a mockAbortController
 */
export function createMockAbortController() {
  return {
    abort: vi.fn(),
    signal: {} as AbortSignal,
  };
}
