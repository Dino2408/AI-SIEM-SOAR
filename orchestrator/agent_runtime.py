import json
from pathlib import Path
import yaml
from jsonschema import validate
from .artifact_store import ArtifactStore

class AgentRuntime:
    def __init__(self, root, gateway, audit, ollama):
        self.root = Path(root).resolve()
        self.gateway, self.audit, self.ollama = gateway, audit, ollama
        self.store = ArtifactStore(self.root)
        self.schema = json.loads((self.root / ".ai/contracts/agent_result.schema.json").read_text())

    def spec(self, agent_id):
        return yaml.safe_load((self.root / f"agents/{agent_id}/agent.yaml").read_text())

    def _json(self, content):
        content = content.strip()
        if content.startswith("MARKDOWN_FENCE"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1])
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start, end = content.find("{"), content.rfind("}")
            if start < 0 or end <= start:
                raise ValueError("agent did not return JSON")
            return json.loads(content[start:end+1])

    def run(self, agent_id, task, model, context):
        spec = self.spec(agent_id)
        prompt = (self.root / spec["system_prompt"]).read_text()
        system = prompt + "\n\nWORKFLOW CONTEXT:\n" + json.dumps(context, ensure_ascii=False, indent=2)
        system += "\n\nTASK:\n" + task + "\nReturn only the required JSON object."
        self.audit.write({"event_id": f"agent-start-{agent_id}", "event": "agent_start", "agent": agent_id})
        response = self.ollama.chat([{"role": "system", "content": system}], model=model, options={"temperature": 0.1})
        result = self._json(response["message"]["content"])
        validate(instance=result, schema=self.schema)
        allowed = tuple(spec["permissions"].get("write", []))
        for artifact in result["artifacts"]:
            self.store.write(artifact["path"], artifact["content"], allowed)
        for call in result["tool_calls"]:
            self.gateway.call(agent_id, call["tool"], call["args"])
        self.audit.write({"event_id": f"agent-end-{agent_id}", "event": "agent_end", "agent": agent_id, "status": result["status"], "summary": result["summary"]})
        return result
