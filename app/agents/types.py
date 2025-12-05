from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class ToolSpec:
    name: str
    build: Callable[[], Any]
    description: str
