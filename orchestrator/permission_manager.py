from dataclasses import dataclass

@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str

class PermissionManager:
    def check(self, agent: str, tool_name: str, spec) -> PermissionDecision:
        if agent not in spec.agents:
            return PermissionDecision(False, f"Agent '{agent}' is not allowed to call '{tool_name}'")
        return PermissionDecision(True, "allowed")
