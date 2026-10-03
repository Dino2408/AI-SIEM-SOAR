class ToolGateway:
    """Deterministic allowlisted tool boundary; arbitrary shell is never exposed."""
    def __init__(self, registry, audit_logger=None, permissions=None):
        from .permission_manager import PermissionManager
        self.registry = registry
        self.audit = audit_logger
        self.permissions = permissions or PermissionManager()

    def call(self, agent: str, name: str, args=None):
        args = args or {}
        spec = self.registry.get(name)
        decision = self.permissions.check(agent, name, spec)
        if not decision.allowed:
            if self.audit:
                self.audit.write({"event_id":"tool-denied","event":"tool_denied","agent":agent,"tool":name,"reason":decision.reason})
            raise PermissionError(decision.reason)
        try:
            result = spec.handler(args)
            if self.audit:
                self.audit.write({"event_id":"tool-call","event":"tool_call","agent":agent,"tool":name,"success":True})
            return result
        except Exception as exc:
            if self.audit:
                self.audit.write({"event_id":"tool-error","event":"tool_error","agent":agent,"tool":name,"success":False,"error":str(exc)})
            raise
