"""Autonomous agent service using LangChain DeepAgents."""
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import AsyncGenerator


# =============================================================================
# Tag-Based Streaming Parser
# =============================================================================

class StreamContext(Enum):
    """Current parsing context for tag-based streaming."""
    NONE = "none"             # Outside any tag
    THINKING = "thinking"     # Inside <thinking>
    ANSWER = "answer"         # Inside <answer>
    SUGGESTIONS = "suggestions"  # Inside <suggestions> (nested in answer)


@dataclass
class ParsedToken:
    """A parsed token with its semantic type."""
    content: str
    type: str  # "thinking", "answer", or "suggestions"


class TagStreamParser:
    """State machine for parsing XML-tagged streaming output.

    Parses LLM output with <thinking>...</thinking>, <answer>...</answer>,
    and nested <suggestions>...</suggestions> tags.

    Usage:
        parser = TagStreamParser()
        for token in stream:
            for parsed in parser.feed(token):
                emit(parsed.type, parsed.content)
        for parsed in parser.flush():
            emit(parsed.type, parsed.content)
    """

    def __init__(self):
        self.context = StreamContext.NONE
        self.buffer = ""
        self.in_answer = False  # Track if we're inside answer (for nested suggestions)

    def reset(self):
        """Reset parser state for a new stream."""
        self.context = StreamContext.NONE
        self.buffer = ""
        self.in_answer = False

    def feed(self, token: str) -> list[ParsedToken]:
        """Feed a token and return parsed tokens with types.

        Args:
            token: Raw token from LLM stream

        Returns:
            List of ParsedToken with content and type ("thinking", "answer", or "suggestions")
        """
        self.buffer += token
        results = []

        while True:
            if self.context == StreamContext.NONE:
                # Look for opening tags (thinking or answer)
                match = re.search(r'<(thinking|answer)>', self.buffer)
                if match:
                    # Emit any untagged content as "thinking" (fallback)
                    prefix = self.buffer[:match.start()].strip()
                    if prefix:
                        results.append(ParsedToken(prefix, "thinking"))

                    tag = match.group(1)
                    self.context = StreamContext(tag)
                    if tag == "answer":
                        self.in_answer = True
                    self.buffer = self.buffer[match.end():]
                else:
                    break  # Wait for more tokens

            elif self.context == StreamContext.ANSWER:
                # Inside <answer>, look for either </answer> or nested <suggestions>
                suggestions_match = re.search(r'<suggestions>', self.buffer)
                close_idx = self.buffer.find('</answer>')

                if suggestions_match and (close_idx == -1 or suggestions_match.start() < close_idx):
                    # Found <suggestions> before </answer>
                    content = self.buffer[:suggestions_match.start()]
                    if content.strip():
                        results.append(ParsedToken(content, "answer"))
                    self.buffer = self.buffer[suggestions_match.end():]
                    self.context = StreamContext.SUGGESTIONS
                elif close_idx != -1:
                    # Found </answer>
                    content = self.buffer[:close_idx]
                    if content.strip():
                        results.append(ParsedToken(content, "answer"))
                    self.buffer = self.buffer[close_idx + len('</answer>'):]
                    self.context = StreamContext.NONE
                    self.in_answer = False
                else:
                    # Keep buffer for partial tag detection (larger for suggestions tag)
                    safe_boundary = max(0, len(self.buffer) - 25)
                    if safe_boundary > 0:
                        results.append(ParsedToken(self.buffer[:safe_boundary], "answer"))
                        self.buffer = self.buffer[safe_boundary:]
                    break

            elif self.context == StreamContext.SUGGESTIONS:
                # Inside <suggestions>, look for </suggestions>
                close_tag = '</suggestions>'
                if close_tag in self.buffer:
                    idx = self.buffer.index(close_tag)
                    content = self.buffer[:idx]
                    if content.strip():
                        results.append(ParsedToken(content, "suggestions"))
                    self.buffer = self.buffer[idx + len(close_tag):]
                    # Go back to answer context (suggestions is nested in answer)
                    self.context = StreamContext.ANSWER
                else:
                    # Keep buffer for partial tag detection
                    safe_boundary = max(0, len(self.buffer) - 20)
                    if safe_boundary > 0:
                        results.append(ParsedToken(self.buffer[:safe_boundary], "suggestions"))
                        self.buffer = self.buffer[safe_boundary:]
                    break

            else:
                # Inside <thinking>
                close_tag = f'</{self.context.value}>'
                if close_tag in self.buffer:
                    idx = self.buffer.index(close_tag)
                    content = self.buffer[:idx]
                    if content:
                        results.append(ParsedToken(content, self.context.value))
                    self.buffer = self.buffer[idx + len(close_tag):]
                    self.context = StreamContext.NONE
                else:
                    # Emit buffered content (keep last 20 chars for partial tag detection)
                    safe_boundary = max(0, len(self.buffer) - 20)
                    if safe_boundary > 0:
                        results.append(ParsedToken(self.buffer[:safe_boundary], self.context.value))
                        self.buffer = self.buffer[safe_boundary:]
                    break

        return results

    def flush(self, preserve_partial_tags: bool = False) -> list[ParsedToken]:
        """Call at stream end to emit any remaining buffer.

        Args:
            preserve_partial_tags: If True, keep partial tag content (like '<' or '<answer')
                                   in buffer instead of emitting it

        Returns:
            List of remaining ParsedToken
        """
        results = []

        if preserve_partial_tags and self.context == StreamContext.NONE:
            # Check if buffer looks like start of a tag (partial tag)
            # Pattern: ends with '<' or '<' followed by partial tag name
            import re
            partial_tag_pattern = r'<(thinking|answer)?$'
            if re.search(partial_tag_pattern, self.buffer):
                # Keep the partial tag in buffer, don't flush it
                return results

        if self.buffer.strip():
            # Default to thinking if outside tags, otherwise use current context
            if self.context == StreamContext.NONE:
                emit_type = "thinking"
            else:
                emit_type = self.context.value
            results.append(ParsedToken(self.buffer, emit_type))
        self.buffer = ""
        self.context = StreamContext.NONE
        self.in_answer = False
        return results


# =============================================================================
# Autonomous Agent Service
# =============================================================================

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

from app.modules.autonomous_agent.models import (
    AgentTask,
    AgentResult,
    MissionStage,
    MissionState,
    MissionStreamEvent,
)
from app.modules.autonomous_agent.learning import (
    capture_with_correction_detection,
    get_memory_context_async,
)
from app.modules.memory.services import MemoryService
from app.modules.skill.services import SkillService
from app.modules.autonomous_agent.tools import (
    create_sql_query_tool,
    create_chart_tool,
    create_pandas_analysis_tool,
    create_python_execute_tool,
    create_report_tool,
    create_excel_tool,
    create_read_excel_tool,
    create_schema_context_tool,
    create_list_tables_tool,
    create_get_table_details_tool,
    create_get_filterable_columns_tool,
    create_search_tables_tool,
    create_get_business_glossary_tool,
    create_lookup_metric_tool,
    create_search_metrics_tool,
    create_get_instructions_tool,
    get_default_instructions,
    create_list_skills_tool,
    create_load_skill_tool,
    create_search_skills_tool,
    create_find_skills_for_question_tool,
    create_remember_tool,
    create_recall_tool,
    create_forget_tool,
    create_list_memories_tool,
    create_recall_for_question_tool,
    create_notebook_tool,
    create_list_notebooks_tool,
    create_get_notebook_tool,
    create_export_notebook_tool,
    create_lookup_verified_sql_tool,
    create_save_verified_sql_tool,
    create_list_verified_queries_tool,
    create_search_verified_queries_tool,
    create_delete_verified_sql_tool,
    create_get_mdl_manifest_tool,
    create_explore_mdl_model_tool,
    create_explore_mdl_relationships_tool,
    create_explore_mdl_metrics_tool,
    create_explore_mdl_views_tool,
    create_search_mdl_columns_tool,
    create_get_mdl_join_path_tool,
)
from app.data.db.storage import Storage
from app.modules.autonomous_agent.subagents import get_analysis_subagents
from app.modules.autonomous_agent.prompts import get_system_prompt
from app.modules.autonomous_agent.learning import (
    async_learning_context,
    get_learning_client,
)
from app.modules.database_connection.models import DatabaseConnection
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.model.chat_model import ChatModel

