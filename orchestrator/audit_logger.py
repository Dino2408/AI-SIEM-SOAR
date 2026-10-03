import json
from pathlib import Path
from datetime import datetime, timezone
class AuditLogger:
    def __init__(self,directory): self.directory=Path(directory); self.directory.mkdir(parents=True,exist_ok=True)
    def write(self,event):
        event={"timestamp":datetime.now(timezone.utc).isoformat(),**event}
        (self.directory/(event.get("event_id","event")+".json")).write_text(json.dumps(event,indent=2),encoding="utf-8")
