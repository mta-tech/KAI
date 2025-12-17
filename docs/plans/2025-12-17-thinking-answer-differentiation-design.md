# Design: Thinking/Answer Differentiation via Tag-Based Streaming

## Overview

Replace fragile regex-based heuristics for differentiating agent reasoning from final answers with explicit XML-style tagging and a streaming state machine parser.

## Problem Statement

Current implementation uses `_get_answer_start_regex()` with patterns like `^jumlah\s+\w+` to guess whether streamed content is an answer or reasoning. This causes:

1. **False negatives**: Answers like "Jumlah koperasi di Jakarta adalah 14." incorrectly typed as "thinking"
2. **Maintenance burden**: New patterns must be added for each answer format
3. **Language fragility**: Indonesian patterns differ from English patterns

## Solution

### 1. Prompt-Based Tagging

Instruct the LLM to wrap all output in explicit tags:

```xml
<thinking>
Internal reasoning, planning, analysis, tool decisions
</thinking>

<answer>
Final user-facing response
</answer>
```

### 2. Streaming State Machine

Parse tags in real-time while preserving streaming UX:

```python
from enum import Enum
from dataclasses import dataclass
import re

class StreamContext(Enum):
    NONE = "none"
    THINKING = "thinking"
    ANSWER = "answer"

@dataclass
class ParsedToken:
    content: str
    type: str  # "thinking" or "answer"

class TagStreamParser:
    """State machine for parsing XML-tagged streaming output."""

    def __init__(self):
        self.context = StreamContext.NONE
        self.buffer = ""

    def feed(self, token: str) -> list[ParsedToken]:
        """Feed a token and return parsed tokens with types."""
        self.buffer += token
        results = []

        while True:
            if self.context == StreamContext.NONE:
                # Look for opening tags
                match = re.search(r'<(thinking|answer)>', self.buffer)
                if match:
                    # Emit any untagged content as "thinking" (fallback)
                    prefix = self.buffer[:match.start()].strip()
                    if prefix:
                        results.append(ParsedToken(prefix, "thinking"))

                    tag = match.group(1)
                    self.context = StreamContext(tag)
                    self.buffer = self.buffer[match.end():]
                else:
                    break  # Wait for more tokens

            else:
                # Look for closing tag
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

    def flush(self) -> list[ParsedToken]:
        """Call at stream end to emit any remaining buffer."""
        results = []
        if self.buffer.strip():
            # Default to thinking if outside tags, otherwise use current context
            emit_type = self.context.value if self.context != StreamContext.NONE else "thinking"
            results.append(ParsedToken(self.buffer, emit_type))
        self.buffer = ""
        self.context = StreamContext.NONE
        return results
```

### 3. System Prompt Addition

```python
THINKING_ANSWER_INSTRUCTION = """
## Output Format

You MUST structure ALL your responses using these tags:

<thinking>
Use this for your internal reasoning, planning, and analysis.
This includes: interpreting the question, deciding which tools to use,
analyzing results, and any intermediate thoughts.
</thinking>

<answer>
Use this for the final response to show the user.
This is what gets displayed in the chat interface.
Keep it clear, concise, and user-friendly.
</answer>

Example:
<thinking>
The user wants to know the count of cooperatives in Jakarta.
I'll query the database using the geography dimension filtered by province.
</thinking>
<answer>
Jumlah koperasi di Jakarta adalah 14.

**Saran Tindak Lanjut:**
- Analisis per wilayah
- Tren waktu
</answer>
"""
```

## Fallback Behavior

| Scenario | Behavior |
|----------|----------|
| Content before any tag | Emit as `thinking` |
| Unclosed `<thinking>` at stream end | Emit as `thinking` |
| Unclosed `<answer>` at stream end | Emit as `answer` |
| No tags at all | Everything emits as `thinking` |

## Files to Modify

| File | Action | Changes |
|------|--------|---------|
| `app/modules/autonomous_agent/service.py` | MODIFY | Add `TagStreamParser`, update `_process_event()`, remove regex heuristics |
| `app/utils/prompts/agent_prompts.py` | MODIFY | Add `THINKING_ANSWER_INSTRUCTION` |
| `app/modules/autonomous_agent/prompts.py` | MODIFY | Append tag instructions to agent prompt |

### Code to Remove

From `service.py`:
- `_answer_start_regex` class variable
- `_get_answer_start_regex()` method
- `_is_final_answer_content()` method
- Buffer-based heuristics in `_process_event()`

### Code to Add

- `TagStreamParser` class (~60 lines)
- Tag instruction constant (~25 lines)
- Updated `_process_event()` using parser (~20 lines)

## Integration with _process_event

```python
class AutonomousAgentService:
    def __init__(self, ...):
        # ... existing init ...
        self._tag_parser = TagStreamParser()

    def _process_event(self, event: dict) -> dict | list:
        """Process LangGraph event for streaming."""
        event_type = event.get("event")

        if event_type == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                # Feed token to parser
                parsed_tokens = self._tag_parser.feed(chunk.content)

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

                return results if results else None

        # ... handle other event types unchanged ...
```

## Benefits

| Before (Regex) | After (Tag-based) |
|----------------|-------------------|
| Fragile pattern matching | Explicit LLM marking |
| False negatives for new patterns | Works for any language/format |
| Maintenance burden | Zero maintenance |
| Guessing game | Deterministic parsing |

## Non-Goals

- CLI REPL behavior unchanged
- Tool event handling unchanged (`tool_start`, `tool_end`)
- Session/graph structure unchanged

## Testing Plan

1. Unit test `TagStreamParser` with various token sequences
2. Test fallback behavior (untagged content, unclosed tags)
3. Integration test with actual LLM streaming
4. Verify CLI REPL still works unchanged
