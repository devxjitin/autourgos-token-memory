# autourgos-token-memory

Token-bounded short-term memory for [Autourgos](https://github.com/devxjitin) agents.

Keeps messages in RAM and evicts the oldest ones when the total token count exceeds a budget. Automatically uses `tiktoken` for accurate counts if installed, with a fast character-based heuristic as fallback.

---

## Install

```bash
pip install autourgos-token-memory

# For accurate tiktoken counts (recommended for OpenAI models)
pip install 'autourgos-token-memory[tiktoken]'
```

---

## Quick Start

```python
from autourgos_token_memory import TokenBufferedMemory
from autourgos_react_agent import ReactAgent

memory = TokenBufferedMemory(max_tokens=4000)
agent  = ReactAgent(llm=my_llm, memory=memory)
agent.invoke("Long conversation task...")
```

---

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `max_tokens` | int | `2000` | Token budget. Oldest messages evicted when exceeded. |
| `token_estimator` | callable | `None` | Custom `(text: str) -> int`. Defaults to tiktoken / heuristic. |

---

## Custom token estimator

```python
from autourgos_token_memory import TokenBufferedMemory

def my_estimator(text: str) -> int:
    return len(text.split())  # word count

memory = TokenBufferedMemory(max_tokens=500, token_estimator=my_estimator)
```

---

## Token counting

- **tiktoken installed**: uses `cl100k_base` encoding (accurate for GPT-3.5/4/4o).
- **tiktoken not installed**: Unicode-aware heuristic — ~0.25 tokens per ASCII char, ~1.5 per CJK character.

Check current usage:

```python
print(memory.total_tokens)  # → int
```

---

## Links

- PyPI: https://pypi.org/project/autourgos-token-memory/
- GitHub: https://github.com/devxjitin/autourgos-token-memory
- Issues: https://github.com/devxjitin/autourgos-token-memory/issues

---

## License

MIT — see [LICENSE](LICENSE)
