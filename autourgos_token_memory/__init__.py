"""
autourgos-token-memory — Token-bounded short-term memory for Autourgos agents.

    from autourgos_token_memory import TokenBufferedMemory

Install with tiktoken for accurate counts::

    pip install 'autourgos-token-memory[tiktoken]'
"""
from .memory import TokenBufferedMemory, _default_token_estimator

try:
    from importlib.metadata import version as _v
    __version__ = _v("autourgos-token-memory")
except Exception:
    __version__ = "1.0.2"

__all__ = ["TokenBufferedMemory"]
