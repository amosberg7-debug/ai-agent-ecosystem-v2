"""Episodic memory and skill registry for your agents."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
from config import Config


class MemoryStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.MEMORY_DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize SQLite tables for memory and skills."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT,
                    task TEXT,
                    actions TEXT,
                    outcome TEXT,
                    success BOOLEAN,
                    lessons TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    description TEXT,
                    code TEXT,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT,
                    action_type TEXT,
                    action_details TEXT,
                    approved_by TEXT,
                    decision TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_episode(self, agent_name: str, task: str, actions: list,
                     outcome: str, success: bool, lessons: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO episodes (agent_name, task, actions, outcome, success, lessons)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (agent_name, task, json.dumps(actions), outcome, success, lessons))
            conn.commit()

    def get_relevant_episodes(self, task: str, limit: int = 5) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM episodes
                WHERE task LIKE ? OR lessons LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{task}%", f"%{task}%", limit))
            return [dict(row) for row in cursor.fetchall()]

    def save_skill(self, name: str, description: str, code: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO skills (name, description, code)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    description=excluded.description,
                    code=excluded.code,
                    updated_at=CURRENT_TIMESTAMP
            """, (name, description, code))
            conn.commit()

    def get_skills(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM skills ORDER BY usage_count DESC")
            return [dict(row) for row in cursor.fetchall()]

    def log_audit(self, agent_name: str, action_type: str, action_details: str,
                  approved_by: str, decision: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_log (agent_name, action_type, action_details, approved_by, decision)
                VALUES (?, ?, ?, ?, ?)
            """, (agent_name, action_type, action_details, approved_by, decision))
            conn.commit()

    def get_stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            episodes = conn.execute("SELECT COUNT(*), AVG(success) FROM episodes").fetchone()
            skills = conn.execute("SELECT COUNT(*) FROM skills").fetchone()
            audits = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()
            return {
                "total_episodes": episodes[0],
                "success_rate": round((episodes[1] or 0) * 100, 2),
                "total_skills": skills[0],
                "total_decisions": audits[0]
            }
