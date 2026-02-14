// Type definitions for API responses

export interface Connection {
  id: string;
  alias: string;
  dialect: string;
  created_at: string;
  database_type?: string;
  status?: string;
  schemas?: string[];
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

/**
 * All streaming event types including mission events.
 * Mission events are identified by checking for the 'version' field (v1)
 * or the type starting with 'mission_'.
 */
export type StreamingEvent = AgentEvent | MissionStreamEvent;

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

// ============================================================================
// Mission Event Contract (Agentic Context Platform)
// ============================================================================

/**
 * Mission stage types representing the lifecycle stages of an autonomous mission.
 * Includes 'failed' as a terminal stage for missions that cannot complete.
 * Matches backend: app/modules/autonomous_agent/models.py:MissionStage
 */
export type MissionStage = 'plan' | 'explore' | 'execute' | 'synthesize' | 'finalize' | 'failed';

/**
 * Mission event types for the mission stream.
 * Matches backend: app/modules/autonomous_agent/models.py:MissionStreamEvent
 */
export type MissionEventType = 'mission_stage' | 'mission_update' | 'mission_error' | 'mission_complete';

/**
 * Stage status for tracking mission stage progression.
 */
export type MissionStageStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

/**
 * Mission final status when complete.
 */
export type MissionFinalStatus = 'completed' | 'failed' | 'partial';

/**
 * Mission stream event - emitted during mission execution via SSE.
 * This is the primary event contract for mission lifecycle communication.
 * Matches backend: app/modules/autonomous_agent/models.py:MissionStreamEvent
 */
export interface MissionStreamEvent {
  /** Event envelope version for compatibility */
  version: 'v1';
  /** Event type discriminator */
  type: MissionEventType;
  /** Current mission stage */
  stage: MissionStage | null;
  /** Unique identifier for this mission run */
  mission_id: string;
  /** Session this mission belongs to */
  session_id: string;
  /** ISO 8601 timestamp of when this event was emitted */
  timestamp: string;
  /** Event-specific payload data */
  payload: Record<string, unknown>;

  // Event metadata
  /** Sequence number for ordering events within a mission */
  sequence_number: number;
  /** Confidence score (0-1) at this point in the mission */
  confidence: number | null;
  /** Status of the current stage */
  stage_status: MissionStageStatus | null;

  // For mission_stage events
  /** Unique identifier for this stage occurrence */
  stage_id: string | null;
  /** Summary of stage output */
  output_summary: string | null;
  /** List of artifact IDs produced in this stage */
  artifacts_produced: string[];

  // For mission_error events
  /** Error message */
  error: string | null;
  /** Number of retries attempted */
  retry_count: number;
  /** Whether this error is retryable */
  can_retry: boolean;

