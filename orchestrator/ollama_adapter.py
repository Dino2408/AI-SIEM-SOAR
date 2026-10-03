import requests

class OllamaAdapter:
    def __init__(self, base_url="http://127.0.0.1:11434", model=None, timeout=120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
    def health(self):
        r = requests.get(self.base_url + "/api/tags", timeout=5)
        r.raise_for_status()
        return r.json()
    def chat(self, messages, model=None, options=None):
        selected = model or self.model
        if not selected:
            raise ValueError("No Ollama model configured")
        payload = {"model": selected, "messages": messages, "stream": False}
        if options:
            payload["options"] = options
        r = requests.post(self.base_url + "/api/chat", json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()
