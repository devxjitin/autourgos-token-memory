# autourgos-token-memory

[![Framework: Autourgos](https://img.shields.io/badge/Framework-Autourgos-orange.svg)](https://github.com/devxjitin)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://pypi.org/project/autourgos-token-memory/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/devxjitin/autourgos-token-memory/blob/main/LICENSE)
[![Author](https://img.shields.io/badge/Author-Jitin%20Kumar%20Sengar-blue.svg)](https://github.com/devxjitin)
[![Contributor](https://img.shields.io/badge/Contributor-Sonia-blueviolet.svg)](https://github.com/dahiyasonia)
[![Contributor](https://img.shields.io/badge/Contributor-Vishwanil%20Suman-blueviolet.svg)]()

Token-bounded short-term memory for [Autourgos](https://github.com/devxjitin) agents. Keeps messages in RAM
and evicts the oldest ones when the total token count exceeds a budget. Automatically uses `tiktoken` for
accurate counts if installed, with a fast character-based heuristic as fallback.

```python
from autourgos_token_memory import TokenBufferedMemory
from autourgos_agent import Agent
from autourgos_openaichat import OpenAIChatModel

my_llm = OpenAIChatModel(model="gpt-4o-mini")  # needs OPENAI_API_KEY set
memory = TokenBufferedMemory(max_tokens=4000)
agent  = Agent(llm=my_llm, memory=memory)
```

---

## Features

- **Token-budget eviction**, not message-count — a better proxy for what actually blows an LLM's context
- **`tiktoken` support (optional)** — accurate `cl100k_base` counts for GPT-3.5/4/4o when installed
- **Unicode-aware heuristic fallback** — ~0.25 tokens/ASCII char, ~1.5/CJK char when `tiktoken` isn't installed
- **Custom estimator** — swap in your own `(text: str) -> int` counter

---

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [Parameters](#parameters)
- [Custom Token Estimator](#custom-token-estimator)
- [Token Counting](#token-counting)
- [License](#license)

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
from autourgos_agent import Agent
from autourgos_openaichat import OpenAIChatModel

my_llm = OpenAIChatModel(model="gpt-4o-mini")  # needs OPENAI_API_KEY set
memory = TokenBufferedMemory(max_tokens=4000)
agent  = Agent(llm=my_llm, memory=memory)
agent.invoke("Long conversation task...")
```

---

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `max_tokens` | int | `2000` | Token budget. Oldest messages evicted when exceeded. |
| `token_estimator` | callable | `None` | Custom `(text: str) -> int`. Defaults to tiktoken / heuristic. |

---

## Custom Token Estimator

```python
from autourgos_token_memory import TokenBufferedMemory

def my_estimator(text: str) -> int:
    return len(text.split())  # word count

memory = TokenBufferedMemory(max_tokens=500, token_estimator=my_estimator)
```

---

## Token Counting

- **tiktoken installed**: uses `cl100k_base` encoding (accurate for GPT-3.5/4/4o).
- **tiktoken not installed**: Unicode-aware heuristic — ~0.25 tokens per ASCII char, ~1.5 per CJK character.

Check current usage:

```python
print(memory.total_tokens)  # → int
```

---

## License

Apache License 2.0, Copyright (c) 2026 Jitin Kumar Sengar
