import json
from pathlib import Path
class StateManager:
    def __init__(self,path): self.path=Path(path)
    def load(self): return json.loads(self.path.read_text(encoding="utf-8"))
    def save(self,state): self.path.write_text(json.dumps(state,indent=2),encoding="utf-8")
