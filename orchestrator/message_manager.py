from pathlib import Path
import json
class MessageManager:
    def __init__(self,directory): self.directory=Path(directory)
    def list_messages(self): return sorted(p.name for p in self.directory.glob("*.json"))
    def load(self,name): return json.loads((self.directory/name).read_text(encoding="utf-8"))
