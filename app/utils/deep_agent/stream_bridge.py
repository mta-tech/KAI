"""Helpers for translating Deep Agent stream events into legacy queue messages."""

from __future__ import annotations

import json
import logging
from typing import Callable, Dict, Iterable

logger = logging.getLogger(__name__)


def bridge_event_to_queue(
    *,
    event: Dict,
    queue,
    format_fn: Callable[[str], str],
    include_tool_name: bool = False,
    artifact_log: list | None = None,
) -> None:
    """Translate a Deep Agent event into legacy-style streaming messages."""

    if not event:
        logger.debug(f"[DEEPAGENT BRIDGE] Empty event, skipping")
        return

    logger.info(f"[DEEPAGENT BRIDGE] Processing event with keys: {list(event.keys())}")

    todos: Iterable[dict] = event.get("todos", []) or []
    if todos:
        logger.info(f"[DEEPAGENT BRIDGE] Processing {len(list(todos))} todos")
        formatted = "\n**Plan Update**\n"
        for todo in todos:
            status = todo.get("status", "pending")
            text = todo.get("text", "")
            formatted += f"- [{status}] {text}\n"
        queue.put(formatted)
        if artifact_log is not None:
            artifact_log.append({"type": "todos", "items": todos})

    tool_run = event.get("tool")
    if tool_run:
        name = tool_run.get("name", "tool")
        output = tool_run.get("output", "")
        logger.info(f"[DEEPAGENT BRIDGE] Processing tool run: {name}, output length: {len(str(output))}")
        parsed_output = _maybe_json(output)
        files = parsed_output.get("files") if isinstance(parsed_output, dict) else None
        header = (
            f"\n**Observation ({name})**\n"
            if include_tool_name
            else "\n**Observation:**\n"
        )
        queue.put(header + format_fn(str(output).strip()) + "\n")
        if files and artifact_log is not None:
            artifact_log.append({"type": "files", "items": files})
        if artifact_log is not None:
            artifact_log.append({"type": "tool", "name": name, "output": output})

    messages = event.get("messages") or []
    if messages:
        logger.info(f"[DEEPAGENT BRIDGE] Processing {len(messages)} messages")
        for i, message in enumerate(messages):
            content = message.get("content") if isinstance(message, dict) else message
            if content:
                logger.info(f"[DEEPAGENT BRIDGE] Message {i}: {str(content)[:100]}...")
                queue.put("\n**Thought**\n " + format_fn(str(content)) + "\n")
                if artifact_log is not None:
                    artifact_log.append({"type": "thought", "content": content})

    if "output" in event and event["output"]:
        answer = event["output"]
        logger.info(f"[DEEPAGENT BRIDGE] Processing final answer: {str(answer)[:100]}...")
        queue.put("\n**Final Answer:**\n " + format_fn(str(answer)) + "\n")
        if artifact_log is not None:
            artifact_log.append({"type": "final", "content": answer})

    files = event.get("files")
    if files and artifact_log is not None:
        artifact_log.append({"type": "files", "items": files})


def _maybe_json(payload: Any) -> dict:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except Exception:
            return {}
    return {}
