"""
memory.py — Token-bounded short-term memory.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Callable, List, Optional

from autourgos_memory import BaseMemory, MemoryMessage


def _default_token_estimator(text: Optional[str]) -> int:
    """Estimate tokens. Uses tiktoken if installed, otherwise a heuristic."""
    if not text:
        return 0
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text, disallowed_special=()))
    except Exception:
        pass
    # Unicode-aware heuristic
    total = 0.0
    for ch in text:
        o = ord(ch)
        if (0x4E00 <= o <= 0x9FFF or 0x3040 <= o <= 0x309F or
                0x30A0 <= o <= 0x30FF or 0x1100 <= o <= 0x11FF or
                0xAC00 <= o <= 0xD7AF):
            total += 1.5
        elif ch in ('{', '}', '[', ']', '"', "'", ':', ',', ';', '=', '+', '-', '*', '/', '<', '>', '&', '|', '^', '%'):
            total += 0.5
        else:
            total += 0.25
    return max(1, int(total))


class TokenBufferedMemory(BaseMemory):
    """Short-term memory bounded by maximum token count.

    Oldest messages are evicted from the front whenever the total token
    count exceeds ``max_tokens``. Optionally uses ``tiktoken`` for accurate
    counts; falls back to a character-based heuristic if not installed.

    Parameters
    ----------
    max_tokens : int
        Token budget. Default 2000.
    token_estimator : callable, optional
        Custom ``(text: str) -> int`` estimator. Defaults to tiktoken / heuristic.
    """

    def __init__(
        self,
        max_tokens: int = 2000,
        token_estimator: Optional[Callable[[str], int]] = None,
    ) -> None:
        if not isinstance(max_tokens, int) or max_tokens < 1:
            raise ValueError("max_tokens must be an integer >= 1")
        self.max_tokens      = max_tokens
        self.token_estimator = token_estimator or _default_token_estimator
        self._messages: List[MemoryMessage] = []
        self._total_tokens = 0
        self._lock = threading.RLock()

    def _msg_tokens(self, msg: MemoryMessage) -> int:
        return self.token_estimator(msg.role) + self.token_estimator(msg.content)

    def _enforce_limit(self) -> None:
        while self._messages and self._total_tokens > self.max_tokens:
            removed = self._messages.pop(0)
            self._total_tokens -= self._msg_tokens(removed)

    def add_message(self, role: str, content: str, timestamp: Optional[datetime] = None) -> MemoryMessage:
        with self._lock:
            msg = MemoryMessage(role=role, content=content, timestamp=timestamp or datetime.now(timezone.utc))
            self._messages.append(msg)
            self._total_tokens += self._msg_tokens(msg)
            self._enforce_limit()
            return msg

    def add_user_message(self, content: str) -> MemoryMessage:
        return self.add_message("user", content)

    def add_agent_message(self, content: str) -> MemoryMessage:
        return self.add_message("agent", content)

    def add_tool_message(self, tool_name: str, result: str) -> MemoryMessage:
        return self.add_message("tool", f"[{tool_name} returned]: {result}")

    def get_messages(self) -> List[MemoryMessage]:
        with self._lock:
            return list(self._messages)

    @property
    def total_tokens(self) -> int:
        with self._lock:
            return self._total_tokens

    def format_for_llm(self, query: Optional[str] = None) -> str:
        with self._lock:
            if not self._messages:
                return ""
            lines = "\n".join(f"[{m.timestamp.isoformat()}] {m.role}: {m.content}" for m in self._messages)
            return f"\n--- Previous Conversation Context ---\n{lines}\n--------------------------------------\n"

    def clear(self) -> None:
        with self._lock:
            self._messages.clear()
            self._total_tokens = 0
