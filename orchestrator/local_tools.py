import json
import os
import subprocess
import urllib.request
from pathlib import Path
from .tool_registry import ToolRegistry, ToolSpec

ROOT = Path(__file__).resolve().parents[1]

def _safe(path):
    p = (ROOT / path).resolve()
    if ROOT not in p.parents and p != ROOT:
        raise PermissionError("path escapes repository")
    return p

def _read(args):
    p = _safe(args["path"])
    return {"path": args["path"], "content": p.read_text(encoding="utf-8")}

def _list(args):
    p = _safe(args.get("path", "."))
    return {"path": args.get("path", "."), "entries": sorted(str(x.relative_to(ROOT)) for x in p.iterdir())}

def _run(args):
    command = args["command"]
    if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
        raise ValueError("command must be an argv list")
    forbidden = {"sh", "bash", "zsh", "fish", "cmd", "powershell", "pwsh"}
    if Path(command[0]).name.lower() in forbidden:
        raise PermissionError("shell interpreters are forbidden")
    operators = ("&&", "||", ";", "|", ">", "<", "$(")
    if any(any(op in x for op in operators) for x in command):
        raise PermissionError("shell operators are forbidden")
    p = subprocess.run(command, cwd=ROOT, env=os.environ.copy(), text=True, capture_output=True, timeout=int(args.get("timeout", 300)))
    return {"command": command, "returncode": p.returncode, "stdout": p.stdout[-12000:], "stderr": p.stderr[-12000:]}

def _ollama_health(_args):
    import shutil
    return {"installed": bool(shutil.which("ollama"))}

def _siem_health(_args):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=5) as r:
            return {"status": r.status, "body": json.loads(r.read().decode())}
    except Exception as exc:
        return {"status": 0, "error": str(exc)}

def _siem_events(args):
    url = "http://127.0.0.1:8080/api/v1/events"
    if args.get("limit") is not None:
        url += "?limit=" + str(int(args["limit"]))
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.loads(r.read().decode())

def build_default_registry():
    r = ToolRegistry()
    all_agents = ("architect", "developer", "devops", "validator")
    r.register(ToolSpec("filesystem.read", all_agents, _read, False, "Read repository text"))
    r.register(ToolSpec("filesystem.list", all_agents, _list, False, "List repository entries"))
    r.register(ToolSpec("testing.run", ("devops", "validator"), _run, True, "Run local argv-only test command"))
    r.register(ToolSpec("siem.health", ("devops", "validator"), _siem_health, False, "Query local SIEM health"))
    r.register(ToolSpec("siem.events", ("devops", "validator"), _siem_events, False, "Query local SIEM events"))
    r.register(ToolSpec("ollama.health", all_agents, _ollama_health, False, "Check local Ollama executable"))
    return r
