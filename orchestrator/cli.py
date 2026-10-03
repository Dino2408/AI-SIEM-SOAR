import argparse
import json
import os
from .paths import repo_path
from .state_manager import StateManager
from .message_manager import MessageManager
from .agent_manager import AgentManager
from .audit_logger import AuditLogger
from .local_tools import build_default_registry
from .permission_manager import PermissionManager
from .tool_gateway import ToolGateway
from .ollama_adapter import OllamaAdapter

def check():
    state = StateManager(repo_path(".ai/state/workflow.json"))
    messages = MessageManager(repo_path(".ai/messages"))
    agents = AgentManager(repo_path("agents"))
    audit = AuditLogger(repo_path(".ai/audit"))
    gw = ToolGateway(build_default_registry(), audit, PermissionManager())
    result = {
        "state": state.load().get("state"),
        "agents": agents.list_agents(),
        "messages": messages.list_messages(),
        "tools": gw.registry.names(),
        "ollama_installed": gw.call("architect","ollama.health")["installed"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))

def demo():
    audit = AuditLogger(repo_path(".ai/audit"))
    gw = ToolGateway(build_default_registry(), audit, PermissionManager())
    python = os.environ.get("PYTHON", "python")
    result = gw.call("devops","testing.run",{"command":[python,"-m","pytest","-q"]})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["returncode"] != 0:
        raise SystemExit(result["returncode"])

def ollama():
    data = OllamaAdapter(base_url=os.environ.get("OLLAMA_BASE_URL","http://127.0.0.1:11434")).health()
    print(json.dumps({"reachable":True,"models":[x.get("name") for x in data.get("models",[])]},indent=2,ensure_ascii=False))

def main():
    p = argparse.ArgumentParser(prog="ai-siem-soar")
    p.add_argument("command", choices=["check","demo","ollama"], nargs="?", default="check")
    args = p.parse_args()
    {"check":check,"demo":demo,"ollama":ollama}[args.command]()

if __name__ == "__main__":
    main()
