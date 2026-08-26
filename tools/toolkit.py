"""Tools your agents can use. Add more as needed."""
import os
from typing import Dict, Any


class Toolkit:
    """Sandboxed tools for your agents."""

    @staticmethod
    def search_web(query: str) -> str:
        """Search the web using DuckDuckGo (no API key needed)."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                return "\n".join([f"{r['title']}: {r['body']}" for r in results])
        except ImportError:
            return "[Install duckduckgo-search: pip install duckduckgo-search]"

    @staticmethod
    def read_file(path: str) -> str:
        """Read a file from the project directory."""
        safe_path = os.path.abspath(path)
        project_root = os.path.abspath(".")
        if not safe_path.startswith(project_root):
            return "[ERROR: Access denied - path outside project]"
        try:
            with open(safe_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"[ERROR: {str(e)}]"

    @staticmethod
    def write_file(path: str, content: str) -> str:
        """Write a file - REQUIRES HITL APPROVAL."""
        return f"[PENDING APPROVAL] Write {len(content)} chars to {path}"

    @staticmethod
    def execute_sandbox(command: str) -> str:
        """Execute a command in a Docker sandbox - REQUIRES HITL APPROVAL."""
        return f"[PENDING APPROVAL] Execute: {command}"

    @staticmethod
    def get_available_tools() -> Dict[str, Any]:
        return {
            "search_web": {
                "description": "Search the web for information",
                "risk": "green",
                "params": {"query": "string"}
            },
            "read_file": {
                "description": "Read a file from the project",
                "risk": "green",
                "params": {"path": "string"}
            },
            "write_file": {
                "description": "Write content to a file",
                "risk": "yellow",
                "params": {"path": "string", "content": "string"}
            },
            "execute_sandbox": {
                "description": "Execute a command in sandboxed environment",
                "risk": "red",
                "params": {"command": "string"}
            }
        }
