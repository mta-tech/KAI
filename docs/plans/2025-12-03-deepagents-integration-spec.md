# Deepagents Integration Specification

**Date:** 2025-12-03
**Type:** Integration Guide
**Audience:** Internal Dev Team
**Status:** Draft

## Overview

This specification describes how to integrate agentic-learning's memory injection capabilities with [deepagents](https://github.com/langchain-ai/deepagents) - LangChain's agent harness for complex agentic tasks.

**Integration Approach:** Transparent SDK Interception
**Supported Providers:** Anthropic, OpenAI, Gemini
**Language:** Python

---

## 1. Architecture

The integration works because of the layered architecture where LangChain chat models are thin wrappers around provider SDKs:

```
┌─────────────────────────────────────────────────────────┐
│                    User Application                      │
├─────────────────────────────────────────────────────────┤
│  learning() context manager ← agentic-learning          │
├─────────────────────────────────────────────────────────┤
│  deepagents.create_deep_agent()                         │
│      └── agent.invoke() / agent.ainvoke()               │
├─────────────────────────────────────────────────────────┤
│  LangChain Abstraction Layer                            │
│      └── ChatAnthropic / ChatOpenAI / ChatGoogleGenAI   │
├─────────────────────────────────────────────────────────┤
│  SDK Layer (INTERCEPTED HERE)                           │
│      ├── anthropic.messages.create()                    │
│      ├── openai.chat.completions.create()               │
│      └── google.generativeai.generate_content()         │
├─────────────────────────────────────────────────────────┤
│  Letta Memory Server                                    │
└─────────────────────────────────────────────────────────┘
```

**Key Insight:** The existing agentic-learning interceptors patch at the SDK level, automatically capturing all LangChain calls without any code changes to deepagents.

---

## 2. Integration Pattern

### Basic Usage

Wrap deepagents invocations in the `learning()` context manager:

```python
from agentic_learning import learning, AgenticLearning
from deepagents import create_deep_agent

# 1. Create clients
letta_client = AgenticLearning(base_url="http://localhost:8283")
agent = create_deep_agent(
    system_prompt="You are a helpful assistant.",
)

# 2. Sync usage
with learning(agent="deepagent-user-123", client=letta_client):
    result = agent.invoke({
        "messages": [{"role": "user", "content": "My name is Alice"}]
    })

# 3. Async usage
async with learning(agent="deepagent-user-123", client=letta_client):
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "What's my name?"}]
    })
    # Memory injected → Agent knows "Alice"
```

### What Happens Under the Hood

1. `learning()` installs interceptors (once per process)
2. `agent.invoke()` triggers LangChain → SDK call
3. Interceptor retrieves memory from Letta
4. Memory injected into `system` parameter
5. Response captured and saved to Letta

---

## 3. Provider-Specific Configuration

### Anthropic (Default)

```python
from deepagents import create_deep_agent

agent = create_deep_agent()  # defaults to claude-sonnet-4-5-20250929
# Memory injected into: kwargs['system']
```

### OpenAI

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

model = init_chat_model("openai:gpt-4o")
agent = create_deep_agent(model=model)
# Memory injected into: messages[0] as system message
```

### Gemini

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

model = init_chat_model("google-genai:gemini-2.0-flash")
agent = create_deep_agent(model=model)
# Memory injected into: contents parameter
```

### Memory Injection Points Summary

| Provider | Interceptor | Injection Target |
|----------|-------------|------------------|
| Anthropic | `AnthropicInterceptor` | `system` parameter |
| OpenAI | `OpenAIInterceptor` | System message in `messages[]` |
| Gemini | `GeminiInterceptor` | `contents` parameter |

---

## 4. Memory Format & Configuration

### Memory Block Format

Memory is injected into the system prompt as XML:

```xml
<memory_blocks>
The following memory blocks are currently engaged:
<human>
<description>Stores information about the user</description>
<value>User name is Alice. Works on Python projects. Prefers concise answers.</value>
</human>
<context>
<description>Current session context</description>
<value>Discussing deepagents integration with agentic-learning.</value>
</context>
</memory_blocks>
```

### Configuration Options

