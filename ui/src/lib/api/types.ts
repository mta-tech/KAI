// Type definitions for API responses

export interface Connection {
  id: string;
  alias: string;
  dialect: string;
  created_at: string;
  database_type?: string;
  status?: string;
  schemas?: string[];
  connection_string?: string;
  connection_uri?: string;
}

/** @deprecated Use Connection instead */
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

export interface MDLColumn {
  name: string;
  type: string;
  is_calculated?: boolean;
  expression?: string;
  description?: string;
  properties?: Record<string, unknown>;
}

export interface MDLModel {
  name: string;
  ref_sql?: string;
  table_name?: string;
  columns: MDLColumn[];
  primary_key?: string;
  cached?: boolean;
  refresh_time?: string;
  properties?: Record<string, unknown>;
}

export interface MDLRelationship {
  name: string;
  models: string[];
  join_type: string;
  condition: string;
  properties?: Record<string, unknown>;
}

export interface MDLMetric {
  name: string;
  base_object: string;
  dimension: string[];
  measure: string[];
  time_grain?: string;
  cached?: boolean;
  refresh_time?: string;
  properties?: Record<string, unknown>;
}

export interface MDLManifest {
  id: string;
  name: string;
  catalog: string;
  schema: string;
  data_source?: string;
  created_at: string;
  db_connection_id: string;
  status?: string;
  models: MDLModel[];
  relationships: MDLRelationship[];
  metrics: MDLMetric[];
}

// Session message from backend
export interface SessionMessage {
  id: string;
  role: string;
  query: string;
  sql: string | null;
  results_summary: string | null;
  analysis: string | null;
  timestamp: string;
}

export interface AgentSession {
  id: string;
  session_id: string;
  title?: string;
  created_at: string;
  status: 'active' | 'completed' | 'failed';
  db_connection_id?: string;
  messages?: SessionMessage[];
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
  condition: string;
  rules: string;
  is_default: boolean;
  metadata?: Record<string, unknown>;
  created_at: string;
}

// Chunk types for structured SSE events
export type ChunkType = 'text' | 'sql' | 'summary' | 'insights' | 'chart_recommendations' | 'reasoning';

// Agent event types for streaming
// Note: Backend sends "chunk" events with type field in data, which gets spread into the event
// So the final type can be: text, sql, summary, insights, chart_recommendations, reasoning
export interface AgentEvent {
  type: 'tool_start' | 'tool_end' | 'text' | 'todo_update' | 'token' | 'done' | 'error' | 'status' | 'chunk' | ChunkType;
  tool?: string;
  input?: Record<string, unknown>;
  output?: string | Record<string, unknown>;
  content?: string;
  todos?: AgentTodo[];
  error?: string;
  // Structured content from SSE
  chunk_type?: ChunkType;
  step?: string;
  message?: string;
  session_id?: string;
  status?: string;
}

// Parsed message content structure
export interface ParsedContent {
  text: string;
  sql?: string;
  summary?: string;
  insights?: string[];
  chartRecommendations?: string[];
}

export interface AgentTodo {
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
}
