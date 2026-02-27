"""
In-memory session store.  For production swap with Redis.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime


class SessionService:
    def __init__(self):
        self._sessions: dict[str, list[dict]] = defaultdict(list)

    def add_turn(self, session_id: str, role: str, content: str):
        self._sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])

    def clear(self, session_id: str):
        self._sessions.pop(session_id, None)

    def get_chat_pairs(self, session_id: str) -> list[dict]:
        """Return only role/content dicts suitable for the model."""
        return [
            {"role": t["role"], "content": t["content"]}
            for t in self._sessions.get(session_id, [])
        ]


session_service = SessionService()
