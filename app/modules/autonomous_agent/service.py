"""Autonomous agent service using LangChain DeepAgents."""
import json
import logging
import os
import time
from datetime import datetime
from typing import AsyncGenerator

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

from app.modules.autonomous_agent.models import AgentTask, AgentResult
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
            augmented_prompt = "\n\n".join(context_parts) + f"\n\n## User Question\n{task.prompt}"
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

        # Clear deduplication cache for new request
        self._seen_content_hashes.clear()
        self._last_streamed_content = ""

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
            augmented_prompt = "\n\n".join(context_parts) + f"\n\n## User Question\n{task.prompt}"
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

                    # Collect AI responses for memory
                    if processed.get("type") == "token":
                        final_answer_parts.append(processed.get("content", ""))

                    yield processed

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

    def _process_event(self, event: dict) -> dict:
        """Process LangGraph event for streaming."""
        event_type = event.get("event")

        if event_type == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk:
                content = chunk.content if hasattr(chunk, "content") else ""
                if content:
                    # Normalize content to string
                    if isinstance(content, list):
                        # Extract text from list of content blocks
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

                    # Detect cumulative content: if new content starts with last content,
                    # only emit the delta (new part)
                    if self._last_streamed_content and content.startswith(self._last_streamed_content):
                        delta = content[len(self._last_streamed_content):]
                        if not delta:
                            return {"type": "other", "event": "no_new_content"}
                        self._last_streamed_content = content
                        return {"type": "token", "content": delta}

                    # Not cumulative - use hash deduplication for exact duplicates
                    content_hash = hash(content)
                    if content_hash in self._seen_content_hashes:
                        return {"type": "other", "event": "duplicate_skipped"}
                    self._seen_content_hashes.add(content_hash)

                    # Track for cumulative detection
                    self._last_streamed_content = content
                    return {"type": "token", "content": content}

        elif event_type == "on_tool_start":
            # Reset cumulative tracking on tool boundaries (context switch)
            self._last_streamed_content = ""

            # Check for write_todos to capture todo state
            if event.get("name") == "write_todos":
                return {
                    "type": "todo_update",
                    "todos": event.get("data", {}).get("input", {}).get("todos", [])
                }

            # Capture regular tool starts
            return {
                "type": "tool_start",
                "tool": event.get("name"),
                "input": event.get("data", {}).get("input"),
            }

        elif event_type == "on_tool_end":
            # Reset cumulative tracking on tool boundaries (context switch)
            self._last_streamed_content = ""

            # Capture full output, let CLI handle display truncation
            output = str(event.get("data", {}).get("output", ""))
            return {
                "type": "tool_end",
                "tool": event.get("name"),
                "output": output,
            }

        return {"type": "other", "event": event_type}

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
