'use client';

import type { AgentEvent } from '@/lib/api/types';
import { SqlExecuteBlock } from './sql-execute-block';
import { ChartBlock } from './chart-block';
import { DataAnalysisBlock } from './data-analysis-block';
import { SearchBlock } from './search-block';
import { GenericBlock } from './generic-block';

export { useToolPairs } from './use-tool-pairs';
export type { ToolPair } from './use-tool-pairs';

interface ToolCallBlockProps {
  event: AgentEvent;
  result?: AgentEvent;
}

type ToolRenderer = React.ComponentType<ToolCallBlockProps>;

// Registry mapping tool names to specialized renderer components.
// Add new tool-specific renderers here. Falls back to GenericBlock.
const TOOL_REGISTRY: Record<string, ToolRenderer> = {
  sql_execute: SqlExecuteBlock,
  sql_query: SqlExecuteBlock,
  run_query: SqlExecuteBlock,
  create_chart: ChartBlock,
  generate_chart: ChartBlock,
  chart: ChartBlock,
  python_execute: DataAnalysisBlock,
  execute_python: DataAnalysisBlock,
  pandas_analysis: DataAnalysisBlock,
  data_analysis: DataAnalysisBlock,
  search: SearchBlock,
  search_context: SearchBlock,
  search_verified_queries: SearchBlock,
  search_metrics: SearchBlock,
  search_published_assets: SearchBlock,
  search_mdl_columns: SearchBlock,
};

export function ToolCallBlock({ event, result }: ToolCallBlockProps) {
  const toolName = event.tool ?? '';
  const Renderer = TOOL_REGISTRY[toolName] ?? GenericBlock;
  return <Renderer event={event} result={result} />;
}
