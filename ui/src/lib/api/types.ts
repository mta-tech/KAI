// Type definitions for API responses

export interface Connection {
  id: string;
  alias: string;
  created_at: string;
  database_type?: string;
  status?: string;
  schemas?: string[];
}

// Alias for backwards compatibility
export type DatabaseConnection = Connection;

export interface CreateConnectionRequest {
  alias: string;
  connection_uri: string;
  schemas?: string[];
}

export interface ColumnDescription {
  name: string;
  data_type: string;
  is_nullable: boolean;
  description?: string;
}

export interface TableDescription {
  id: string;
  table_name: string;
  db_schema?: string;
  db_connection_id: string;
  description?: string;
  columns: ColumnDescription[];
  sync_status: 'NOT_SCANNED' | 'SCANNING' | 'SCANNED' | 'DEPRECATED';
  created_at?: string;
}

export interface MDLManifest {
  id: string;
  name: string;
  created_at: string;
  db_connection_id: string;
  status?: string;
}

export interface AgentSession {
  id: string;
  session_id: string;
  title?: string;
  created_at: string;
  status: 'active' | 'completed' | 'failed';
  db_connection_id?: string;
}

export interface AgentMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface CreateSessionRequest {
  db_connection_id: string;
}

export interface SendMessageRequest {
  query: string;
  session_id: string;
}

export interface AgentResponse {
  response: string;
  session_id: string;
}

export interface SessionsListResponse {
  sessions: AgentSession[];
}

// Business Glossary types
export interface BusinessGlossary {
  id: string;
  db_connection_id: string;
  term: string;
  definition: string;
  synonyms?: string[];
  related_tables?: string[];
  metadata?: Record<string, unknown>;
  created_at: string;
}

// Instruction types
export interface Instruction {
  id: string;
  db_connection_id: string;
  content: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

// Agent event types for streaming
export interface AgentEvent {
  type: 'tool_start' | 'tool_end' | 'text' | 'todo_update';
  tool?: string;
  input?: Record<string, unknown>;
  output?: string | Record<string, unknown>;
  content?: string;
  todos?: AgentTodo[];
}

export interface AgentTodo {
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
}
