"""Adapter that selects between legacy SQL generators and the Deep Agent runtime."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from fastapi import HTTPException

from app.agents import create_kai_sql_agent
from app.agents.deep_agent_factory import DeepAgentRuntimeUnavailable
from app.modules.database_connection.models import DatabaseConnection
from app.modules.sql_generation.models import LLMConfig, SQLGeneration
from app.modules.sql_generation.repositories import SQLGenerationRepository
from app.modules.table_description.models import TableDescriptionStatus
from app.modules.table_description.repositories import TableDescriptionRepository
from app.modules.context_store.services import ContextStoreService
from app.modules.instruction.services import InstructionService
from app.modules.business_glossary.services import BusinessGlossaryService
from app.utils.sql_database.sql_database import SQLDatabase
from app.utils.sql_generator.graph_agent import LangGraphSQLAgent
from app.utils.sql_generator.sql_agent import SQLAgent
from app.utils.sql_generator.sql_agent_dev import FullContextSQLAgent
from app.utils.sql_generator.sql_agent_graph import LangGraphReActSQLAgent
from app.utils.sql_generator.sql_agent_dev_graph import LangGraphFullContextSQLAgent
from app.utils.sql_generator.sql_generator import SQLGenerator
from app.utils.model.embedding_model import EmbeddingModel
from app.data.db.storage import Storage
from app.utils.deep_agent.tools import KaiToolContext
from app.utils.deep_agent.stream_bridge import bridge_event_to_queue
from app.server.config import Settings

logger = logging.getLogger(__name__)

# Feature flag for gradual rollout of LangGraph ReAct agents
USE_LANGGRAPH_AGENTS = os.getenv("USE_LANGGRAPH_AGENTS", "false").lower() == "true"


class DeepAgentSQLGeneratorProxy(SQLGenerator):
    """SQLGenerator-compatible wrapper around the Deep Agent runtime."""

    # Maximum retries when sensitive keywords are detected
    MAX_SENSITIVE_KEYWORD_RETRIES = 2

    # Sensitive keywords that should trigger retry instead of error
    SENSITIVE_KEYWORDS = ["CREATE", "DROP", "DELETE", "UPDATE", "INSERT", "GRANT",
                          "REVOKE", "ALTER", "TRUNCATE", "MERGE", "EXECUTE"]

    def __init__(
        self,
        llm_config: LLMConfig,
        *,
        tenant_id: str | None,
        sql_generation_id: str,
        db_connection: DatabaseConnection,
        database: SQLDatabase,
        tool_context: KaiToolContext | None = None,
        extra_instructions: list[str] | None = None,
    ):
        super().__init__(llm_config)
        self.tenant_id = tenant_id or "tenant-default"
        self.sql_generation_id = sql_generation_id
        self.db_connection = db_connection
        self.database = database
        self.tool_context = tool_context
        self.extra_instructions = extra_instructions or []

    def _prepare_tool_context(
        self,
        user_prompt,
        context: list[dict] | None,
    ) -> tuple[KaiToolContext, list[str]]:
        settings = Settings()
        storage = Storage(settings)
        table_repo = TableDescriptionRepository(storage)
        db_scan = table_repo.get_all_tables_by_db(
            {
                "db_connection_id": str(self.db_connection.id),
                "sync_status": TableDescriptionStatus.SCANNED.value,
            }
        )
        db_scan = self.filter_tables_by_schema(db_scan=db_scan, prompt=user_prompt)

        context_store_service = ContextStoreService(storage)
        few_shot_examples = context_store_service.retrieve_context_for_question(
            user_prompt
        )
        instruction_service = InstructionService(storage)
        instructions = instruction_service.retrieve_instruction_for_question(user_prompt)
        business_metrics_service = BusinessGlossaryService(storage)
        business_metrics = business_metrics_service.retrieve_business_metrics_for_question(
            user_prompt
        )

        extra_instructions: list[str] = []
        if instructions:
            for instruction in instructions:
                rules = instruction.get("rules")
                if rules:
                    extra_instructions.append(rules)

        embedding_model = EmbeddingModel().get_model()

        tool_context = KaiToolContext(
            database=self.database,
            db_scan=db_scan,
            embedding=embedding_model,
            context=context,
            few_shot_examples=few_shot_examples or [],
            business_metrics=business_metrics or [],
            aliases=[],  # Aliases handled separately
            is_multiple_schema=len(user_prompt.schemas or []) > 1,
            top_k=self.get_upper_bound_limit(),
            tenant_id=self.tenant_id,
            sql_generation_id=self.sql_generation_id,
        )

        return tool_context, extra_instructions

    def _invoke_agent(
        self,
        user_prompt,
        metadata: Dict[str, Any] | None,
        context: list[dict] | None,
    ) -> dict:
        msg = f"[DEEPAGENT] _invoke_agent called for prompt: {user_prompt.text[:100]}..."
        logger.info(msg)

        if self.tool_context:
            tool_context = self.tool_context
            extra_instr = self.extra_instructions
            logger.info(f"[DEEPAGENT] Using pre-built tool context")
        else:
            logger.info(f"[DEEPAGENT] Preparing tool context from prompt")
            tool_context, extra_instr = self._prepare_tool_context(user_prompt, context)

        logger.info(f"[DEEPAGENT] Creating agent via create_kai_sql_agent")
        agent = create_kai_sql_agent(
            tenant_id=self.tenant_id,
            sql_generation_id=self.sql_generation_id,
            db_connection=self.db_connection,
            database=self.database,
            context=context,
            tool_context=tool_context,
            metadata=metadata,
            extra_instructions=extra_instr,
            llm_config=self.llm_config,
        )

        # Build initial state for native deepagents library
        # Native deepagents only needs "messages" key
        from langchain_core.messages import HumanMessage
        initial_state = {
            "messages": [HumanMessage(content=user_prompt.text)],
        }

        msg = f"[DEEPAGENT] Invoking agent with prompt: {user_prompt.text}"
        logger.info(msg)

        result = agent.invoke(initial_state)

        msg = f"[DEEPAGENT] Agent invocation complete. Result keys: {list(result.keys())}"
        logger.info(msg)

        messages = result.get('messages', [])
        msg = f"[DEEPAGENT] Number of messages in result: {len(messages)}"
        logger.info(msg)

        # Log all messages with details at debug level
        from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
        logger.debug("=" * 80)
        logger.debug("[DEEPAGENT] MESSAGE TRACE - All Messages from Agent Execution")
        logger.debug("=" * 80)
        for i, message in enumerate(messages):
            msg_type = type(message).__name__
            content = message.content if hasattr(message, 'content') else str(message)

            logger.debug(f"[DEEPAGENT] Message {i} | Type: {msg_type}")

            # Log additional message attributes
            if hasattr(message, 'additional_kwargs') and message.additional_kwargs:
                logger.debug(f"[DEEPAGENT]   Additional kwargs: {list(message.additional_kwargs.keys())}")

            if isinstance(message, ToolMessage):
                tool_name = getattr(message, 'name', 'unknown')
                logger.debug(f"[DEEPAGENT]   Tool: {tool_name}")
                logger.debug(f"[DEEPAGENT]   Content: {str(content)[:200]}...")
            elif isinstance(message, AIMessage):
                # Check for tool calls
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    logger.debug(f"[DEEPAGENT]   Tool Calls: {len(message.tool_calls)}")
                    for tc in message.tool_calls:
                        tool_name = tc.get('name', 'unknown')
                        tool_args = tc.get('args', {})

                        # Detect subagent delegation
                        if tool_name == 'task':
                            # Check multiple possible keys for subagent name
                            subagent_name = (tool_args.get('agent') or
                                           tool_args.get('subagent') or
                                           tool_args.get('name') or
                                           'unknown')
                            subagent_prompt = tool_args.get('prompt', '')
                            logger.debug(f"[DEEPAGENT]     SUBAGENT DELEGATION: {subagent_name}")
                            logger.debug(f"[DEEPAGENT]        Prompt: {str(subagent_prompt)[:150]}...")
                            logger.debug(f"[DEEPAGENT]        Full args: {str(tool_args)[:200]}...")
                        else:
                            logger.debug(f"[DEEPAGENT]     - {tool_name}: {str(tool_args)[:100]}...")
                if content:
                    logger.debug(f"[DEEPAGENT]   Content: {str(content)[:300]}...")
            elif isinstance(message, HumanMessage):
                logger.debug(f"[DEEPAGENT]   Content: {str(content)[:200]}...")
            else:
                logger.debug(f"[DEEPAGENT]   Content: {str(content)[:200]}...")

        logger.debug("=" * 80)

        return result

    def _stream_agent(
        self,
        user_prompt,
        metadata: Dict[str, Any] | None,
        context: list[dict] | None,
        queue,
    ) -> dict:
        logger.info(f"[DEEPAGENT] _stream_agent called for prompt: {user_prompt.text[:100]}...")

        if self.tool_context:
            tool_context = self.tool_context
            extra_instr = self.extra_instructions
            logger.info(f"[DEEPAGENT] Using pre-built tool context")
        else:
            logger.info(f"[DEEPAGENT] Preparing tool context from prompt")
            tool_context, extra_instr = self._prepare_tool_context(user_prompt, context)

        logger.info(f"[DEEPAGENT] Creating agent via create_kai_sql_agent")
        agent = create_kai_sql_agent(
            tenant_id=self.tenant_id,
            sql_generation_id=self.sql_generation_id,
            db_connection=self.db_connection,
            database=self.database,
            context=context,
            tool_context=tool_context,
            metadata=metadata,
            extra_instructions=extra_instr,
            llm_config=self.llm_config,
        )

        # Build initial state for native deepagents library
        from langchain_core.messages import HumanMessage
        initial_state = {
            "messages": [HumanMessage(content=user_prompt.text)],
        }

        final_event = {}
        stream = getattr(agent, "stream", None)
        if stream is None:
            raise AttributeError("Deep Agent runtime does not support streaming")

        logger.info(f"[DEEPAGENT] Starting stream with prompt: {user_prompt.text}")
        artifact_log: list = []
        event_count = 0

        for event in stream(initial_state):
            event_count += 1
            logger.info(f"[DEEPAGENT] Stream event {event_count}: {list(event.keys()) if event else 'None'}")

            # Log detailed event information at debug level
            if event:
                logger.debug(f"[DEEPAGENT STREAM] Event {event_count}")
                logger.debug(f"[DEEPAGENT STREAM]   Keys: {list(event.keys())}")

                # Log messages in this event
                if 'messages' in event and event['messages']:
                    from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
                    for msg in event['messages']:
                        msg_type = type(msg).__name__
                        content = msg.content if hasattr(msg, 'content') else ''

                        if isinstance(msg, AIMessage):
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                tool_names = [tc.get('name') for tc in msg.tool_calls]
                                logger.debug(f"[DEEPAGENT STREAM]   AI -> Tool Calls: {tool_names}")

                                # Check for subagent delegations
                                for tc in msg.tool_calls:
                                    if tc.get('name') == 'task':
                                        subagent_name = tc.get('args', {}).get('agent', 'unknown')
                                        subagent_prompt = tc.get('args', {}).get('prompt', '')
                                        logger.debug(f"[DEEPAGENT STREAM]   SUBAGENT DELEGATION: {subagent_name}")
                                        logger.debug(f"[DEEPAGENT STREAM]      Prompt: {str(subagent_prompt)[:100]}...")
                            if content:
                                logger.debug(f"[DEEPAGENT STREAM]   AI -> {str(content)[:150]}...")
                        elif isinstance(msg, ToolMessage):
                            tool_name = getattr(msg, 'name', 'unknown')
                            # Highlight subagent results
                            if tool_name == 'task':
                                logger.debug(f"[DEEPAGENT STREAM]   SUBAGENT RESULT: {str(content)[:150]}...")
                            else:
                                logger.debug(f"[DEEPAGENT STREAM]   Tool Result ({tool_name}): {str(content)[:150]}...")

                # Log todos
                if 'todos' in event and event['todos']:
                    logger.debug(f"[DEEPAGENT STREAM]   Todos: {len(event['todos'])} items")
                    for todo in event['todos']:
                        status = todo.get('status', 'unknown')
                        text = todo.get('text', '')
                        logger.debug(f"[DEEPAGENT STREAM]     [{status}] {text}")

                # Log files
                if 'files' in event and event['files']:
                    logger.debug(f"[DEEPAGENT STREAM]   Files: {event['files']}")

            bridge_event_to_queue(
                event=event,
                queue=queue,
                format_fn=self.format_sql_query_intermediate_steps,
                include_tool_name=False,
                artifact_log=artifact_log,
            )
            final_event = event or final_event

        logger.info(f"[DEEPAGENT] Stream complete. Total events: {event_count}")
        logger.info(f"[DEEPAGENT] Final event keys: {list(final_event.keys()) if final_event else 'None'}")
        logger.info(f"[DEEPAGENT] Artifact log entries: {len(artifact_log)}")

        return final_event, artifact_log

    def _detect_sensitive_keyword_error(self, response: SQLGeneration) -> str | None:
        """Detect if the error is caused by a sensitive SQL keyword.

        Returns the detected keyword if found, None otherwise.
        """
        if response.status != "INVALID" or not response.error:
            return None

        error_lower = response.error.lower()
        if "sensitive sql keyword" not in error_lower:
            return None

        # Extract the keyword from the error message
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword.lower() in error_lower:
                return keyword

        return "UNKNOWN"

    def _create_retry_prompt_with_fix_instruction(
        self,
        original_prompt: str,
        detected_keyword: str,
        retry_count: int,
    ) -> str:
        """Create a modified prompt instructing the agent to avoid sensitive keywords."""
        fix_instruction = f"""

