import json
import os
from pathlib import Path

os.environ["AI_DRY_RUN"]="true"

from src.ai_analysis import app

def test_deterministic_analysis_is_bounded(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "AUDIT_FILE", tmp_path/"audit.jsonl")
    result=app.analyze({
        "alert":{
            "id":"test-1",
            "timestamp":"2026-10-03T00:00:00Z",
            "rule":{"id":"5710","level":10,"description":"Multiple authentication failures","groups":["authentication_failures"]},
            "agent":{"id":"001","name":"lab"}
        }
    })
    assert result["status"]=="BLOCKED"
    assert result["recommended_playbook"]=="collect_context"
    assert result["policy_decision"]["allowed"] is True
    assert result["execution"]["attempted"] is False
    assert Path(app.AUDIT_FILE).exists()