logger = logging.getLogger(__name__)


class AutonomousAgentService:
    """Service for running fully autonomous data analysis tasks.

    Uses LangChain DeepAgents with:
    - Built-in tools: write_todos, read_file, write_file, task, etc.
    - KAI tools: sql_query, analyze_data, python_execute
    - Subagents: query_planner, data_analyst, report_writer
    """

    def __init__(
        self,
        db_connection: DatabaseConnection,
        database: SQLDatabase,
        base_results_dir: str = "./agent_results",
        llm_config=None,
        checkpointer=None,
        storage: Storage = None,
        language: str | None = None,
    ):
        self.db_connection = db_connection
        self.database = database
        self.base_results_dir = base_results_dir
        self.llm_config = llm_config
        self.checkpointer = checkpointer
        # Initialize storage for schema tools
        if storage is None:
            from app.server.config import get_settings
            storage = Storage(get_settings())
        self.storage = storage
        # Initialize memory service for corrections and memory operations
        self.memory_service = MemoryService(storage)
        # Language setting (None = use from Settings)
        self._language = language
        # Track seen content to prevent duplicates from nested agent calls
        self._seen_content_hashes = set()
        # Track last streamed content for cumulative content detection
        self._last_streamed_content = ""
        # Track session conversation for memory saving at end
        self._session_messages: list[dict] = []
        self._last_user_prompt: str | None = None
        self._last_assistant_response: str | None = None
        # Buffer for accumulating response content before cleaning
        self._response_buffer = ""
        # Track if we've started emitting the final answer
        self._in_final_answer = False
        # Tag-based streaming parser for thinking/answer differentiation
        self._tag_parser = TagStreamParser()
        # Track consecutive empty SQL results to detect "no data found" loops
        self._consecutive_empty_sql_count = 0
        self._max_empty_sql_before_stop = 5  # Stop after 5 consecutive empty results
        self._no_data_stop_triggered = False

        # =====================================================================
        # Mission Tracking (Phase 2: Proactive Flow)
        # =====================================================================
        # Mission budget constraints for safety
        self._mission_max_runtime_seconds = 180
        self._mission_max_tool_calls = 40
        self._mission_max_sql_retries = 3
        self._mission_max_identical_failures = 2

        # Mission budget counters (reset per mission)
        self._mission_start_time: float | None = None
        self._mission_tool_call_count = 0
        self._mission_sql_retry_count = 0
        self._mission_identical_failure_count = 0

        # Current mission stage tracking
        self._mission_current_stage: str | None = None  # MissionStage value
        self._mission_stage_sequence: int = 0
        self._mission_stages_completed: list[str] = []

    def _get_session_results_dir(self, session_id: str) -> str:
        """Get results directory for a specific session.

        Args:
            session_id: The session ID

        Returns:
            Path to session-specific results directory
        """
        return os.path.join(
            self.base_results_dir,
            self.db_connection.id,
            session_id
        )

    def _get_llm(self):
        """Get LLM instance."""
        chat_model = ChatModel()
        if self.llm_config:
            return chat_model.get_model(
                database_connection=self.db_connection,
                temperature=0,
                model_family=self.llm_config.model_family,
                model_name=self.llm_config.model_name,
            )
        return chat_model.get_model(
            database_connection=self.db_connection,
            temperature=0,
        )

    def _build_tools(self, results_dir: str) -> list:
        """Build KAI-specific tools.

        Args:
            results_dir: Directory for output files (session-scoped)
        """
        tools = [
            # Schema/context tools - CALL THESE FIRST before writing SQL
            create_schema_context_tool(self.db_connection, self.storage),
            create_list_tables_tool(self.db_connection, self.storage),
            create_get_table_details_tool(self.db_connection, self.storage),
            create_get_filterable_columns_tool(self.db_connection, self.storage),
            create_search_tables_tool(self.db_connection, self.storage),
            # Business glossary tools - understand business terminology
            create_get_business_glossary_tool(self.db_connection, self.storage),
            create_lookup_metric_tool(self.db_connection, self.storage),
            create_search_metrics_tool(self.db_connection, self.storage),
            # Instruction tools - custom rules and guidelines
            create_get_instructions_tool(self.db_connection, self.storage),
            # Skill tools - load specialized analysis skills
            create_list_skills_tool(self.db_connection, self.storage),
            create_load_skill_tool(self.db_connection, self.storage),
            create_search_skills_tool(self.db_connection, self.storage),
            create_find_skills_for_question_tool(self.db_connection, self.storage),
            # Memory tools - long-term memory across conversations
            create_remember_tool(self.db_connection, self.storage),
            create_recall_tool(self.db_connection, self.storage),
            create_forget_tool(self.db_connection, self.storage),
            create_list_memories_tool(self.db_connection, self.storage),
            create_recall_for_question_tool(self.db_connection, self.storage),
            # SQL and analysis tools
            create_sql_query_tool(self.database),
            create_pandas_analysis_tool(),
            create_python_execute_tool(database=self.database),
            create_report_tool(output_dir=results_dir),
            create_excel_tool(output_dir=results_dir),
            create_read_excel_tool(base_dir=results_dir),
            # Visualization tools
            create_chart_tool(output_dir=results_dir),
            # Notebook tools
            create_notebook_tool(self.storage, output_dir=results_dir),
            create_list_notebooks_tool(self.storage),
            create_get_notebook_tool(self.storage),
            create_export_notebook_tool(self.storage, output_dir=results_dir),
            # Context store tools - lookup/save verified SQL queries
            create_lookup_verified_sql_tool(self.db_connection.id, self.storage),
            create_save_verified_sql_tool(self.db_connection.id, self.storage),
            create_list_verified_queries_tool(self.db_connection.id, self.storage),
            create_search_verified_queries_tool(self.db_connection.id, self.storage),
            create_delete_verified_sql_tool(self.db_connection.id, self.storage),
            # MDL manifest explorer tools - explore semantic layer
            create_get_mdl_manifest_tool(self.db_connection.id, self.storage),
            create_explore_mdl_model_tool(self.db_connection.id, self.storage),
            create_explore_mdl_relationships_tool(self.db_connection.id, self.storage),
            create_explore_mdl_metrics_tool(self.db_connection.id, self.storage),
            create_explore_mdl_views_tool(self.db_connection.id, self.storage),
            create_search_mdl_columns_tool(self.db_connection.id, self.storage),
            create_get_mdl_join_path_tool(self.db_connection.id, self.storage),
        ]

        # Load MCP tools if enabled
        mcp_tools = self._load_mcp_tools()
        if mcp_tools:
            tools.extend(mcp_tools)
            logger.info(f"Added {len(mcp_tools)} MCP tools to agent")

        return tools

    def _load_mcp_tools(self) -> list:
        """Load tools from configured MCP servers.

        Returns:
            List of LangChain-compatible tools from MCP servers.
        """
        from app.server.config import get_settings
        settings = get_settings()

        if not getattr(settings, "MCP_ENABLED", False):
            return []

        config_path = getattr(settings, "MCP_SERVERS_CONFIG", None)
        if not config_path:
            return []

        try:
            from app.modules.mcp import MCPToolManager, install_schema_warning_filter
            # Install global filter to suppress LangChain schema warnings
            # This prevents noisy warnings during agent execution
            install_schema_warning_filter()

            manager = MCPToolManager(config_path)
            tools = manager.get_tools_sync()
            if tools:
                logger.info(f"Loaded {len(tools)} tools from MCP servers")
            return tools
        except ImportError:
            logger.warning(
                "langchain-mcp-adapters not installed. "
                "Install with: pip install langchain-mcp-adapters"
            )
            return []
        except Exception as e:
            logger.warning(f"Failed to load MCP tools: {e}")
            return []

    def _make_backend_factory(self, results_dir: str):
        """Create backend factory with session-specific results directory.

        Args:
            results_dir: Directory for output files (session-scoped)

        Returns:
            Backend factory function for create_deep_agent
        """
        def backend_factory(runtime):
            return CompositeBackend(
                default=StateBackend(runtime),
                routes={
                    "/results/": FilesystemBackend(root_dir=results_dir, virtual_mode=True),
                },
            )
        return backend_factory

    def create_agent(self, mode: str = "full_autonomy", results_dir: str | None = None):
        """Create autonomous deep agent.

        Args:
            mode: Agent mode (full_autonomy, analysis, query, script)
            results_dir: Override results directory (for session-scoped)

        Returns:
            Compiled LangGraph agent
        """
        effective_results_dir = results_dir or self.base_results_dir

        # Build system prompt with custom instructions
        # Use instance language or fall back to Settings
        if self._language:
            language = self._language
        else:
            from app.server.config import get_settings
            settings = get_settings()
            language = getattr(settings, "AGENT_LANGUAGE", "id")

        base_prompt = get_system_prompt(
            mode=mode,
            dialect=self.db_connection.dialect,
            language=language,
        )

        # Append default instructions if any
        custom_instructions = get_default_instructions(
            self.db_connection.id, self.storage
        )
        system_prompt = base_prompt + custom_instructions

        return create_deep_agent(
            model=self._get_llm(),
            tools=self._build_tools(effective_results_dir),
            system_prompt=system_prompt,
            subagents=get_analysis_subagents(),
            backend=self._make_backend_factory(effective_results_dir),
            checkpointer=self.checkpointer,
        )

    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute task and return final result."""
        start_time = time.time()

        # Create session-specific results directory
        session_results_dir = self._get_session_results_dir(task.session_id)
        os.makedirs(session_results_dir, exist_ok=True)

        agent = self.create_agent(task.mode, results_dir=session_results_dir)

        config = {
            "configurable": {"thread_id": task.session_id},
            "recursion_limit": 100,
        }

        # Check for existing checkpoint (resume scenario)
        is_resume = False
        if self.checkpointer:
            try:
                existing_checkpoint = await self.checkpointer.aget(config)
                is_resume = existing_checkpoint is not None
                if is_resume:
                    logger.info(f"Resuming session {task.session_id} from checkpoint")
                else:
                    logger.info(f"Starting new session {task.session_id}")
            except Exception as e:
                logger.warning(f"Failed to check checkpoint: {e}")

        # Check if auto-learning is active
        auto_learning_active = get_learning_client() is not None

        # Load relevant memories and skills, prepend to user message
        context_parts = []

        # Load memory context - use Letta if auto-learning is enabled, else use legacy
        if auto_learning_active:
            # Manually retrieve Letta memory context (LangChain isn't intercepted by SDK)
            # This mimics the SDK's inject_memory_context() behavior
            letta_memory = await get_memory_context_async(
                self.db_connection.id,
                session_id=task.session_id,
            )
            if letta_memory:
                # Inject memory context at the beginning (like SDK's inject_memory_context)
                context_parts.append(letta_memory)
                logger.info(f"Injected Letta memory context ({len(letta_memory)} chars)")
                logger.debug(f"Memory context preview: {letta_memory[:200]}...")
            else:
                logger.info("No Letta memory context available (new session or empty)")
        else:
            # Use legacy memory system with Typesense
            memory_context, memory_stats = self._load_relevant_memories(task.prompt)
            if memory_context:
                context_parts.append(memory_context)
                logger.info(f"Loaded {memory_stats.get('total', 0)} relevant memories for task")

            # Also inject corrections from Typesense
            corrections_context = self.memory_service.get_corrections_for_prompt(
                db_connection_id=self.db_connection.id,
                query=task.prompt,
                session_id=task.session_id,
                limit=10,
            )
            if corrections_context:
                context_parts.append(corrections_context)
                logger.info("Injected Typesense corrections context")

        skill_context, skill_metadata = self._load_relevant_skills(task.prompt)
        if skill_context:
            context_parts.append(skill_context)
            skill_names = [s["name"] for s in skill_metadata]
            logger.info(f"Loaded relevant skills for task: {skill_names}")

        if context_parts:
            # Add clear instruction that memory is context, not the current request
            memory_instruction = (
                "## Background Context (FROM PAST SESSIONS - NOT THE CURRENT REQUEST)\n\n"
                "The following is memory/context from previous conversations. "
                "Use this as HINTS only - it is NOT the user's current question.\n\n"
                "IMPORTANT: If the user's current question is a simple greeting (halo, hello, hi), "
                "respond conversationally WITHOUT using this context.\n\n"
            )
            augmented_prompt = memory_instruction + "\n\n".join(context_parts) + f"\n\n## User's CURRENT Question (ANSWER THIS)\n{task.prompt}"
        else:
            augmented_prompt = task.prompt

        input_state = {
            "messages": [{"role": "user", "content": augmented_prompt}]
        }

        try:
            # Wrap with async learning context for memory injection (retrieval only)
            # Note: LangChain is not intercepted, so we manually capture after execution
            async with async_learning_context(self.db_connection.id, session_id=task.session_id):
                # Use ainvoke for proper async execution (non-blocking)
                result = await agent.ainvoke(input_state, config=config)

            final_message = result["messages"][-1]
            final_answer = (
                final_message.content
                if hasattr(final_message, "content")
                else str(final_message)
            )

            # Manually capture conversation for Letta learning
            # (LangChain isn't intercepted by agentic-learning SDK)
            # Uses correction detection to automatically learn from human feedback
            if auto_learning_active:
                await capture_with_correction_detection(
                    db_connection_id=self.db_connection.id,
                    session_id=task.session_id,
                    user_message=task.prompt,
                    assistant_message=final_answer,
                    previous_assistant_message=task.context.get("previous_answer") if task.context else None,
                )
            else:
                # Save session to memory using legacy method
                await self._save_session_to_memory(
                    task=task,
                    messages=result.get("messages", []),
                    final_answer=final_answer,
                )

                # Detect and store corrections using Typesense
                previous_answer = task.context.get("previous_answer") if task.context else None
                self.memory_service.detect_and_store_correction(
                    db_connection_id=self.db_connection.id,
                    user_message=task.prompt,
                    previous_answer=previous_answer,
                    session_id=task.session_id,
                )

            return AgentResult(
                task_id=task.id,
                status="completed",
                final_answer=final_answer,
                execution_time_ms=int((time.time() - start_time) * 1000),
            )
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return AgentResult(
                task_id=task.id,
                status="failed",
                final_answer="",
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

    async def stream_execute(
        self, task: AgentTask
    ) -> AsyncGenerator[dict, None]:
        """Execute task with streaming updates."""
        start_time = time.time()

        # Clear deduplication cache and buffers for new request
        self._seen_content_hashes.clear()
        self._last_streamed_content = ""
        self._response_buffer = ""
        self._in_final_answer = False
        # Reset empty SQL result tracking for new request
        self._consecutive_empty_sql_count = 0
        self._no_data_stop_triggered = False

        # Create session-specific results directory
        session_results_dir = self._get_session_results_dir(task.session_id)
        os.makedirs(session_results_dir, exist_ok=True)

        agent = self.create_agent(task.mode, results_dir=session_results_dir)

        config = {
            "configurable": {"thread_id": task.session_id},
            "recursion_limit": 100,
        }

        # Check for existing checkpoint (resume scenario)
        is_resume = False
        if self.checkpointer:
            try:
                existing_checkpoint = await self.checkpointer.aget(config)
                is_resume = existing_checkpoint is not None
                if is_resume:
                    logger.info(f"Resuming session {task.session_id} from checkpoint")
                    yield {
                        "type": "session_resumed",
                        "message": f"Resuming session {task.session_id}",
                        "session_id": task.session_id,
                    }
                else:
                    logger.info(f"Starting new session {task.session_id}")
            except Exception as e:
                logger.warning(f"Failed to check checkpoint: {e}")

        # Check if auto-learning is active
        auto_learning_active = get_learning_client() is not None

        # Load relevant memories and skills, prepend to user message
        context_parts = []

        # Load memory context - use Letta if auto-learning is enabled, else use legacy
        if auto_learning_active:
            # Manually retrieve Letta memory context (LangChain isn't intercepted by SDK)
            # This mimics the SDK's inject_memory_context() behavior
            letta_memory = await get_memory_context_async(
                self.db_connection.id,
                session_id=task.session_id,
            )
            if letta_memory:
                # Inject memory context at the beginning (like SDK's inject_memory_context)
                context_parts.append(letta_memory)
                logger.info(f"Injected Letta memory context ({len(letta_memory)} chars)")
                logger.debug(f"Memory context preview: {letta_memory[:200]}...")
                yield {
                    "type": "memory_loaded",
                    "message": f"Loaded memory from previous session ({len(letta_memory)} chars)",
                    "stats": {"auto_learning": True, "memory_injected": True, "chars": len(letta_memory)},
                }
            else:
                logger.info("No Letta memory context available (new session or empty)")
                yield {
                    "type": "memory_loaded",
                    "message": "New session (no previous memory)",
                    "stats": {"auto_learning": True, "memory_injected": False},
                }
        else:
            # Use legacy memory system with Typesense
            memory_context, memory_stats = self._load_relevant_memories(task.prompt)
            if memory_context:
                context_parts.append(memory_context)
                logger.info(f"Loaded {memory_stats.get('total', 0)} relevant memories for task")
                yield {
                    "type": "memory_loaded",
                    "message": f"Loaded {memory_stats.get('total', 0)} memories from previous sessions",
                    "stats": memory_stats,
                }

            # Also inject corrections from Typesense
            corrections_context = self.memory_service.get_corrections_for_prompt(
                db_connection_id=self.db_connection.id,
                query=task.prompt,
                session_id=task.session_id,
                limit=10,
            )
            if corrections_context:
                context_parts.append(corrections_context)
                logger.info("Injected Typesense corrections context")

        skill_context, skill_metadata = self._load_relevant_skills(task.prompt)
        if skill_context:
            context_parts.append(skill_context)
            skill_names = [s["name"] for s in skill_metadata]
            logger.info(f"Loaded relevant skills for task: {skill_names}")
            yield {
                "type": "skill_loaded",
                "message": f"Loaded {len(skill_metadata)} skill(s): {', '.join(skill_names)}",
                "skills": skill_metadata,
            }

        if context_parts:
            # Add clear instruction that memory is context, not the current request
            memory_instruction = (
                "## Background Context (FROM PAST SESSIONS - NOT THE CURRENT REQUEST)\n\n"
                "The following is memory/context from previous conversations. "
                "Use this as HINTS only - it is NOT the user's current question.\n\n"
                "IMPORTANT: If the user's current question is a simple greeting (halo, hello, hi), "
                "respond conversationally WITHOUT using this context.\n\n"
            )
            augmented_prompt = memory_instruction + "\n\n".join(context_parts) + f"\n\n## User's CURRENT Question (ANSWER THIS)\n{task.prompt}"
        else:
            augmented_prompt = task.prompt

        input_state = {
            "messages": [{"role": "user", "content": augmented_prompt}]
        }

        # Collect messages and final answer for memory saving
        collected_messages = [{"role": "user", "content": task.prompt}]
        final_answer_parts = []

        try:
            # Wrap with async learning context for automatic memory injection
            async with async_learning_context(self.db_connection.id, session_id=task.session_id):
                async for event in agent.astream_events(
                    input_state, config=config, version="v2"
                ):
                    processed = self._process_event(event)

                    # Handle both single event (dict) and multiple events (list) returns
                    if isinstance(processed, list):
                        for p in processed:
                            if p.get("type") == "token":
                                final_answer_parts.append(p.get("content", ""))
                            yield p
                    else:
                        # Collect AI responses for memory
                        if processed.get("type") == "token":
                            final_answer_parts.append(processed.get("content", ""))
                        yield processed

                    # Check if we should stop due to too many consecutive empty SQL results
                    if self._no_data_stop_triggered:
                        logger.warning(f"Stopping stream due to {self._consecutive_empty_sql_count} consecutive empty SQL results")
                        # Emit a helpful answer for the user
                        no_data_answer = (
                            "Maaf, saya tidak dapat menemukan data yang sesuai dengan permintaan Anda. "
                            f"Setelah mencoba {self._consecutive_empty_sql_count} query berbeda, "
                            "semua hasilnya kosong. Kemungkinan penyebab:\n\n"
                            "1. **Data tidak tersedia** - Data yang Anda cari mungkin tidak ada dalam database\n"
                            "2. **Filter terlalu spesifik** - Coba gunakan kriteria yang lebih luas\n"
                            "3. **Nama/istilah berbeda** - Coba gunakan istilah atau nama alternatif\n\n"
                            "**Saran**: Coba tanyakan data apa saja yang tersedia, misalnya:\n"
                            "- \"Tampilkan daftar provinsi yang tersedia\"\n"
                            "- \"Data apa saja yang ada dalam database?\""
                        )
                        yield {
                            "type": "answer",
                            "content": no_data_answer,
                        }
                        final_answer_parts.append(no_data_answer)
                        break  # Exit the streaming loop

            # Reconstruct final answer from streamed tokens
            final_answer = "".join(final_answer_parts)
            if final_answer:
                collected_messages.append({"role": "assistant", "content": final_answer})
            
            # Track conversation for session-end saving (Typesense backend)
            self._last_user_prompt = task.prompt
            self._last_assistant_response = final_answer
            self._session_messages.extend(collected_messages)

            yield {
                "type": "done",
                "execution_time_ms": int((time.time() - start_time) * 1000),
            }
        except Exception as e:
            yield {"type": "error", "error": str(e)}

    async def save_session(self, session_id: str) -> bool:
        """Save session memory at end of session.
        
        Called explicitly when user exits the interactive session.
        Saves conversation insights to Typesense for future reference.
        
        Args:
            session_id: The session ID to save
            
        Returns:
            True if save was successful
        """
        try:
            from app.server.config import get_settings
            settings = get_settings()
            memory_backend = getattr(settings, "MEMORY_BACKEND", "typesense").lower()
            
            # Check if using Letta backend (not Typesense)
            if memory_backend == "letta":
                # For Letta, the conversation is already captured via checkpointer
                logger.info(f"Session {session_id} using Letta backend - state persisted via checkpointer")
                return True
            
            # Typesense backend - save session conversation to memory
            if not self._session_messages:
                logger.info(f"Session {session_id} has no messages to save")
                return True
            
            logger.info(f"Saving session {session_id} with {len(self._session_messages)} messages to Typesense")
            
            # Create a dummy task for the save method
            from app.modules.autonomous_agent.models import AgentTask
            task = AgentTask(
                id=f"session_save_{session_id}",
                session_id=session_id,
                prompt="Session save",
                db_connection_id=self.db_connection.id,
            )
            
            # Get the final answer (last assistant message)
            final_answer = ""
            for msg in reversed(self._session_messages):
                if msg.get("role") == "assistant":
                    final_answer = msg.get("content", "")
                    break
            
            # Save session insights to memory
            await self._save_session_to_memory(
                task=task,
                messages=self._session_messages,
                final_answer=final_answer,
            )
            
            # Clear session tracking after save
            self._session_messages = []
            self._last_user_prompt = None
            self._last_assistant_response = None
            
            logger.info(f"Session {session_id} saved successfully")
            return True
                
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            return False

    # Compiled regex patterns (lazy initialization)
    _json_block_regex = None
    _reasoning_regex = None
    _answer_start_regex = None

    @classmethod
    def _get_json_block_regex(cls):
        """Compile JSON block detection regex on first use."""
        if cls._json_block_regex is None:
            import re
            # Match JSON blocks: ```json...``` or raw {...} or [...]
            cls._json_block_regex = re.compile(
                r'```json\s*\{[\s\S]*?\}[\s\S]*?```|'  # ```json {...} ```
                r'```\s*\{[\s\S]*?\}[\s\S]*?```|'      # ``` {...} ```
                r'\{\s*"[^"]+"\s*:\s*(?:\{|\[|"|\d|true|false|null)[\s\S]*?\}(?=\s|$|\n)|'  # Raw JSON object
                r'\[\s*\{[\s\S]*?\}\s*\]',  # JSON array
                re.MULTILINE
            )
        return cls._json_block_regex

    @classmethod
    def _get_reasoning_regex(cls):
        """Compile reasoning patterns regex on first use."""
        if cls._reasoning_regex is None:
            import re
            patterns = [
                # Indonesian reasoning patterns
                r"^(baik|oke|tentu),?\s*(saya akan|mari saya)",
                r"^saya akan (membantu|mencari|menggunakan|memanggil|memeriksa|menganalisis|mencari tahu|mencoba)",
                r"^berdasarkan (instruksi|data|hasil|informasi)",
                r"^pertama[,\s]+(saya|mari)",
                r"^langkah (pertama|selanjutnya|berikutnya)",
                r"^untuk menjawab (pertanyaan|ini)",
                r"^(saya perlu|kita perlu|perlu) (memanggil|menggunakan|memeriksa)",
                r"(kueri|query) (gagal|berhasil|sebelumnya|utama)",
                r"^mari (saya|kita) (coba|perbaiki|cek)",
                r"^(sekarang|selanjutnya),?\s*(saya akan|mari)",
                r"karena (kueri|kesalahan)",
                r"mencoba lagi",
                r"terjadi kesalahan",
                r"mungkin maksud",
                r"pesan kesalahan",
                r"kolom.{0,50}tidak (ada|ditemukan)",
                # English reasoning patterns
                r"^(okay|ok|alright),?\s*(let me|i will|i'll)",
                r"^i (will|need to|should|am going to) (use|call|check|analyze|query|find|try)",
                r"^based on (the|this|these) (instructions|data|results)",
                r"^first[,\s]+(let me|i will|i'll)",
                r"^let me (try|fix|check|call|use|find)",
                r"(query|sql).{0,30}(failed|error|incorrect)",
                r"there was an error",
                r"the error message",
                r"column.{0,30}(not found|doesn't exist)",
            ]
            cls._reasoning_regex = re.compile("|".join(patterns), re.IGNORECASE | re.MULTILINE)
        return cls._reasoning_regex

    @classmethod
    def _get_answer_start_regex(cls):
        """Compile answer start detection regex on first use."""
        if cls._answer_start_regex is None:
            import re
            # Patterns that indicate the start of actual answer content
            patterns = [
                r"^total\s+\w+",  # "Total koperasi..."
                r"^jumlah\s+\w+",  # "Jumlah koperasi..." (Indonesian for count/amount)
                r"^\d+[\.,]?\d*\s*(koperasi|unit|orang|buah|ribu|juta)",  # Numbers with units
                r"^(berdasarkan|dari)\s+(data|hasil|analisis)",  # "Based on data/results..."
                r"^\*\*saran\s+tindak\s+lanjut",  # "**Saran Tindak Lanjut"
                r"^(berikut|ini)\s+(adalah|hasil)",  # "Here are/These are..."
                r"^(jawaban|hasil|ringkasan)",  # "Answer/Result/Summary"
                r"^(terdapat|ada)\s+\d+",  # "Terdapat X..." / "Ada X..."
                r"^\w+\s+(adalah|berjumlah|sebanyak)\s+\d+",  # "X adalah Y" / "X berjumlah Y"
            ]
            cls._answer_start_regex = re.compile("|".join(patterns), re.IGNORECASE | re.MULTILINE)
        return cls._answer_start_regex

    def _clean_response_buffer(self, content: str) -> str:
        """Clean response buffer by removing JSON blocks and reasoning patterns.

        Args:
            content: Raw accumulated content from LLM

        Returns:
            Cleaned content suitable for user display
        """
        if not content:
            return ""

        import re

        # Step 1: Remove JSON code blocks (```json...```)
        content = re.sub(r'```json[\s\S]*?```', '', content)
        content = re.sub(r'```[\s\S]*?```', '', content)

        # Step 2: Remove raw JSON objects that look like tool outputs
        # Match patterns like { "success": true, ... } or { "todos": [...] }
        content = re.sub(
            r'\{\s*"(success|todos|database|instructions|columns|tables|error)"[\s\S]*?\}(?:\s*\})*',
            '',
            content
        )

        # Step 3: Remove reasoning sentences
        reasoning_regex = self._get_reasoning_regex()
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not reasoning_regex.search(stripped):
                cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)

        # Step 4: Clean up excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()

        return content

    def _is_final_answer_content(self, content: str) -> bool:
        """Check if content appears to be final answer (not reasoning).

        Args:
            content: Content to check

        Returns:
            True if this looks like final answer content
        """
        if not content or len(content) < 3:
            return False

        content_stripped = content.strip()

        # If it starts with JSON-like content, it's not final answer
        if content_stripped.startswith(('{', '[', '```')):
            return False

        # If it matches reasoning patterns, it's not final answer
        if self._get_reasoning_regex().search(content_stripped):
            return False

        # If it matches answer patterns or contains numbers/results, it's likely answer
        if self._get_answer_start_regex().search(content_stripped):
            return True

        # If it contains emoji (follow-up suggestions), it's answer
        if any(ord(c) > 0x1F300 for c in content_stripped):
            return True

        # If it's a short numeric response, it's answer
        if any(c.isdigit() for c in content_stripped[:20]):
            return True

        return False

    def _process_event(self, event: dict) -> dict | list:
        """Process LangGraph event for streaming.

        Uses tag-based parsing for token content:
        1. LLM output should be wrapped in <thinking>...</thinking> or <answer>...</answer> tags
        2. TagStreamParser tracks context and emits typed tokens
        3. Untagged content defaults to "thinking" for safety

        Returns:
            dict for single event, list of dicts for multiple events
        """
        event_type = event.get("event")

        if event_type == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk:
                content = chunk.content if hasattr(chunk, "content") else ""
                if content:
                    # Normalize content to string
                    if isinstance(content, list):
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and "text" in item:
                                text_parts.append(item["text"])
                            elif isinstance(item, str):
                                text_parts.append(item)
                            else:
                                text_parts.append(str(item))
                        content = "".join(text_parts)

                    if not content:
                        return {"type": "other", "event": "empty_content"}

                    # Handle cumulative content (get delta only)
                    if self._last_streamed_content and content.startswith(self._last_streamed_content):
                        delta = content[len(self._last_streamed_content):]
                        if not delta:
                            return {"type": "other", "event": "no_new_content"}
                        self._last_streamed_content = content
                        content = delta
                    else:
                        # Hash deduplication for exact duplicates
                        content_hash = hash(content)
                        if content_hash in self._seen_content_hashes:
                            return {"type": "other", "event": "duplicate_skipped"}
                        self._seen_content_hashes.add(content_hash)
                        self._last_streamed_content = content

                    # Feed token to tag parser
                    parsed_tokens = self._tag_parser.feed(content)

                    # DEBUG: Log parsing activity
                    import logging
                    _logger = logging.getLogger(__name__)
                    if '<' in content or '>' in content:
                        _logger.info(f"[TAG_PARSE] Content with tags: {content[:100]}")
                    if parsed_tokens:
                        _logger.info(f"[TAG_PARSE] Parsed {len(parsed_tokens)} tokens: {[(p.type, p.content[:30]) for p in parsed_tokens]}")

                    if parsed_tokens:
                        results = []
                        for parsed in parsed_tokens:
                            if parsed.type == "thinking":
                                results.append({
                                    "type": "thinking",
                                    "content": parsed.content
                                })
                            elif parsed.type == "answer":
                                results.append({
                                    "type": "token",  # User-visible answer
                                    "content": parsed.content
                                })
                            elif parsed.type == "suggestions":
                                results.append({
                                    "type": "suggestions",
                                    "content": parsed.content
                                })
                        return results if len(results) > 1 else results[0] if results else {"type": "other", "event": "buffering"}

                    # Parser buffering - no complete tokens yet
                    return {"type": "other", "event": "buffering"}

        elif event_type == "on_chat_model_end":
            # Stream ended - flush any remaining buffer content
            flushed = self._tag_parser.flush()
            if flushed:
                results = []
                for parsed in flushed:
                    if parsed.type == "thinking":
                        results.append({"type": "thinking", "content": parsed.content})
                    elif parsed.type == "answer":
                        results.append({"type": "token", "content": parsed.content})
                    elif parsed.type == "suggestions":
                        results.append({"type": "suggestions", "content": parsed.content})
                if results:
                    return results if len(results) > 1 else results[0]

            return {"type": "other", "event": "chat_model_end"}

        elif event_type == "on_tool_start":
            # Flush tag parser before tool call, but preserve partial tags
            # to avoid breaking tags that span across tool calls
            events = []
            flushed = self._tag_parser.flush(preserve_partial_tags=True)
            for parsed in flushed:
                if parsed.type == "answer":
                    events.append({"type": "token", "content": parsed.content})
                elif parsed.type == "suggestions":
                    events.append({"type": "suggestions", "content": parsed.content})
                else:
                    events.append({"type": "thinking", "content": parsed.content})

            self._last_streamed_content = ""
            self._in_final_answer = False

            # Check for write_todos to capture todo state
            if event.get("name") == "write_todos":
                events.append({
                    "type": "todo_update",
                    "todos": event.get("data", {}).get("input", {}).get("todos", [])
                })
            else:
                # Track SQL query for later use in tool_end
                if event.get("name") == "sql_query":
                    self._last_sql_query = event.get("data", {}).get("input", {}).get("sql", "")

                events.append({
                    "type": "tool_start",
                    "tool": event.get("name"),
                    "input": event.get("data", {}).get("input"),
                })

            return events if len(events) > 1 else events[0] if events else {"type": "other", "event": "tool_start"}

        elif event_type == "on_tool_end":
            # Reset tracking on tool boundaries
            self._last_streamed_content = ""

            # Capture tool output (not shown in answer, but for tracing)
            # Handle both raw string and ToolMessage object formats
            raw_output = event.get("data", {}).get("output", "")
            if hasattr(raw_output, "content"):
                # LangChain ToolMessage object - extract content
                output = str(raw_output.content)
            else:
                output = str(raw_output)
            tool_name = event.get("name")

            # DEBUG: Log tool_name to verify chart_tool detection
            logger.info(f"[TOOL_END] tool_name={tool_name}, output_preview={output[:200] if output else 'empty'}")

            events = [{
                "type": "tool_end",
                "tool": tool_name,
                "output": output,
            }]

            # Special handling for sql_query tool - emit structured visualization events
            if tool_name == "sql_query":
                try:
                    import json
                    result = json.loads(output)
                    row_count = result.get("row_count", 0)

                    # Track consecutive empty SQL results to detect "no data found" loops
                    if result.get("success") and row_count == 0:
                        self._consecutive_empty_sql_count += 1
                        logger.info(f"[SQL_QUERY] Empty result #{self._consecutive_empty_sql_count} (threshold: {self._max_empty_sql_before_stop})")

                        # Check if we should stop due to too many empty results
                        if self._consecutive_empty_sql_count >= self._max_empty_sql_before_stop:
                            self._no_data_stop_triggered = True
                            logger.warning(f"[SQL_QUERY] Stopping due to {self._consecutive_empty_sql_count} consecutive empty results")
                            events.append({
                                "type": "no_data_warning",
                                "message": f"Query tidak menemukan data yang sesuai setelah {self._consecutive_empty_sql_count} percobaan. Kemungkinan data yang diminta tidak ada dalam database.",
                                "consecutive_empty_count": self._consecutive_empty_sql_count,
                            })
                    elif result.get("success") and row_count > 0:
                        # Reset counter when data is found
                        self._consecutive_empty_sql_count = 0

                    if result.get("success") and result.get("data"):
                        # Emit sql_result event with structured data
                        events.append({
                            "type": "sql_result",
                            "sql": getattr(self, "_last_sql_query", ""),
                            "columns": result.get("columns", []),
                            "data": result.get("data", []),
                            "row_count": row_count,
                            "truncated": result.get("truncated", False),
                        })

                        # Auto-detect chart type and emit chart_config
                        chart_type = self._detect_chart_type(result)
                        if chart_type:
                            events.append({
                                "type": "chart_config",
                                "widget_type": chart_type,
                                "widget_data": result["data"],
                                "x_axis_key": result["columns"][0] if result["columns"] else None,
                                "y_axis_key": result["columns"][1] if len(result["columns"]) > 1 else None,
                            })
                except (json.JSONDecodeError, TypeError):
                    pass

            # Special handling for chart_tool - emit chart_config event for frontend rendering
            elif tool_name == "chart_tool":
                logger.info(f"[CHART_TOOL] Detected chart_tool, parsing output...")
                try:
                    import json
                    result = json.loads(output)
                    logger.info(f"[CHART_TOOL] Parsed result: success={result.get('success')}, render_type={result.get('render_type')}")
                    if result.get("success") and result.get("render_type") == "recharts":
                        # Emit chart_config event with frontend-compatible configuration
                        events.append({
                            "type": "chart_config",
                            "widget_type": result.get("chart_type", "bar"),
                            "widget_data": result.get("data", []),
                            "widget_title": result.get("title", ""),
                            "x_axis_key": result.get("x_axis_key"),
                            "y_axis_key": result.get("y_axis_key"),
                            "x_axis_label": result.get("x_axis_label"),
                            "y_axis_label": result.get("y_axis_label"),
                        })
                except (json.JSONDecodeError, TypeError):
                    pass

            return events if len(events) > 1 else events[0]

        return {"type": "other", "event": event_type}

    def _detect_chart_type(self, sql_result: dict) -> str | None:
        """Auto-detect appropriate chart type based on data shape.

        Args:
            sql_result: SQL query result with columns, data, and row_count

        Returns:
            Chart type string: 'bar', 'line', 'pie', 'kpi', 'table', or None
        """
        data = sql_result.get("data", [])
        columns = sql_result.get("columns", [])
        row_count = sql_result.get("row_count", 0)

        if not data or not columns:
            return None

        # Single row with 1-2 columns = KPI display
        if row_count == 1 and len(columns) <= 2:
            return "kpi"

        # Analyze column types from first row
        first_row = data[0] if data else {}
        numeric_cols = []
        text_cols = []

        for col in columns:
            val = first_row.get(col)
            if isinstance(val, (int, float)):
                numeric_cols.append(col)
            else:
                text_cols.append(col)

        # Check for date-like columns by name
        date_keywords = ["date", "time", "period", "month", "year", "tanggal", "bulan", "tahun"]
        has_date = any(
            any(kw in col.lower() for kw in date_keywords)
            for col in columns
        )

        # Time series: date column + numeric = line chart
        if has_date and numeric_cols:
            return "line"

        # Categorical: one text + one or more numeric = bar or pie
        if len(text_cols) == 1 and len(numeric_cols) >= 1:
            # Small number of categories = pie chart
            if row_count <= 6:
                return "pie"
            return "bar"

        # Multiple numeric columns = grouped bar
        if len(numeric_cols) >= 2:
            return "bar"

        # Many rows = table is more appropriate
        if row_count > 10:
            return "table"

        # Default to bar chart if we have numeric data
        return "bar" if numeric_cols else None

    async def _save_session_to_memory(
        self,
        task: AgentTask,
        messages: list,
        final_answer: str,
    ) -> None:
        """Extract insights from session and save to long-term memory.

        Analyzes the conversation to extract:
        - User preferences discovered
        - Business facts learned
        - Data insights found
        - Any corrections made

        Args:
            task: The completed task
            messages: All messages from the conversation
            final_answer: The final response to the user
        """
        try:
            memory_service = MemoryService(self.storage)

            # Build conversation summary for LLM analysis
            conversation_text = self._format_messages_for_summary(messages)

            # Use LLM to extract insights
            extraction_prompt = f"""Analyze this data analysis conversation and extract key insights to remember for future conversations.

