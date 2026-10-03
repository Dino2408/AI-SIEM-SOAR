"""Minimal Orchestrator entry point."""
from .state_manager import StateManager
from .message_manager import MessageManager
from .agent_manager import AgentManager

def main():
    state=StateManager(".ai/state/workflow.json")
    messages=MessageManager(".ai/messages")
    agents=AgentManager("agents")
    print({"state":state.load(),"agents":agents.list_agents(),"messages":messages.list_messages()})

if __name__=="__main__": main()
