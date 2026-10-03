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

def _script(name, timeout=900):
    allowed={"bootstrap":"scripts/bootstrap_stack.sh","stop":"scripts/stop_stack.sh","smoke":"scripts/stack_smoke_test.sh"}
    if name not in allowed:
        raise PermissionError("unknown stack operation")
    p=subprocess.run(["bash",str(ROOT/allowed[name])],cwd=ROOT,env=os.environ.copy(),text=True,capture_output=True,timeout=timeout)
    return {"operation":name,"returncode":p.returncode,"stdout":p.stdout[-20000:],"stderr":p.stderr[-20000:]}

def _ollama_health(_args):
    import shutil
    return {"installed": bool(shutil.which("ollama"))}

def _ai_health(_args):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=5) as r:
            return {"status": r.status, "body": json.loads(r.read().decode())}
    except Exception as exc:
        return {"status": 0, "error": str(exc)}

def _ai_audit(args):
    url="http://127.0.0.1:8080/v1/audit"
    with urllib.request.urlopen(url, timeout=5) as r:
        data=json.loads(r.read().decode())
    if args.get("limit") is not None:
        data["records"]=data.get("records",[])[-int(args["limit"]):]
    return data

def build_default_registry():
    r = ToolRegistry()
    all_agents = ("architect", "developer", "devops", "validator")
    r.register(ToolSpec("filesystem.read", all_agents, _read, False, "Read repository text"))
    r.register(ToolSpec("filesystem.list", all_agents, _list, False, "List repository entries"))
    r.register(ToolSpec("testing.run", ("devops", "validator"), _run, True, "Run local argv-only test command"))
    r.register(ToolSpec("stack.bootstrap", ("devops",), lambda a: _script("bootstrap"), True, "Start the pinned integrated Docker stack"))
    r.register(ToolSpec("stack.stop", ("devops",), lambda a: _script("stop"), True, "Stop the integrated Docker stack"))
    r.register(ToolSpec("stack.smoke_test", ("devops", "validator"), lambda a: _script("smoke", 300), True, "Run the integrated stack smoke test"))
    r.register(ToolSpec("stack.health", ("devops", "validator"), _ai_health, False, "Query the project AI gateway health"))
    r.register(ToolSpec("ai.audit", ("devops", "validator"), _ai_audit, False, "Read audited AI decisions"))
    r.register(ToolSpec("ollama.health", all_agents, _ollama_health, False, "Check local Ollama executable"))
    return r
