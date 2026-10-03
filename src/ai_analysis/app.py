from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os, uuid
from datetime import datetime, timezone
from pathlib import Path
import requests

OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL","http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL","").strip()
SHUFFLE_WEBHOOK_URL=os.getenv("SHUFFLE_WEBHOOK_URL","").strip()
AUDIT_FILE=Path(os.getenv("AI_AUDIT_FILE","/data/audit.jsonl"))
DRY_RUN=os.getenv("AI_DRY_RUN","false").lower()=="true"
ALLOWED_PLAYBOOKS={"none","notify_only","collect_context","isolate_host","disable_account"}
HIGH_IMPACT={"isolate_host","disable_account"}

def now():
    return datetime.now(timezone.utc).isoformat()

def append_audit(record):
    AUDIT_FILE.parent.mkdir(parents=True,exist_ok=True)
    with AUDIT_FILE.open("a",encoding="utf-8") as f:
        f.write(json.dumps(record,ensure_ascii=False)+"\n")

def evidence_from_alert(alert):
    r=alert.get("rule",{}) if isinstance(alert,dict) else {}
    a=alert.get("agent",{}) if isinstance(alert,dict) else {}
    out=[]
    for label,path,value in [
        ("rule.id","rule.id",r.get("id")),
        ("rule.level","rule.level",r.get("level")),
        ("rule.description","rule.description",r.get("description")),
        ("rule.groups","rule.groups",r.get("groups")),
        ("agent.id","agent.id",a.get("id")),
        ("agent.name","agent.name",a.get("name")),
        ("timestamp","timestamp",alert.get("timestamp")),
        ("location","location",alert.get("location")),
    ]:
        if value not in (None,"",[],{}):
            out.append({"field":path,"value":value,"source":"wazuh_alert","label":label})
    return out

def deterministic_severity(level):
    try: level=int(level)
    except Exception: level=0
    if level>=12: return "critical"
    if level>=10: return "high"
    if level>=7: return "medium"
    if level>=4: return "low"
    return "informational"

def bounded_playbook(level, groups):
    try: level=int(level)
    except Exception: level=0
    groups=set(groups or [])
    if level>=12 or "authentication_failures" in groups or "syscheck" in groups:
        return "collect_context"
    if level>=7:
        return "notify_only"
    return "none"

def call_ollama(alert, context):
    if DRY_RUN:
        return {"status":"BLOCKED","reason":"AI_DRY_RUN=true"}
    if not OLLAMA_MODEL:
        return {"status":"BLOCKED","reason":"OLLAMA_MODEL is not configured"}
    prompt={
        "role":"SOC incident analyst",
        "rules":[
            "Use only facts present in the supplied Wazuh alert/context.",
            "Do not invent evidence, IPs, users, processes, timestamps or actions.",
            "Return JSON only.",
            "Recommend only one of: none, notify_only, collect_context, isolate_host, disable_account.",
            "Treat isolate_host and disable_account as high-impact and never claim they were executed."
        ],
        "alert":alert,
        "related_context":context,
        "required":{"attack_hypothesis":"string","recommended_playbook":"string","confidence":"number 0..1","rationale":"string"}
    }
    resp=requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model":OLLAMA_MODEL,"stream":False,"format":"json",
              "messages":[
                  {"role":"system","content":"You are a defensive SOC analyst. Never fabricate evidence. Output JSON only."},
                  {"role":"user","content":json.dumps(prompt,ensure_ascii=False)}
              ]},
        timeout=90)
    resp.raise_for_status()
    data=resp.json()
    content=data.get("message",{}).get("content","")
    result=json.loads(content)
    return {"status":"SUCCESS","result":result}

