"""
autourgos-token-memory — Token-bounded short-term memory for Autourgos agents.

    from autourgos_token_memory import TokenBufferedMemory

Install with tiktoken for accurate counts::

    pip install 'autourgos-token-memory[tiktoken]'
"""
from .memory import TokenBufferedMemory, _default_token_estimator

from autourgos_core import package_version

__version__ = package_version("autourgos-token-memory", fallback="2.0.5")

__all__ = ["TokenBufferedMemory"]
