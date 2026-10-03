from pathlib import Path
class AgentManager:
    def __init__(self,directory): self.directory=Path(directory)
    def list_agents(self): return sorted(p.name for p in self.directory.iterdir() if p.is_dir())