CONVERSATION:
{conversation_text}

FINAL ANSWER:
{final_answer}

Extract and return a JSON object with the following structure. Only include categories that have actual insights discovered:

{{
    "user_preferences": [
        {{"key": "preference_name", "content": "description", "importance": 0.7}}
    ],
    "business_facts": [
        {{"key": "fact_name", "content": "description", "importance": 0.6}}
    ],
    "data_insights": [
        {{"key": "insight_name", "content": "description", "importance": 0.5}}
    ],
    "corrections": [
        {{"key": "correction_name", "content": "description", "importance": 0.8}}
    ],
    "session_summary": "Brief 1-2 sentence summary of what was accomplished"
}}

Guidelines:
- user_preferences: Date formats, reporting styles, preferred metrics, display preferences
- business_facts: Business rules, fiscal periods, product categories, customer segments discovered
- data_insights: Data patterns, anomalies, relationships between tables, data quality issues found
- corrections: Any mistakes you made that the user corrected
- importance: 0.3-0.5 (low), 0.5-0.7 (medium), 0.7-1.0 (high)
- Use snake_case for keys (e.g., "date_format_preference", "q4_revenue_rule")
- Only include genuinely useful insights, not obvious things
- If no insights in a category, omit it entirely

Return ONLY the JSON object, no other text."""

            llm = self._get_llm()
            response = llm.invoke(extraction_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Parse the JSON response
            try:
                # Clean up response - remove markdown code blocks if present
                clean_response = response_text.strip()
                if clean_response.startswith("```"):
                    clean_response = clean_response.split("```")[1]
                    if clean_response.startswith("json"):
                        clean_response = clean_response[4:]
                    clean_response = clean_response.strip()

                insights = json.loads(clean_response)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response as JSON: {response_text[:200]}")
                return

            # Store each insight as a memory
            timestamp = datetime.now().isoformat()

            for namespace in ["user_preferences", "business_facts", "data_insights", "corrections"]:
                if namespace in insights and insights[namespace]:
                    for item in insights[namespace]:
                        key = item.get("key", "").strip()
                        content = item.get("content", "").strip()
                        importance = float(item.get("importance", 0.5))

                        if key and content:
                            memory_service.remember(
                                db_connection_id=self.db_connection.id,
                                namespace=namespace,
                                key=key,
                                value={
                                    "content": content,
                                    "source_task_id": task.id,
                                    "source_question": task.prompt[:500],
                                    "discovered_at": timestamp,
                                },
                                importance=importance,
                            )
                            logger.info(f"Saved memory: {namespace}/{key}")

            # Store session summary
            if "session_summary" in insights and insights["session_summary"]:
                session_key = f"session_{task.id[:8]}_{timestamp[:10]}"
                memory_service.remember(
                    db_connection_id=self.db_connection.id,
                    namespace="session_summaries",
                    key=session_key,
                    value={
                        "content": insights["session_summary"],
                        "task_id": task.id,
                        "user_question": task.prompt[:500],
                        "timestamp": timestamp,
                    },
                    importance=0.4,
                )
                logger.info(f"Saved session summary: {session_key}")

        except Exception as e:
            logger.warning(f"Failed to save session to memory: {e}")

    def _load_relevant_memories(self, question: str) -> tuple[str | None, dict]:
        """Load relevant memories for a question at the start of execution.

        Args:
            question: The user's question/prompt

        Returns:
            Tuple of (formatted memory context string, memory stats dict)
        """
        try:
            memory_service = MemoryService(self.storage)
            results = memory_service.recall(
                db_connection_id=self.db_connection.id,
                query=question,
                namespace=None,  # Search all namespaces
                limit=10,
            )

            if not results:
                return None, {}

            # Group by namespace
            by_namespace: dict = {}
            for r in results:
                ns = r.memory.namespace
                if ns not in by_namespace:
                    by_namespace[ns] = []

                content = r.memory.value.get("content", str(r.memory.value))
                age = self._calculate_memory_age(r.memory.created_at)
                by_namespace[ns].append(f"- [{r.memory.key}] {content} ({age})")

            # Format as context
            sections = []
            namespace_labels = {
                "user_preferences": "User Preferences",
                "business_facts": "Business Facts",
                "data_insights": "Data Insights",
                "corrections": "Previous Corrections",
                "session_summaries": "Recent Sessions",
            }

            # Collect stats for reporting
            memory_stats = {
                "total": len(results),
                "by_namespace": {ns: len(items) for ns, items in by_namespace.items()},
            }

            for ns, items in by_namespace.items():
                label = namespace_labels.get(ns, ns.replace("_", " ").title())
                sections.append(f"### {label}\n" + "\n".join(items))

            if sections:
                context = (
                    "## Context from Previous Sessions (HINTS ONLY - NOT DATA)\n\n"
                    + "\n\n".join(sections)
                    + "\n\n---\n\n"
                    "**IMPORTANT**: These memories are CONTEXT HINTS, not actual data! "
                    "You MUST still query the database to answer data questions. "
                    "Never say 'I don't have data' based on memories alone - always run SQL queries first."
                )
                return context, memory_stats

            return None, {}

        except Exception as e:
            logger.warning(f"Failed to load memories: {e}")
            return None, {}

    def _calculate_memory_age(self, created_at: str) -> str:
        """Calculate human-readable age of a memory."""
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now = datetime.now()
            if created.tzinfo:
                now = datetime.now(created.tzinfo)
            delta = now - created

            if delta.days > 365:
                years = delta.days // 365
                return f"{years}y ago"
            elif delta.days > 30:
                months = delta.days // 30
                return f"{months}mo ago"
            elif delta.days > 0:
                return f"{delta.days}d ago"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
            else:
                return "recent"
        except Exception:
            return "unknown"

    def _load_relevant_skills(self, question: str) -> tuple[str | None, list[dict]]:
        """Load relevant skills for a question at the start of execution.

        Args:
            question: The user's question/prompt

        Returns:
            Tuple of (formatted skill context string, list of skill metadata dicts)
        """
        try:
            skill_service = SkillService(self.storage)
            skills = skill_service.find_relevant_skills(
                db_connection_id=self.db_connection.id,
                query=question,
                limit=3,
            )

            if not skills:
                return None, []

            # Collect skill metadata for reporting
            skill_metadata = [
                {
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "category": skill.category or "General",
                }
                for skill in skills
            ]

            # Format skills with their full content
            skill_sections = []
            for skill in skills:
                skill_sections.append(
                    f"### Skill: {skill.name}\n"
                    f"**Category:** {skill.category or 'General'}\n"
                    f"**Description:** {skill.description}\n\n"
                    f"{skill.content}"
                )

            if skill_sections:
                context = (
                    "## Relevant Skills for This Analysis\n\n"
                    "The following skills contain guidelines and approaches for this type of analysis. "
                    "Follow these instructions where applicable.\n\n"
                    + "\n\n---\n\n".join(skill_sections)
                )
                return context, skill_metadata

            return None, []

        except Exception as e:
            logger.warning(f"Failed to load skills: {e}")
            return None, []

    def _format_messages_for_summary(self, messages: list) -> str:
        """Format conversation messages for LLM summarization."""
        formatted = []
        for msg in messages[-20:]:  # Limit to last 20 messages
            if hasattr(msg, 'type'):
                role = msg.type
            elif hasattr(msg, 'role'):
                role = msg.role
            elif isinstance(msg, dict):
                role = msg.get('role', msg.get('type', 'unknown'))
            else:
                role = 'unknown'

            if hasattr(msg, 'content'):
                content = msg.content
            elif isinstance(msg, dict):
                content = msg.get('content', str(msg))
            else:
                content = str(msg)

            # Truncate very long content
            if len(content) > 1000:
                content = content[:1000] + "..."

            formatted.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted)

    # =====================================================================
    # Mission Stage & Budget Helpers (Phase 2.2a/2.2b)
    # =====================================================================

    def _initialize_mission_tracking(self) -> None:
        """Initialize mission budget counters and stage tracking."""
        self._mission_start_time = time.time()
        self._mission_tool_call_count = 0
        self._mission_sql_retry_count = 0
        self._mission_identical_failure_count = 0
        self._mission_current_stage = None
        self._mission_stage_sequence = 0
        self._mission_stages_completed = []

    def _check_mission_budget(self) -> tuple[bool, str | None]:
        """Check if mission has exceeded any budget constraints.

        Returns:
            (can_continue: bool, error_message: str | None)
        """
        # Check runtime
        if self._mission_start_time:
            elapsed = time.time() - self._mission_start_time
            if elapsed > self._mission_max_runtime_seconds:
                return False, f"Mission exceeded maximum runtime of {self._mission_max_runtime_seconds}s (elapsed: {elapsed:.1f}s)"

        # Check tool calls
        if self._mission_tool_call_count >= self._mission_max_tool_calls:
            return False, f"Mission exceeded maximum tool calls ({self._mission_max_tool_calls})"

        # Check SQL retries
        if self._mission_sql_retry_count >= self._mission_max_sql_retries:
            return False, f"Mission exceeded maximum SQL retries ({self._mission_max_sql_retries})"

        # Check identical failures
        if self._mission_identical_failure_count >= self._mission_max_identical_failures:
            return False, f"Mission exceeded maximum identical failures ({self._mission_max_identical_failures})"

        return True, None

    def _transition_mission_stage(
        self,
        new_stage: str,
        confidence: float = 0.0,
        output_summary: str | None = None,
        artifacts: list[str] | None = None,
    ) -> dict:
        """Transition to a new mission stage and emit stage event.

        Args:
            new_stage: The new MissionStage value (plan, explore, execute, synthesize, finalize, failed)
            confidence: Stage-level confidence (0-1)
            output_summary: Optional summary of stage output
            artifacts: Optional list of artifact IDs produced

        Returns:
            Stage event dict for yielding
        """
        from app.modules.autonomous_agent.models import MissionStage

        old_stage = self._mission_current_stage
        self._mission_current_stage = new_stage
        self._mission_stage_sequence += 1

        if old_stage and old_stage != new_stage:
            self._mission_stages_completed.append(old_stage)

        # Emit stage transition event
        return {
            "version": "v1",
            "type": "mission_stage",
            "stage": new_stage,
            "mission_id": "",  # Will be set by caller
            "session_id": "",  # Will be set by caller
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "old_stage": old_stage,
                "new_stage": new_stage,
                "stage_id": f"{new_stage}_{self._mission_stage_sequence}",
                "confidence": confidence,
                "output_summary": output_summary,
                "artifacts_produced": artifacts or [],
                "tool_calls_so_far": self._mission_tool_call_count,
                "runtime_seconds": time.time() - (self._mission_start_time or time.time()),
            },
            "sequence_number": self._mission_stage_sequence,
            "confidence": confidence,
            "stage_id": f"{new_stage}_{self._mission_stage_sequence}",
            "output_summary": output_summary,
            "artifacts_produced": artifacts or [],
        }

    def _emit_mission_complete_event(
        self,
        mission_id: str,
        session_id: str,
        final_status: str,
        overall_confidence: float,
        execution_time_ms: int,
        stages_completed: list[str],
        final_stage: str | None = None,
    ) -> dict:
        """Emit mission complete event.

        Args:
            mission_id: Mission run ID
            session_id: Session ID
            final_status: Final status (completed, failed, partial)
            overall_confidence: Overall mission confidence (0-1)
            execution_time_ms: Total execution time in milliseconds
            stages_completed: List of completed stage IDs
            final_stage: The stage where mission ended

        Returns:
            Mission complete event dict
        """
        return {
            "version": "v1",
            "type": "mission_complete",
            "stage": final_stage,
            "mission_id": mission_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "final_status": final_status,
                "overall_confidence": overall_confidence,
                "stages_completed": stages_completed,
                "final_stage": final_stage,
                "tool_calls_total": self._mission_tool_call_count,
                "runtime_seconds": execution_time_ms / 1000,
            },
            "sequence_number": self._mission_stage_sequence + 1,
            "confidence": overall_confidence,
            "final_status": final_status,
            "execution_time_ms": execution_time_ms,
        }

    def _emit_mission_error_event(
        self,
        mission_id: str,
        session_id: str,
        error: str,
        retry_count: int = 0,
        can_retry: bool = False,
        current_stage: str | None = None,
    ) -> dict:
        """Emit mission error event.

        Args:
            mission_id: Mission run ID
            session_id: Session ID
            error: Error message
            retry_count: Number of retries attempted
            can_retry: Whether this error is retryable
            current_stage: Current stage when error occurred

        Returns:
            Mission error event dict
        """
        return {
            "version": "v1",
            "type": "mission_error",
            "stage": current_stage,
            "mission_id": mission_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "error": error,
                "can_retry": can_retry,
            },
            "sequence_number": self._mission_stage_sequence + 1,
            "error": error,
            "retry_count": retry_count,
            "can_retry": can_retry,
        }

    def _increment_tool_calls(self) -> tuple[bool, str | None]:
        """Increment tool call counter and check budget.

        Returns:
            (can_continue: bool, error_message: str | None)
        """
        self._mission_tool_call_count += 1
        return self._check_mission_budget()

    def _increment_sql_retry(self) -> None:
        """Increment SQL retry counter."""
        self._mission_sql_retry_count += 1

    def _increment_identical_failure(self) -> tuple[bool, str | None]:
        """Increment identical failure counter and check budget.

        Returns:
            (can_continue: bool, error_message: str | None)
        """
        self._mission_identical_failure_count += 1
        return self._check_mission_budget()

    def _get_mission_status_snapshot(self) -> dict:
        """Get current mission status snapshot for monitoring.

        Returns:
            Dict with current mission state
        """
        elapsed = time.time() - (self._mission_start_time or time.time())
        return {
            "current_stage": self._mission_current_stage,
            "stages_completed": self._mission_stages_completed.copy(),
            "tool_calls": self._mission_tool_call_count,
            "sql_retries": self._mission_sql_retry_count,
            "identical_failures": self._mission_identical_failure_count,
            "runtime_seconds": elapsed,
            "budget_remaining": {
                "runtime_seconds": max(0, self._mission_max_runtime_seconds - elapsed),
                "tool_calls": max(0, self._mission_max_tool_calls - self._mission_tool_call_count),
                "sql_retries": max(0, self._mission_max_sql_retries - self._mission_sql_retry_count),
                "identical_failures": max(0, self._mission_max_identical_failures - self._mission_identical_failure_count),
            },
        }
