from dataclasses import dataclass, field
from typing import Callable, Any, Tuple, Dict


@dataclass
class ToolSpec:
    name: str
    build: Callable[[], Any]
    description: str


@dataclass
class SubAgentSpec:
    """Specification for a subagent in the Deep Agent hierarchy."""
    name: str
    description: str
    tools: Tuple[str, ...]
    system_prompt: str
    interrupt_on: Dict[str, bool] = field(default_factory=dict)