IMPORTANT CORRECTION (Attempt {retry_count + 1}):
Your previous SQL query contained the '{detected_keyword}' keyword which is not allowed.
Only SELECT queries are permitted. Do NOT use {detected_keyword}, CREATE, DROP, DELETE, UPDATE, INSERT, or any DDL/DML statements.

If the user is asking about available tables, columns, or metrics, use a SELECT query to retrieve this information from the database schema/information_schema, or provide the information based on the schema context you already have.

Please generate a valid SELECT query to answer the original question.

Original question: {original_prompt}"""
        return fix_instruction

    def generate_response(
        self,
        user_prompt,
        database_connection,
        context: list[dict] | None = None,
        metadata: dict | None = None,
    ) -> SQLGeneration:
        retry_count = 0
        last_response = None
        original_text = user_prompt.text

        while retry_count <= self.MAX_SENSITIVE_KEYWORD_RETRIES:
            try:
                # Modify prompt if this is a retry
                if retry_count > 0 and last_response:
                    detected_keyword = self._detect_sensitive_keyword_error(last_response)
                    user_prompt.text = self._create_retry_prompt_with_fix_instruction(
                        original_text, detected_keyword or "CREATE", retry_count
                    )
                    logger.info(f"[DEEPAGENT] Retry {retry_count}: Reinvoking agent with fix instruction for '{detected_keyword}'")

                result = self._invoke_agent(user_prompt, metadata, context)
            except DeepAgentRuntimeUnavailable as exc:  # pragma: no cover - env guard
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            except Exception as exc:  # pragma: no cover - future logging
                logger.exception("Deep Agent invocation failed")
                raise HTTPException(status_code=500, detail=str(exc)) from exc

            # Extract SQL from the final message
            sql_text = self._extract_sql_from_result(result)

            # If no SQL found, extract clarifying message from the agent
            clarifying_message = None
            if not sql_text:
                clarifying_message = self._extract_clarifying_message(result)

            response = SQLGeneration(
                prompt_id=user_prompt.id,
                llm_config=self.llm_config,
                sql=sql_text,
                metadata={
                    "runtime": "native_deep_agent",
                    "runtime_details": {
                        "message_count": len(result.get("messages", [])),
                        "retry_count": retry_count,
                    },
                },
            )

            # Add clarifying message to metadata if present
            if clarifying_message:
                response.metadata["clarifying_message"] = clarifying_message
                logger.info(f"[DEEPAGENT] Added clarifying message to response metadata")

            # Validate the SQL query
            response = self.create_sql_query_status(
                db=self.database,
                query=response.sql or "",
                sql_generation=response,
            )

            # Check if we need to retry due to sensitive keyword
            detected_keyword = self._detect_sensitive_keyword_error(response)
            if detected_keyword and retry_count < self.MAX_SENSITIVE_KEYWORD_RETRIES:
                logger.warning(
                    f"[DEEPAGENT] Sensitive keyword '{detected_keyword}' detected in SQL. "
                    f"Retrying ({retry_count + 1}/{self.MAX_SENSITIVE_KEYWORD_RETRIES})..."
                )
                last_response = response
                retry_count += 1
                # Restore original prompt text for next iteration
                user_prompt.text = original_text
                continue

            # Success or max retries reached
            if retry_count > 0:
                response.metadata["retry_info"] = {
                    "total_retries": retry_count,
                    "reason": "sensitive_keyword_detected",
                }
                if response.status == "VALID":
                    logger.info(f"[DEEPAGENT] Successfully generated valid SQL after {retry_count} retries")

            # Restore original prompt text before returning
            user_prompt.text = original_text
            return response

        # This shouldn't be reached, but just in case
        user_prompt.text = original_text
        return last_response or response

    def _extract_sql_from_result(self, result: dict) -> str:
        """Extract SQL from the Deep Agent result."""
        from langchain_core.messages import AIMessage, HumanMessage
        import re

        logger.info(f"[DEEPAGENT] _extract_sql_from_result called")
        logger.info(f"[DEEPAGENT] Result keys: {list(result.keys())}")

        # Check for final_sql in state
        if result.get("final_sql"):
            logger.info(f"[DEEPAGENT] Found final_sql in state: {result['final_sql'][:100]}...")
            return result["final_sql"]

        # Extract from messages - check all messages, not just AI messages
        messages = result.get("messages", [])
        logger.info(f"[DEEPAGENT] Extracting from {len(messages)} messages")

        # First pass: Look for SQL code blocks in any message
        for i, msg in enumerate(reversed(messages)):
            msg_idx = len(messages) - 1 - i
            # Skip human messages
            if isinstance(msg, HumanMessage):
                logger.info(f"[DEEPAGENT] Message {msg_idx}: HumanMessage (skipped)")
                continue

            content = msg.content if hasattr(msg, 'content') else str(msg)
            msg_type = type(msg).__name__
            logger.info(f"[DEEPAGENT] Message {msg_idx} ({msg_type}): {content[:200] if content else 'None'}...")

            if not content:
                continue

            # Look for SQL in code blocks (most reliable)
            # Match ```sql\n...\n``` or ```sql ... ``` patterns
            sql_block_pattern = r'```sql\s*\n(.*?)```'
            matches = re.findall(sql_block_pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                # Return the last SQL block found (most recent)
                sql = matches[-1].strip()
                if sql:
                    logger.info(f"[DEEPAGENT] Found SQL in code block (multiline): {sql[:100]}...")
                    return sql

            # Also try without newline after ```sql
            sql_block_pattern_inline = r'```sql\s+(.*?)```'
            matches = re.findall(sql_block_pattern_inline, content, re.DOTALL | re.IGNORECASE)
            if matches:
                sql = matches[-1].strip()
                if sql:
                    logger.info(f"[DEEPAGENT] Found SQL in code block (inline): {sql[:100]}...")
                    return sql

        # Second pass: Look for SELECT/WITH/INSERT/UPDATE/DELETE statements
        # (fallback for cases where code blocks aren't used)
        logger.info(f"[DEEPAGENT] First pass (code blocks) found no SQL, trying second pass (SQL keywords)")

        for i, msg in enumerate(reversed(messages)):
            msg_idx = len(messages) - 1 - i
            if isinstance(msg, HumanMessage):
                continue

            content = msg.content if hasattr(msg, 'content') else str(msg)
            if not content:
                continue

            content_upper = content.upper()

            # Check for common SQL statement starters
            sql_starters = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE']
            for starter in sql_starters:
                if starter in content_upper:
                    logger.info(f"[DEEPAGENT] Found '{starter}' keyword in message {msg_idx}")
                    # Try to extract SQL-like content
                    # Find the line with the SQL starter
                    lines = content.split("\n")
                    sql_lines = []
                    in_sql = False

                    for line in lines:
                        line_stripped = line.strip()
                        if not in_sql and starter in line_stripped.upper():
                            in_sql = True

                        if in_sql:
                            sql_lines.append(line)
                            # Stop at semicolon or empty line after SQL started
                            if ";" in line:
                                break

                    if sql_lines:
                        sql = "\n".join(sql_lines).strip()
                        # Clean up if it ends with semicolon
                        if sql.endswith(";"):
                            sql = sql[:-1].strip() + ";"
                        logger.info(f"[DEEPAGENT] Extracted SQL from keyword match: {sql[:100]}...")
                        return sql

        logger.warning(f"[DEEPAGENT] No SQL found in any messages!")
        return ""

    def _extract_clarifying_message(self, result: dict) -> str | None:
        """Extract clarifying message from the last AI message when no SQL was generated.

        This is used when the agent needs more information or cannot generate SQL.
        """
        from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

        messages = result.get("messages", [])
        logger.info(f"[DEEPAGENT] _extract_clarifying_message: {len(messages)} messages to check")

        if not messages:
            logger.warning("[DEEPAGENT] No messages in result to extract clarifying message from")
            return None

        # Log message types for debugging
        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            content = getattr(msg, 'content', None)
            has_tool_calls = hasattr(msg, 'tool_calls') and msg.tool_calls
            logger.info(f"[DEEPAGENT] Message {i}: type={msg_type}, content_len={len(content) if content else 0}, has_tool_calls={has_tool_calls}")

        # Look for the last AI message that contains actual content (not tool calls)
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                content = msg.content if hasattr(msg, 'content') else None
                if content and isinstance(content, str) and content.strip():
                    # Skip if it looks like it contains SQL (shouldn't happen, but safety check)
                    content_upper = content.upper()
                    if any(kw in content_upper for kw in ['SELECT ', 'WITH ', 'INSERT ', 'UPDATE ', 'DELETE ']):
                        logger.info(f"[DEEPAGENT] Skipping message with SQL keywords")
                        continue

                    logger.info(f"[DEEPAGENT] Extracted clarifying message from AIMessage: {content[:200]}...")
                    return content.strip()

        # Fallback: Look for tool message results that might contain useful info
        # (e.g., schema information that the agent retrieved but couldn't turn into SQL)
        for msg in reversed(messages):
            if isinstance(msg, ToolMessage):
                tool_name = getattr(msg, 'name', '')
                # Don't use tool results that are just schema dumps
                if tool_name in ['get_schema', 'get_table_schema', 'list_tables']:
                    continue
                content = msg.content if hasattr(msg, 'content') else None
                if content and isinstance(content, str) and len(content) < 500:
                    logger.info(f"[DEEPAGENT] Using tool message as clarifying info: {content[:200]}...")
                    # Don't return tool results directly, just note we found something
                    break

        logger.warning("[DEEPAGENT] No clarifying message found in messages")
        return None

    def stream_response(
        self,
        user_prompt,
        database_connection,
        response,
        queue,
        metadata: dict | None = None,
    ):
        artifact_log: list = []
        clarifying_message = None
        final_event = None
        retry_count = 0
        original_text = user_prompt.text

        try:
            final_event, artifact_log = self._stream_agent(
                user_prompt=user_prompt,
                metadata=metadata,
                context=None,
                queue=queue,
            )
            # Extract SQL from final event
            response.sql = self._extract_sql_from_result(final_event)

            # If no SQL found, extract clarifying message
            if not response.sql and final_event:
                clarifying_message = self._extract_clarifying_message(final_event)
        except AttributeError:
            queue.put("Deep Agent runtime missing streaming support; falling back to sync execution.\n")
            final_response = self.generate_response(
                user_prompt=user_prompt,
                database_connection=database_connection,
                metadata=metadata,
            )
            response.sql = final_response.sql
            # Copy clarifying message from sync response if present
            if final_response.metadata and final_response.metadata.get("clarifying_message"):
                clarifying_message = final_response.metadata["clarifying_message"]
            # Copy retry info if present
            if final_response.metadata and final_response.metadata.get("retry_info"):
                response.metadata = response.metadata or {}
                response.metadata["retry_info"] = final_response.metadata["retry_info"]
            queue.put(None)
            return final_response
        finally:
            queue.put(None)

        response.metadata = response.metadata or {}
        response.metadata["runtime"] = "native_deep_agent"
        runtime_details = response.metadata.setdefault("runtime_details", {})
        runtime_details["artifacts"] = artifact_log

        # Add clarifying message to metadata if present
        if clarifying_message:
            response.metadata["clarifying_message"] = clarifying_message
            logger.info(f"[DEEPAGENT] Added clarifying message to stream response metadata")

        # Validate the SQL query
        response = self.create_sql_query_status(
            db=self.database,
            query=response.sql or "",
            sql_generation=response,
        )

        # Check if we need to retry due to sensitive keyword
        detected_keyword = self._detect_sensitive_keyword_error(response)
        if detected_keyword and retry_count < self.MAX_SENSITIVE_KEYWORD_RETRIES:
            logger.warning(
                f"[DEEPAGENT] Sensitive keyword '{detected_keyword}' detected in streamed SQL. "
                f"Falling back to sync retry..."
            )
            # For streaming, we fall back to sync generate_response which handles retries
            user_prompt.text = self._create_retry_prompt_with_fix_instruction(
                original_text, detected_keyword, 1
            )
            try:
                retry_response = self.generate_response(
                    user_prompt=user_prompt,
                    database_connection=database_connection,
                    metadata=metadata,
                )
                # Restore original prompt text
                user_prompt.text = original_text
                # Merge retry info
                if retry_response.status == "VALID":
                    logger.info(f"[DEEPAGENT] Successfully generated valid SQL after stream retry")
                return retry_response
            except Exception as e:
                logger.exception(f"[DEEPAGENT] Retry after stream failed: {e}")
                user_prompt.text = original_text
                # Return original invalid response
                return response

        return response


class KaiSqlGeneratorAdapter:
    """Factory that returns the appropriate SQLGenerator implementation."""

    def __init__(self, repository: SQLGenerationRepository):
        self.repository = repository

    def _legacy_generator(
        self,
        option: str,
        llm_config: LLMConfig,
    ) -> SQLGenerator:
        # Use LangGraph ReAct agents when feature flag is enabled
        if USE_LANGGRAPH_AGENTS:
            if option == "dev":
                logger.info("Using LangGraph Full Context SQL Agent")
                return LangGraphFullContextSQLAgent(llm_config)
            if option == "graph":
                return LangGraphSQLAgent(llm_config)
            logger.info("Using LangGraph ReAct SQL Agent")
            return LangGraphReActSQLAgent(llm_config)

        # Legacy agents (deprecated patterns)
        if option == "dev":
            return FullContextSQLAgent(llm_config)
        if option == "graph":
            return LangGraphSQLAgent(llm_config)
        return SQLAgent(llm_config)

    def _is_deep_agent_enabled(
        self,
        option: str,
        tenant_id: str | None,
        metadata: dict | None,
    ) -> bool:
        if option == "deep_agent":
            return True
        feature_flag = (metadata or {}).get("use_deep_agent")
        if isinstance(feature_flag, bool):
            return feature_flag
        # Placeholder: future per-tenant toggle hook
        return False

    def is_deep_agent_enabled(
        self,
        option: str,
        tenant_id: str | None,
        metadata: dict | None,
    ) -> bool:
        return self._is_deep_agent_enabled(option, tenant_id, metadata)

    def select_generator(
        self,
        *,
        option: str,
        llm_config: LLMConfig,
        tenant_id: str | None,
        sql_generation_id: str,
        db_connection: DatabaseConnection,
        database: SQLDatabase,
        metadata: dict | None,
        tool_context: KaiToolContext | None = None,
        extra_instructions: list[str] | None = None,
    ) -> SQLGenerator:
        if self._is_deep_agent_enabled(option, tenant_id, metadata):
            return DeepAgentSQLGeneratorProxy(
                llm_config,
                tenant_id=tenant_id,
                sql_generation_id=sql_generation_id,
                db_connection=db_connection,
                database=database,
                tool_context=tool_context,
                extra_instructions=extra_instructions,
            )
        return self._legacy_generator(option, llm_config)
