from pathlib import Path
import json
from agent.tools.web_search import DuckDuckClient

class DuckDuckStub(DuckDuckClient):
    def search(self, query: str):
        fixture = Path(__file__).parent.parent / "fixtures" / "ddg_example.json"
        with open(fixture) as f:
            return [json.loads(f.read())]

