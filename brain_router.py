"""Brain Router - Decides which AI model handles each task."""
import os
import json
import time
from datetime import date
from typing import Dict
from config import Config


class BrainRouter:
    """
    Routes tasks to the right AI brain based on:
    - Task type (coding, research, sensitive data)
    - Privacy needs (local vs cloud)
    - Cost budget (daily limits per brain)
    - Complexity (simple vs hard reasoning)
    """

    def __init__(self):
        self.budget_file = "./memory/brain_budgets.json"
        self._load_budgets()
        self.last_call_time = 0
        self.min_delay = 1.0  # Rate limit: 1 second between API calls

    def _load_budgets(self):
        """Track daily spending per brain."""
        if os.path.exists(self.budget_file):
            with open(self.budget_file, 'r') as f:
                self.budgets = json.load(f)
        else:
            self.budgets = {}

    def _save_budgets(self):
        """Save budget tracking."""
        os.makedirs("./memory", exist_ok=True)
        with open(self.budget_file, 'w') as f:
            json.dump(self.budgets, f, indent=2)

    def get_today_key(self):
        return str(date.today())

    def get_spent_today(self, brain: str) -> float:
        today = self.get_today_key()
        if today not in self.budgets:
            self.budgets[today] = {}
        return self.budgets[today].get(brain, 0.0)

    def record_cost(self, brain: str, cost_usd: float):
        today = self.get_today_key()
        if today not in self.budgets:
            self.budgets[today] = {}
        self.budgets[today][brain] = self.budgets[today].get(brain, 0.0) + cost_usd
        self._save_budgets()

    def is_over_budget(self, brain: str, limit: float) -> bool:
        return self.get_spent_today(brain) >= limit

    def global_kill_switch(self) -> bool:
        """Check if total daily spending hit the absolute ceiling."""
        total = sum(
            self.get_spent_today(b) for b in ["claude", "codex", "openai"]
        )
        return total >= Config.DAILY_BUDGET_TOTAL

    def analyze_task(self, task: str) -> Dict:
        task_lower = task.lower()
        coding_keywords = [
            "code", "script", "program", "build", "debug", "fix",
            "function", "api", "deploy", "app", "website", "scrape",
             "bot", "integration", "database", "server"
        ]
        sensitive_keywords = [
            "password", "secret", "key", "token", "financial",
            "bank", "wallet", "crypto", "ssn", "private", "confidential",
            "customer data", "email list", "revenue", "income", "tax"
        ]
        complex_keywords = [
            "strategy", "plan", "analyze", "compare", "evaluate",
            "research", "market", "competitor", "business model",
            "optimize", "forecast", "predict", "trend"
        ]
        simple_keywords = [
            "summarize", "short", "brief", "quick", "simple",
            "format", "convert", "list", "count"
        ]
        return {
            "is_coding": any(kw in task_lower for kw in coding_keywords),
            "is_sensitive": any(kw in task_lower for kw in sensitive_keywords),
            "is_complex": any(kw in task_lower for kw in complex_keywords),
            "is_simple": any(kw in task_lower for kw in simple_keywords),
        }

    def route(self, task: str, force_brain: str = None) -> Dict:
        analysis = self.analyze_task(task)

        if force_brain:
            return self._get_brain_config(force_brain, "User forced selection")

        # EMERGENCY: Global kill switch
        if self.global_kill_switch():
            return self._get_brain_config("ollama", "GLOBAL KILL SWITCH: Daily budget exceeded - forcing local model")

        BUDGETS = {
            "codex": Config.DAILY_BUDGET_CODEX,
            "claude": Config.DAILY_BUDGET_CLAUDE,
            "ollama": 0.0
        }

        # RULE 1: Sensitive data -> ALWAYS local
        if analysis["is_sensitive"]:
            if self._is_ollama_available():
                return self._get_brain_config("ollama", "Sensitive task - local model for privacy")
            return self._get_brain_config("claude", "Sensitive task but Ollama unavailable")

        # RULE 2: Coding -> Codex (if budget allows)
        if analysis["is_coding"]:
            if not self.is_over_budget("codex", BUDGETS["codex"]):
                return self._get_brain_config("codex", "Coding task - Codex is best")
            elif not self.is_over_budget("claude", BUDGETS["claude"]):
                return self._get_brain_config("claude", "Coding task but Codex over budget")
            else:
                return self._get_brain_config("ollama", "Coding task but all budgets spent")
            

        # RULE 3: Complex reasoning -> Claude
        if analysis["is_complex"] and not analysis["is_simple"]:
            if not self.is_over_budget("claude", BUDGETS["claude"]):
                return self._get_brain_config("claude", "Complex reasoning - Claude is best")
            elif not self.is_over_budget("codex", BUDGETS["codex"]):
                return self._get_brain_config("codex", "Complex task but Claude over budget")
            else:
                return self._get_brain_config("ollama", "Complex task but budgets spent")

        # RULE 4: Simple tasks -> Ollama
        if analysis["is_simple"] and self._is_ollama_available():
            return self._get_brain_config("ollama", "Simple task - local model is fast and free")

        # RULE 5: Default -> Claude
        if not self.is_over_budget("claude", BUDGETS["claude"]):
            return self._get_brain_config("claude", "General task - defaulting to Claude")
        elif not self.is_over_budget("codex", BUDGETS["codex"]):
            return self._get_brain_config("codex", "General task but Claude over budget")
        else:
            return self._get_brain_config("ollama", "All cloud budgets spent - using local")

    def _is_ollama_available(self) -> bool:
        try:
            import requests
            response = requests.get("http://localhost:11434", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _get_brain_config(self, brain: str, reason: str) -> Dict:
        configs = {
            "ollama": {
                "brain": "ollama",
                "reason": reason,
                "estimated_cost": 0.0,
                "model_id": Config.LOCAL_MODEL,
                "provider": "ollama",
                "base_url": Config.OLLAMA_BASE_URL
            },
            "claude": {
                "brain": "claude",
                "reason": reason,
                "estimated_cost": 0.02,
                "model_id": "~anthropic/claude-sonnet-latest",                 "provider": "openrouter",
                "base_url": Config.OPENROUTER_BASE_URL,
                "api_key": Config.OPENROUTER_API_KEY
            },
            "codex": {
                "brain": "codex",
                "reason": reason,
                "estimated_cost": 0.05,
                "model_id": "gpt-4o",
                "provider": "openai",
                "base_url": "https://api.openai.com/v1",
                "api_key": Config.OPENAI_API_KEY
            }
        }
        return configs.get(brain, configs["claude"])

    def get_budget_report(self) -> str:
        today = self.get_today_key()
        if today not in self.budgets:
            return "No spending today."
        lines = [f"Brain Budget Report ({today})"]
        for brain, spent in self.budgets[today].items():
            limits = {"codex": Config.DAILY_BUDGET_CODEX, "claude": Config.DAILY_BUDGET_CLAUDE, "ollama": 0.0}
            limit = limits.get(brain, 10.0)
            pct = (spent / limit * 100) if limit > 0 else 0
            lines.append(f"  {brain}: ${spent:.2f} / ${limit:.2f} ({pct:.0f}%)")
        return "\n".join(lines)
