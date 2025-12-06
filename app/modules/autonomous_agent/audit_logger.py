"""Audit logger for capturing agent execution traces.

This module provides detailed logging of all agent interactions including:
- User prompts
- Agent reasoning/thinking
- Tool calls and results
- Final responses
- Timing information

The audit log is written as a JSONL (JSON Lines) file for easy parsing.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


class AuditLogger:
    """Logger for capturing detailed agent execution traces.

    Writes all interactions to a JSONL file for audit purposes.
    Each line is a JSON object representing one event.
    """

    def __init__(
        self,
        output_path: str | Path,
        session_id: str,
        db_connection_id: str,
        mode: str = "full_autonomy",
    ):
        """Initialize the audit logger.

        Args:
            output_path: Path to the audit log file
            session_id: Session identifier
            db_connection_id: Database connection ID
            mode: Agent operation mode
        """
        self.output_path = Path(output_path)
        self.session_id = session_id
        self.db_connection_id = db_connection_id
        self.mode = mode
        self.start_time = datetime.now()
        self._event_count = 0
        self._file_handle = None

        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write session header
        self._write_header()

    def _write_header(self) -> None:
        """Write session metadata header."""
        header = {
            "event_type": "session_start",
            "timestamp": self.start_time.isoformat(),
            "session_id": self.session_id,
            "db_connection_id": self.db_connection_id,
            "mode": self.mode,
            "output_file": str(self.output_path),
        }
        self._write_event(header)

    def _write_event(self, event: dict[str, Any]) -> None:
        """Write an event to the log file.

        Args:
            event: Event data to write
        """
        self._event_count += 1
        event["event_id"] = self._event_count

        with open(self.output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")

    def log_user_prompt(self, prompt: str, task_id: str | None = None) -> None:
        """Log a user prompt.

        Args:
            prompt: The user's input prompt
            task_id: Optional task identifier
        """
        self._write_event({
            "event_type": "user_prompt",
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "prompt": prompt,
        })

    def log_reasoning(self, content: str) -> None:
        """Log agent reasoning/thinking content.

        Args:
            content: The reasoning text from the agent
        """
        self._write_event({
            "event_type": "reasoning",
            "timestamp": datetime.now().isoformat(),
            "content": content,
        })

    def log_token(self, token: str) -> None:
        """Log a streamed token.

        Note: For efficiency, tokens are batched - call log_token_batch
        for multiple tokens.

        Args:
            token: The token content
        """
        # Don't log individual tokens - too verbose
        # Use log_response for the complete response
        pass

    def log_tool_start(
        self,
        tool_name: str,
        tool_input: Any,
        tool_call_id: str | None = None,
    ) -> None:
        """Log the start of a tool call.

        Args:
            tool_name: Name of the tool being called
            tool_input: Input parameters to the tool
            tool_call_id: Optional tool call identifier
        """
        # Sanitize tool input for logging (handle non-serializable objects)
        try:
            if isinstance(tool_input, dict):
                # Remove potentially large/sensitive fields
                sanitized = {
                    k: v for k, v in tool_input.items()
                    if k not in {"runtime", "config", "state", "messages", "memory"}
                }
                # Truncate very long string values
                for k, v in sanitized.items():
                    if isinstance(v, str) and len(v) > 5000:
                        sanitized[k] = v[:5000] + f"... [truncated {len(v) - 5000} chars]"
            else:
                sanitized = str(tool_input)
                if len(sanitized) > 5000:
                    sanitized = sanitized[:5000] + f"... [truncated {len(sanitized) - 5000} chars]"
        except Exception:
            sanitized = str(tool_input)[:1000]

        self._write_event({
            "event_type": "tool_start",
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "tool_call_id": tool_call_id,
            "input": sanitized,
        })

    def log_tool_end(
        self,
        tool_name: str,
        tool_output: Any,
        tool_call_id: str | None = None,
        duration_ms: int | None = None,
    ) -> None:
        """Log the end of a tool call.

        Args:
            tool_name: Name of the tool that was called
            tool_output: Output from the tool
            tool_call_id: Optional tool call identifier
            duration_ms: Optional duration in milliseconds
        """
        # Sanitize output
        try:
            output_str = str(tool_output)
            if len(output_str) > 10000:
                output_str = output_str[:10000] + f"... [truncated {len(output_str) - 10000} chars]"
        except Exception:
            output_str = "[Unable to serialize output]"

        self._write_event({
            "event_type": "tool_end",
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "tool_call_id": tool_call_id,
            "output": output_str,
            "duration_ms": duration_ms,
        })

    def log_subagent_start(
        self,
        agent_name: str,
        prompt: str,
    ) -> None:
        """Log the start of a subagent call.

        Args:
            agent_name: Name of the subagent
            prompt: Prompt given to the subagent
        """
        self._write_event({
            "event_type": "subagent_start",
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "prompt": prompt,
        })

    def log_subagent_end(
        self,
        agent_name: str,
        result: str,
    ) -> None:
        """Log the end of a subagent call.

        Args:
            agent_name: Name of the subagent
            result: Result from the subagent
        """
        result_str = str(result)
        if len(result_str) > 10000:
            result_str = result_str[:10000] + f"... [truncated {len(result_str) - 10000} chars]"

        self._write_event({
            "event_type": "subagent_end",
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "result": result_str,
        })

    def log_todo_update(self, todos: list[dict]) -> None:
        """Log a todo list update.

        Args:
            todos: List of todo items
        """
        self._write_event({
            "event_type": "todo_update",
            "timestamp": datetime.now().isoformat(),
            "todos": todos,
        })

    def log_memory_loaded(self, stats: dict) -> None:
        """Log memory loading event.

        Args:
            stats: Memory loading statistics
        """
        self._write_event({
            "event_type": "memory_loaded",
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
        })

    def log_skill_loaded(self, skills: list[dict]) -> None:
        """Log skill loading event.

        Args:
            skills: List of loaded skills metadata
        """
        self._write_event({
            "event_type": "skill_loaded",
            "timestamp": datetime.now().isoformat(),
            "skills": skills,
        })

    def log_response(self, response: str, duration_ms: int | None = None) -> None:
        """Log the final agent response.

        Args:
            response: The complete response text
            duration_ms: Optional total duration in milliseconds
        """
        self._write_event({
            "event_type": "response",
            "timestamp": datetime.now().isoformat(),
            "content": response,
            "duration_ms": duration_ms,
        })

    def log_error(self, error: str, context: str | None = None) -> None:
        """Log an error.

        Args:
            error: Error message
            context: Optional context about where the error occurred
        """
        self._write_event({
            "event_type": "error",
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "context": context,
        })

    def log_session_end(self, total_prompts: int = 0) -> None:
        """Log session end.

        Args:
            total_prompts: Total number of prompts in the session
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self._write_event({
            "event_type": "session_end",
            "timestamp": end_time.isoformat(),
            "session_id": self.session_id,
            "total_events": self._event_count,
            "total_prompts": total_prompts,
            "duration_seconds": duration,
        })

    def get_log_path(self) -> str:
        """Get the path to the log file.

        Returns:
            Absolute path to the log file
        """
        return str(self.output_path.absolute())


def create_audit_log_path(
    session_id: str,
    base_dir: str | None = None,
    custom_path: str | None = None,
) -> str:
    """Create a path for the audit log file.

    Args:
        session_id: Session identifier
        base_dir: Base directory for logs (default: ./audit_logs)
        custom_path: Custom path override

    Returns:
        Path for the audit log file
    """
    if custom_path:
        return custom_path

    base_dir = base_dir or "./audit_logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{session_id}_{timestamp}.jsonl"

    return os.path.join(base_dir, filename)
