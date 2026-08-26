"""Configuration for your AI Agent Ecosystem."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # LLM Providers
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LOCAL_MODEL = os.getenv("LOCAL_MODEL", "codestral")

    # Agent
    AGENT_NAME = os.getenv("AGENT_NAME", "alpha")
    MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", "./memory/agent_memory.db")
    SKILLS_DIR = os.getenv("SKILLS_DIR", "./skills")
    HITL_ENABLED = os.getenv("HITL_ENABLED", "true").lower() == "true"

    # Budgets
    DAILY_BUDGET_CLAUDE = float(os.getenv("DAILY_BUDGET_CLAUDE", "10.0"))
    DAILY_BUDGET_CODEX = float(os.getenv("DAILY_BUDGET_CODEX", "5.0"))
    DAILY_BUDGET_TOTAL = float(os.getenv("DAILY_BUDGET_TOTAL", "20.0"))

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Risk tiers
    GREEN_ACTIONS = ["read_file", "search_web", "analyze_data", "draft_document"]
    YELLOW_ACTIONS = ["send_email", "commit_code", "update_crm", "scrape_website"]
    RED_ACTIONS = ["execute_production", "send_money", "delete_data", "modify_skills"]

    @classmethod
    def get_llm_config(cls):
        """Returns the active LLM configuration."""
        if cls.OPENROUTER_API_KEY:
            return {
                "provider": "openrouter",
                "api_key": cls.OPENROUTER_API_KEY,
                "base_url": cls.OPENROUTER_BASE_URL,
                "model": "anthropic/claude-3.5-sonnet-20241022"
            }
        elif cls.OPENAI_API_KEY:
            return {
                "provider": "openai",
                "api_key": cls.OPENAI_API_KEY,
                "model": "gpt-4o"
            }
        else:
            return {
                "provider": "ollama",
                "base_url": cls.OLLAMA_BASE_URL,
                "model": cls.LOCAL_MODEL
            }
