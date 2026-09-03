# autourgos-token-memory — Features

Token-bounded short-term memory for Autourgos agents. Keeps messages in RAM and evicts the oldest ones once the total token count exceeds a configured budget, using `tiktoken` for accurate counts when installed, or a fast character-based heuristic when it isn't.

## Full Feature List

### Core behavior
- **`TokenBufferedMemory`** — eviction is based on token budget (`max_tokens`), not message count, which is a better proxy for what actually overflows an LLM's context window
- Oldest messages evicted first (FIFO) once the budget is exceeded
- `memory.total_tokens` exposes live current usage for inspection

### Token counting
- **`tiktoken` support (optional extra)** — accurate `cl100k_base` encoding, correct for GPT-3.5/4/4o-family tokenization when the `tiktoken` extra is installed (`pip install 'autourgos-token-memory[tiktoken]'`)
- **Unicode-aware heuristic fallback** when `tiktoken` isn't installed — roughly 0.25 tokens/ASCII character, ~1.5 tokens/CJK character, so it's not a naive whitespace-split count
- **Custom token estimator** — any `(text: str) -> int` callable can be swapped in, e.g. word-count or a different tokenizer entirely

### Dependencies
- No hard dependency — `tiktoken` is an optional extra, not required to use the package

---

## Competitor Comparison

The direct comparison set is other token-bounded/window conversation buffers in agent frameworks, since this package's entire scope is "evict by token budget" rather than semantic retrieval or summarization.

| Capability | **autourgos-token-memory** | LangChain `ConversationTokenBufferMemory` | LangChain `ConversationBufferWindowMemory` | LlamaIndex `ChatMemoryBuffer` |
|---|---|---|---|---|
| Eviction basis | Token count | Token count (`max_token_limit`) | Message count (`k` most recent) | Token count |
| Accurate tokenizer support | Yes, via optional `tiktoken` extra | Yes, via `tiktoken` (tied to the configured LLM) | N/A (message-count based) | Yes, via a configurable tokenizer function |
| Fallback when no tokenizer is installed | Unicode-aware heuristic (ASCII/CJK-weighted) | Falls back to a rough word-based estimate depending on LLM wrapper | N/A | Typically requires a tokenizer to be specified |
| Custom token estimator | Yes, any `(text) -> int` callable | Indirect — depends on which LLM object is passed | N/A | Yes, `tokenizer_fn` param |
| Provider/LLM coupling | None — pure counting utility, no LLM object required | Requires a LangChain `BaseLanguageModel` instance (for its `get_num_tokens`) | Requires a LangChain chain, but no tokenizer coupling | Loosely coupled to LlamaIndex's chat engine abstractions |
| Framework lock-in | None — standalone, plugs into any Autourgos `Agent` | Tied to LangChain's memory interfaces (also being deprecated in favor of LangGraph) | Same | Tied to LlamaIndex |
| Setup complexity | `pip install`, optional extra for exact counts | `pip install langchain` + an LLM object | `pip install langchain` | `pip install llama-index` |
| Persistence across restarts | No — in-memory (RAM) only, per the README | No | No | No |

### How to read this

- **vs. LangChain's `ConversationTokenBufferMemory`**: the closest direct analog — both bound by tokens rather than message count. The difference is coupling: LangChain's version needs a `BaseLanguageModel` instance to compute token counts, while this package is a standalone counting utility with `tiktoken` as an optional extra and a documented, testable heuristic fallback (not just "assume 4 chars/token"). It's also worth noting LangChain's classic memory classes are on a deprecation path toward LangGraph-based persistence, whereas this package has no such dependency to inherit that churn from.
- **vs. `ConversationBufferWindowMemory`-style (message-count) windows**: message count is a weak proxy for context-window usage — ten short messages and ten long ones consume very different amounts of context. Token-budget eviction (this package's whole premise) is strictly more accurate for the actual failure mode (context overflow).
- **vs. LlamaIndex's `ChatMemoryBuffer`**: conceptually similar (token-bounded, custom tokenizer support), but tied into LlamaIndex's broader chat-engine machinery rather than usable standalone.
- **What this package doesn't do**: no persistence (RAM-only, by design per its own README), no retrieval/relevance ranking, no summarization of evicted messages — it's a narrow, single-purpose eviction primitive meant to compose with other Autourgos memory packages (e.g. wrap it, or pair token budgeting with `autourgos-summary-memory`'s compression instead of pure eviction) rather than a general memory system.

Sources:
- [ConversationTokenBufferMemory | langchain_classic | LangChain Reference](https://reference.langchain.com/python/langchain-classic/memory/token_buffer/ConversationTokenBufferMemory)
- [langchain.memory.token_buffer.ConversationTokenBufferMemory — LangChain 0.2.17 docs](https://api.python.langchain.com/en/latest/memory/langchain.memory.token_buffer.ConversationTokenBufferMemory.html)
- [Conversational Memory with LangChain for LLMs | Medium](https://medium.com/@nisargmehta1406/conversational-memory-with-langchain-for-llms-14bca1993102)
- [How to Implement LangChain Memory](https://oneuptime.com/blog/post/2026-01-27-langchain-memory/view)
