from pathlib import Path
from orchestrator.local_tools import build_default_registry
from orchestrator.permission_manager import PermissionManager
from orchestrator.tool_gateway import ToolGateway
from orchestrator.audit_logger import AuditLogger

ROOT = Path(__file__).resolve().parents[1]

def test_registry_and_permissions(tmp_path):
    gw = ToolGateway(build_default_registry(), AuditLogger(tmp_path), PermissionManager())
    assert "testing.run" in gw.registry.names()
    assert gw.call("architect","filesystem.read",{"path":str(ROOT/"README.md")}).startswith("# AI-SIEM-SOAR")

def test_denies_wrong_agent(tmp_path):
    gw = ToolGateway(build_default_registry(), AuditLogger(tmp_path), PermissionManager())
    try:
        gw.call("architect","testing.run",{"command":["python","-V"]})
        assert False
    except PermissionError:
        pass
