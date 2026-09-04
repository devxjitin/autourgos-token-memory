# Changelog

## [2.1.0] - 2026-09-05

- Added: `TokenBufferedMemory.add_system_message()` (new — inherited from `autourgos-memory`'s `BaseMemory` default, didn't exist before).
- Internal: `TokenBufferedMemory` now uses `autourgos-memory`'s shared `add_message`-based defaults (removed duplicated `add_user_message`/`add_agent_message`/`add_tool_message` one-liners) and `format_conversation_banner()` (removed duplicated banner-building). Requires `autourgos-memory>=1.2.0`. No output change for existing methods.

## [2.0.5] - 2026-09-04

- Internal: `__version__` resolution moved to `autourgos_core.package_version()` (new `autourgos-core>=0.3.0` dependency). No functional change.

## [2.0.4] - 2026-09-03

- Added `features.md` documenting the module's feature set and a competitor comparison. No code changes.


## [2.0.3] - 2026-09-01

- Metadata: added `maintainers` (Sonia, Vishwanil Suman) to `pyproject.toml`,
  and linked the README's existing Sonia contributor badge to her GitHub
  profile (https://github.com/dahiyasonia). No code changes.

## [2.0.1] - 2026-07-27

- Fixed: standardized logger to logging.getLogger(__name__); a single message whose token count alone exceeds max_tokens is now kept (with a warning) instead of being silently evicted.

All notable changes to `autourgos-token-memory` are documented here.

---

## [2.0.0] - 2026-07-27

### Changed
- BREAKING: this package now depends on `autourgos-memory>=1.0.1` (previously zero-dependency). `BaseMemory`/`BaseRetriever`/`Document`/`MemoryMessage` are now re-exported from `autourgos-memory` instead of duplicated locally. No public API/behavior change for typical usage.

## [1.0.1] - 2026-07-27

### Fixed
- `__version__` fallback in `__init__.py` now matches `pyproject.toml` (was incorrectly `1.0.2`, now `1.0.0`).
- Wording correction: CHANGELOG previously referenced a non-existent `autourgos-core` package; now correctly states there is no dependency on `autourgos-memory` or any other Autourgos package.
- `TokenBufferedMemory` now stores messages in a `collections.deque` instead of a `list`, making oldest-message eviction in `_enforce_limit` O(1) instead of O(n). Public API (`get_messages()` return type, constructor signature) is unchanged.
- `_default_token_estimator` no longer silently swallows all exceptions from tiktoken. `ImportError`/`ModuleNotFoundError` (tiktoken not installed) still falls back silently as before; any other unexpected error now logs a warning via `logging.getLogger("autourgos_token_memory")` before falling back to the heuristic.

## [1.0.0] - 2026-06-17

### Added
- Initial release.
- Token-bounded short-term memory with tiktoken support.
- Self-contained package — no dependency on `autourgos-memory` or any other Autourgos package.
- All base interfaces (`BaseMemory`, `BaseRetriever`, `MemoryMessage`, `Document`) inlined.
- Thread-safe implementation using `threading.RLock`.
- Full type annotations and `py.typed` marker.