def analyze(payload):
    alert=payload.get("alert",payload)
    context=payload.get("related_context",[])
    rule=alert.get("rule",{}) if isinstance(alert,dict) else {}
    level=rule.get("level",0)
    groups=rule.get("groups",[]) or []
    audit_id=str(uuid.uuid4())
    model_result=call_ollama(alert,context)
    evidence=evidence_from_alert(alert)
    severity=deterministic_severity(level)
    policy_playbook=bounded_playbook(level,groups)
    llm_playbook=None
    hypothesis="No LLM hypothesis available."
    confidence=0.0
    rationale="Deterministic policy selected the response class from Wazuh rule metadata."
    if model_result.get("status")=="SUCCESS":
        llm=model_result.get("result",{})
        llm_playbook=llm.get("recommended_playbook")
        hypothesis=str(llm.get("attack_hypothesis",""))
        confidence=float(llm.get("confidence",0.0) or 0.0)
        rationale=str(llm.get("rationale",""))
        if llm_playbook not in ALLOWED_PLAYBOOKS:
            llm_playbook="none"
    chosen=policy_playbook
    if llm_playbook in {"notify_only","collect_context"} and policy_playbook!="none":
        chosen=llm_playbook
    if llm_playbook in HIGH_IMPACT:
        rationale += " LLM requested a high-impact action; policy gate rejected autonomous execution."
    policy={
        "allowed": chosen not in HIGH_IMPACT,
        "requires_human_approval": chosen in HIGH_IMPACT,
        "selected_playbook": chosen,
        "reason":"High-impact actions are never executed autonomously; selected playbooks are allowlisted."
    }
    execution={"attempted":False,"result":"not_requested"}
    if chosen in {"notify_only","collect_context"} and SHUFFLE_WEBHOOK_URL:
        try:
            r=requests.post(SHUFFLE_WEBHOOK_URL,json={
                "source":"AI-SIEM-SOAR","audit_id":audit_id,"alert":alert,
                "analysis":{"severity":severity,"hypothesis":hypothesis,"confidence":confidence},
                "playbook":chosen,"policy":policy
            },timeout=15)
            execution={"attempted":True,"result":"submitted","http_status":r.status_code}
        except Exception as exc:
            execution={"attempted":True,"result":"failed","error":str(exc)}
    result={
        "status":"SUCCESS" if model_result.get("status")=="SUCCESS" else "BLOCKED",
        "audit_id":audit_id,
        "incident_summary":rule.get("description","Wazuh security alert"),
        "severity_assessment":{"level":severity,"wazuh_rule_level":level,"rationale":rationale},
        "evidence":evidence,
        "attack_hypothesis":hypothesis,
        "recommended_playbook":chosen,
        "response_arguments":{"alert_id":alert.get("id"),"agent_id":(alert.get("agent") or {}).get("id")},
        "confidence":max(0.0,min(1.0,confidence)),
        "policy_decision":policy,
        "execution":execution
    }
    append_audit({"timestamp":now(),"audit_id":audit_id,"input_alert_id":alert.get("id"),"decision":result})
    return result

class Handler(BaseHTTPRequestHandler):
    def json(self,code,obj):
        body=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path=="/health":
            return self.json(200,{"status":"ok","service":"ai-analysis","model":OLLAMA_MODEL or None,"ollama":OLLAMA_BASE_URL})
        if self.path=="/v1/audit":
            rows=[]
            if AUDIT_FILE.exists():
                rows=[json.loads(x) for x in AUDIT_FILE.read_text(encoding="utf-8").splitlines() if x.strip()]
            return self.json(200,{"count":len(rows),"records":rows[-100:]})
        return self.json(404,{"error":"not_found"})
    def do_POST(self):
        if self.path not in ("/v1/analyze","/v1/webhook/wazuh"):
            return self.json(404,{"error":"not_found"})
        try:
            n=int(self.headers.get("Content-Length","0")); payload=json.loads(self.rfile.read(n))
            return self.json(200,analyze(payload))
        except Exception as exc:
            return self.json(400,{"status":"FAILURE","error":str(exc)})
    def log_message(self,*args): pass

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",8080),Handler).serve_forever()
