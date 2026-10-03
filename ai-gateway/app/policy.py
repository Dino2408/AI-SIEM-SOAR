from .config import AI_CONFIDENCE_THRESHOLD
from .schemas import Decision
APPROVED_AUTOMATION={"PB-BRUTEFORCE-BLOCK-IP"}
def apply_policy(decision:Decision)->bool:
    if decision.confidence<AI_CONFIDENCE_THRESHOLD or decision.playbook not in APPROVED_AUTOMATION or decision.severity=="critical" or decision.action!="block_source_ip":
        decision.requires_approval=True
        return False
    decision.requires_approval=False
    return True
