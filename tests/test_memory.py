"""Tests for TokenBufferedMemory."""
import logging

import pytest

from autourgos_token_memory.memory import TokenBufferedMemory, _default_token_estimator


def _count_tokens(mem: TokenBufferedMemory, text: str) -> int:
    return mem.token_estimator(text)


def test_add_and_get_messages_normal():
    mem = TokenBufferedMemory(max_tokens=1000)
    mem.add_user_message("hello")
    mem.add_agent_message("hi there")
    msgs = mem.get_messages()
    assert isinstance(msgs, list)
    assert [m.role for m in msgs] == ["user", "agent"]
    assert [m.content for m in msgs] == ["hello", "hi there"]


def test_eviction_respects_token_limit():
    # Each message costs a fixed 2 tokens (role + content). With a budget of
    # 5, at most 2 messages (4 tokens) can be retained before the oldest is
    # evicted to make room for a new one.
    mem = TokenBufferedMemory(max_tokens=5, token_estimator=lambda t: 1)
    mem.add_user_message("first")
    mem.add_user_message("second")
    mem.add_user_message("third")
    msgs = mem.get_messages()
    assert msgs[-1].content == "third"
    assert mem.total_tokens <= 5
    assert "first" not in [m.content for m in msgs]


def test_eviction_order_is_fifo():
    mem = TokenBufferedMemory(max_tokens=6, token_estimator=lambda t: 1)
    mem.add_user_message("a")
    mem.add_user_message("b")
    mem.add_user_message("c")
    mem.add_user_message("d")
    msgs = mem.get_messages()
    contents = [m.content for m in msgs]
    # Oldest messages should have been evicted first (FIFO), newest retained.
    assert contents == sorted(contents, key=lambda c: "abcd".index(c))
    assert "d" in contents


def test_get_messages_returns_list_type_and_clear_works():
    mem = TokenBufferedMemory(max_tokens=1000)
    mem.add_user_message("x")
    assert isinstance(mem.get_messages(), list)
    mem.clear()
    assert mem.get_messages() == []
    assert mem.total_tokens == 0


def test_default_token_estimator_import_error_is_silent(monkeypatch, caplog):
    # Simulate tiktoken not being installed: should fall back silently,
    # no warning logged.
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "tiktoken":
            raise ImportError("no tiktoken")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with caplog.at_level(logging.WARNING, logger="autourgos_token_memory"):
        result = _default_token_estimator("hello world")
    assert result > 0
    assert not any(r.name == "autourgos_token_memory" for r in caplog.records)


def test_oversized_single_message_is_kept_and_warns(caplog):
    # A message whose token count alone exceeds max_tokens must not be
    # silently dropped; it should be kept and a warning logged.
    mem = TokenBufferedMemory(max_tokens=5, token_estimator=lambda t: 10)
    with caplog.at_level(logging.WARNING, logger="autourgos_token_memory.memory"):
        mem.add_user_message("this single message is huge")
    msgs = mem.get_messages()
    assert len(msgs) == 1
    assert msgs[0].content == "this single message is huge"
    assert any("exceeds max_tokens budget by itself" in r.message for r in caplog.records)