```python
# Full configuration
with learning(
    agent="deepagent-user-123",      # Agent identifier in Letta
    client=letta_client,              # AgenticLearning client
    capture_only=False,               # False = inject + capture, True = capture only
    memory=["human", "context"],      # Memory block labels to use
):
    result = agent.invoke(...)

# Capture-only mode (no memory injection, just save conversations)
with learning(agent="my-agent", client=letta_client, capture_only=True):
    result = agent.invoke(...)
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `LETTA_BASE_URL` | Letta server URL (default: http://localhost:8283) |
| `DEBUG_AGENTIC_LEARNING` | Set to `1` for detailed logging |

---

## 5. Complete Example

```python
import asyncio
from agentic_learning import learning, AgenticLearning
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

# Setup
letta_client = AgenticLearning(base_url="http://localhost:8283")

# Create agent with custom tools
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

agent = create_deep_agent(
    model=init_chat_model("anthropic:claude-sonnet-4-20250514"),
    system_prompt="You are a research assistant with memory.",
    tools=[search_web],
)

async def chat(user_id: str, message: str) -> str:
    """Chat with memory persistence per user."""
    async with learning(agent=f"deepagent-{user_id}", client=letta_client):
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": message}]
        })
        return result["messages"][-1].content

# Usage
async def main():
    # First conversation - establishes memory
    await chat("alice", "I'm working on a machine learning project in PyTorch")

    # Later conversation - memory is injected
    response = await chat("alice", "What framework am I using?")
    print(response)  # Knows about PyTorch from memory

asyncio.run(main())
```

### Error Handling

The interceptors handle errors gracefully - LLM calls never fail due to memory issues:

```python
# Graceful degradation - if Letta is unavailable, calls proceed without memory
with learning(agent="my-agent", client=letta_client):
    # If memory retrieval fails: warning logged, call continues
    # If save fails: warning logged, response still returned
    result = agent.invoke(...)
```

---

## 6. Limitations & Caveats

### Known Limitations

| Limitation | Description | Workaround |
|------------|-------------|------------|
| Streaming chunks | Memory saved after stream completes, not per-chunk | Use non-streaming for real-time saves |
| Subagent isolation | Subagents share parent's `learning()` context | Use separate agent IDs if needed |
| Context window | Memory injection adds tokens to system prompt | Monitor token usage, prune memory blocks |
| Summarization middleware | deepagents' `SummarizationMiddleware` may truncate injected memory | Place critical memory at end of block |

### Important Caveats

#### 1. Interceptor Installation is Global

Once installed, ALL SDK calls are intercepted (even outside `learning()` context, but no-op if no active context).

#### 2. Agent Naming

Use consistent agent names per user/session:

```python
# Good: deterministic agent ID
learning(agent=f"deepagent-{user_id}")

# Bad: random/changing agent ID (loses memory continuity)
learning(agent=f"deepagent-{uuid4()}")
```

#### 3. Async Context

Must use `async with` for async agent calls:

```python
# Wrong - sync context with async call
with learning(...):
    await agent.ainvoke(...)  # May lose context

# Correct
async with learning(...):
    await agent.ainvoke(...)
```

---

## 7. Related Files

### agentic-learning Interceptors

| File | Purpose |
|------|---------|
| `python/src/agentic_learning/core.py` | `learning()` context manager |
| `python/src/agentic_learning/interceptors/anthropic.py` | Anthropic SDK interceptor |
| `python/src/agentic_learning/interceptors/openai.py` | OpenAI SDK interceptor |
| `python/src/agentic_learning/interceptors/gemini.py` | Gemini SDK interceptor |
| `python/src/agentic_learning/client/memory/context.py` | Memory formatting |

### deepagents

| File | Purpose |
|------|---------|
| `libs/deepagents/deepagents/graph.py` | `create_deep_agent()` function |
| `libs/deepagents/deepagents/middleware/` | Built-in middleware |

---

## 8. Testing Checklist

- [ ] Verify Letta server is running at configured URL
- [ ] Test sync `agent.invoke()` with `learning()` context
- [ ] Test async `agent.ainvoke()` with `async learning()` context
- [ ] Verify memory injection by checking system prompt in debug logs
- [ ] Verify conversation capture by querying Letta API
- [ ] Test with each provider (Anthropic, OpenAI, Gemini)
- [ ] Test error handling when Letta is unavailable
- [ ] Test `capture_only=True` mode

---

## Appendix: How LangChain Calls SDKs

LangChain's chat models internally use the provider SDKs:

- `ChatAnthropic` → `anthropic.Anthropic().messages.create()`
- `ChatOpenAI` → `openai.OpenAI().chat.completions.create()`
- `ChatGoogleGenerativeAI` → `google.generativeai.GenerativeModel().generate_content()`

This is why transparent SDK interception works - we intercept at the lowest layer where all requests funnel through.
