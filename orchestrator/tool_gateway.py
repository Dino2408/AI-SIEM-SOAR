class ToolGateway:
    """Allowlisted tool boundary; arbitrary shell is forbidden."""
    def __init__(self,registry=None): self.registry=registry or {}
    def call(self,name,args=None):
        if name not in self.registry: raise PermissionError(f"Tool not allowlisted: {name}")
        return self.registry[name](args or {})