  // For mission_complete events
  /** Final mission status */
  final_status: MissionFinalStatus | null;
  /** Total execution time in milliseconds */
  execution_time_ms: number;
}

/**
 * Type guard to check if an event is a MissionStreamEvent.
 * Mission events have a 'version' field set to 'v1' and a type starting with 'mission_'.
 */
export function isMissionStreamEvent(event: StreamingEvent): event is MissionStreamEvent {
  return 'version' in event && event.version === 'v1' && event.type.startsWith('mission_');
}

/**
 * Type guard to check if an event is a mission stage event.
 */
export function isMissionStageEvent(event: StreamingEvent): event is MissionStreamEvent {
  return isMissionStreamEvent(event) && event.type === 'mission_stage';
}

/**
 * Type guard to check if an event is a mission complete event.
 */
export function isMissionCompleteEvent(event: StreamingEvent): event is MissionStreamEvent {
  return isMissionStreamEvent(event) && event.type === 'mission_complete';
}

/**
 * Type guard to check if an event is a mission error event.
 */
export function isMissionErrorEvent(event: StreamingEvent): event is MissionStreamEvent {
  return isMissionStreamEvent(event) && event.type === 'mission_error';
}

/**
 * Mission metadata including confidence scores and budget tracking.
 * Used for mission monitoring and quality gate enforcement.
 */
export interface MissionMetadata {
  /** Confidence score (0-1) indicating mission success likelihood */
  confidence?: number;
  /** Maximum runtime budget in seconds (default: 180) */
  max_runtime_seconds?: number;
  /** Maximum tool calls allowed (default: 40) */
  max_tool_calls?: number;
  /** Maximum consecutive SQL retry attempts (default: 3) */
  max_sql_retries?: number;
  /** Maximum identical failure retries (default: 2) */
  max_failure_retries?: number;
  /** Current tool call count */
  current_tool_calls?: number;
  /** Current SQL retry count */
  current_sql_retries?: number;
  /** Elapsed runtime in seconds */
  elapsed_seconds?: number;
}

/**
 * Mission stage payload for stage transition events.
 * Contains data specific to the stage being transitioned to.
 */
export interface MissionStagePayload {
  /** Previous stage (if any) */
  old_stage?: MissionStage | null;
  /** New stage */
  new_stage: MissionStage;
  /** Stage identifier (e.g., "plan_1") */
  stage_id: string;
  /** Confidence score for this stage (0-1) */
  confidence: number;
  /** Summary of stage output */
  output_summary?: string | null;
  /** List of artifact IDs produced */
  artifacts_produced: string[];
  /** Tool calls made so far */
  tool_calls_so_far: number;
  /** Runtime elapsed in seconds */
  runtime_seconds: number;
}

/**
 * Mission complete payload.
 */
export interface MissionCompletePayload {
  /** Final mission status */
  final_status: MissionFinalStatus;
  /** Overall confidence score */
  overall_confidence: number;
  /** List of completed stage IDs */
  stages_completed: string[];
  /** The stage where mission ended */
  final_stage?: MissionStage | null;
  /** Total tool calls made */
  tool_calls_total: number;
  /** Total runtime in seconds */
  runtime_seconds: number;
}

/**
 * Mission error payload.
 */
export interface MissionErrorPayload {
  /** Error message */
  error: string;
  /** Whether this error is retryable */
  can_retry: boolean;
}

/**
 * Mission artifact types representing reusable outputs from missions.
 */
export type MissionArtifactType = 'verified_sql' | 'notebook' | 'summary' | 'chart_config';

/**
 * A reusable artifact produced during a mission run.
 */
export interface MissionArtifact {
  id: string;
  type: MissionArtifactType;
  title: string;
  description?: string;
  content: string;
  provenance: {
    mission_id: string;
    session_id: string;
    stage: MissionStage;
    timestamp: string;
  };
  /** Whether this artifact has been verified/promoted to context catalog */
  is_verified?: boolean;
  /** Asset ID if promoted to context catalog */
  context_asset_id?: string;
}

// ============================================================================
// Context Asset Types (Agentic Context Platform)
// ============================================================================

/**
 * Lifecycle states for context assets.
 * Governance model: draft -> verified -> published -> deprecated
 */
export type ContextAssetLifecycle = 'draft' | 'verified' | 'published' | 'deprecated';

/**
 * Context asset types representing different kinds of reusable context.
 */
export type ContextAssetType = 'rule' | 'verified_sql' | 'mission_template' | 'benchmark_case' | 'correction';

/**
 * Context asset - first-class reusable artifact for analytics.
 */
export interface ContextAsset {
  id: string;
  db_connection_id: string;
  asset_type: ContextAssetType;
  lifecycle_state: ContextAssetLifecycle;
  owner: string;
  created_at: string;
  updated_at?: string;
  /** Current version number */
  version: number;
  /** Human-readable title */
  title?: string;
  /** Description of this asset */
  description?: string;
  /** Tags for discovery and organization */
  tags?: string[];
}

/**
 * Context asset version - immutable snapshot of an asset.
 */
export interface ContextAssetVersion {
  id: string;
  context_asset_id: string;
  version: number;
  payload: Record<string, unknown>;
  change_note?: string;
  created_at: string;
  created_by: string;
}

/**
 * Artifact promotion request - for promoting mission outputs to context assets.
 */
export interface ArtifactPromotionRequest {
  /** The artifact to promote */
  artifact_id: string;
  /** Target asset type */
  asset_type: ContextAssetType;
  /** Title for the promoted asset */
  title: string;
  /** Description of why this artifact is reusable */
  description?: string;
  /** Tags for discovery */
  tags?: string[];
  /** Change note explaining the promotion */
  change_note?: string;
}

/**
 * Artifact promotion response.
 */
export interface ArtifactPromotionResponse {
  /** ID of the created or updated context asset */
  asset_id: string;
  /** Version number of the new version */
  version: number;
  /** Previous version if updating an existing asset */
  previous_version?: number;
}

// ============================================================================
// Feedback Types (Agentic Context Platform)
// ============================================================================

/**
 * Feedback vote type.
 */
export type FeedbackVote = 'up' | 'down';

/**
 * Feedback event linked to a mission run and optionally to a context asset.
 */
export interface FeedbackEvent {
  id: string;
  mission_run_id: string;
  session_id: string;
  vote: FeedbackVote;
  explanation?: string;
  /** Optional: link to specific context asset this feedback applies to */
  context_asset_id?: string;
  /** Optional: link to specific mission step */
  mission_step_id?: string;
  created_at: string;
  created_by: string;
}

/**
 * Feedback submission request.
 */
export interface SubmitFeedbackRequest {
  mission_run_id: string;
  vote: FeedbackVote;
  explanation?: string;
  context_asset_id?: string;
  mission_step_id?: string;
}

// ============================================================================
// Benchmark Types (Agentic Context Platform)
// ============================================================================

/**
 * Benchmark case severity levels.
 */
export type BenchmarkSeverity = 'critical' | 'important' | 'informative';

/**
 * Expected behavior specification for a benchmark case.
 */
export interface BenchmarkExpectedBehavior {
  /** Description of expected SQL behavior patterns */
  sql_behavior?: string;
  /** Minimum fields that must be present in results */
  minimum_fields?: string[];
  /** Acceptance rules that must be satisfied */
  acceptance_rules?: string[];
}

/**
 * A benchmark test case for validating agent behavior.
 */
export interface BenchmarkCase {
  id: string;
  benchmark_suite_id: string;
  question: string;
  expected: BenchmarkExpectedBehavior;
  severity: BenchmarkSeverity;
  tags?: string[];
  created_at: string;
  updated_at?: string;
}

/**
 * Status of a benchmark run.
 */
export type BenchmarkRunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'partial';

/**
 * Result of a single benchmark case execution.
 */
export interface BenchmarkResult {
  id: string;
  benchmark_run_id: string;
  benchmark_case_id: string;
  passed: boolean;
  failure_reason?: string;
  execution_time_seconds?: number;
  created_at: string;
}

/**
 * A benchmark suite containing multiple test cases.
 */
export interface BenchmarkSuite {
  id: string;
  name: string;
  db_connection_id: string;
  owner: string;
  description?: string;
  tags?: string[];
  created_at: string;
  updated_at?: string;
}

/**
 * A benchmark run execution.
 */
export interface BenchmarkRun {
  id: string;
  benchmark_suite_id: string;
  status: BenchmarkRunStatus;
  pass_rate: number;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  created_at: string;
  completed_at?: string;
  created_by: string;
}
