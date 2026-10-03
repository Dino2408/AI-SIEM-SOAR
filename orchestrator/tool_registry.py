from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class ToolSpec:
    name: str
    agents: tuple[str, ...]
    handler: Callable[[dict], Any]
    side_effect: bool = False
    description: str = ""

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}
    def register(self, spec: ToolSpec):
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec
    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]
    def names(self):
        return sorted(self._tools)
