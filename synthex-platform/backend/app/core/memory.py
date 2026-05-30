"""
Synthex Conversation Memory
Short-term: In-memory dict (per session)
Long-term: File-based JSON (simple, no external DB needed for MVP)
Upgrade path: Pinecone / ChromaDB when ready
"""
import json
import os
from datetime import datetime
from typing import Optional
from app.utils.compression import compress_messages, estimate_tokens
from app.models.request import Message


MEMORY_DIR = "data/memory"
os.makedirs(MEMORY_DIR, exist_ok=True)


class ConversationMemory:
    """Per-user conversation memory with context compression."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.short_term: list[dict] = []  # Current session
        self.key_facts: list[str] = []
        self._load()

    def _path(self) -> str:
        return os.path.join(MEMORY_DIR, f"{self.user_id}.json")

    def _load(self):
        """Load long-term memory from disk."""
        try:
            if os.path.exists(self._path()):
                with open(self._path()) as f:
                    data = json.load(f)
                    self.key_facts = data.get("key_facts", [])
        except Exception:
            self.key_facts = []

    def save(self):
        """Persist key facts to disk."""
        try:
            with open(self._path(), "w") as f:
                json.dump({
                    "user_id": self.user_id,
                    "key_facts": self.key_facts[-50:],  # Keep last 50 facts
                    "updated_at": datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception:
            pass

    def add_message(self, role: str, content: str):
        self.short_term.append({"role": role, "content": content})

    def add_key_fact(self, fact: str):
        if fact and fact not in self.key_facts:
            self.key_facts.append(fact)
            self.save()

    def get_context_messages(self) -> list[Message]:
        """Get compressed messages for API call."""
        msgs = [Message(role=m["role"], content=m["content"]) for m in self.short_term]
        return compress_messages(msgs)

    def get_system_context(self) -> Optional[str]:
        """Build system prompt context from key facts."""
        if not self.key_facts:
            return None
        return f"Known context about this user:\n" + "\n".join(f"- {f}" for f in self.key_facts[-10:])

    def clear_session(self):
        self.short_term = []


# Simple session store (in-memory for MVP)
_sessions: dict[str, ConversationMemory] = {}


def get_memory(api_key_id: str) -> ConversationMemory:
    """Get or create memory for a user."""
    if api_key_id not in _sessions:
        _sessions[api_key_id] = ConversationMemory(api_key_id)
    return _sessions[api_key_id]
