---
name: pythonic-code
description: Review Python code for idiomatic style and suggest improvements. Use when refactoring, reviewing Python code, or when code feels overly verbose or unpythonic.
license: MIT
---

# Pythonic Code Review

Review Python for idiomatic style and apply targeted refactors. Flag common anti-patterns and replace with Pythonic alternatives.

## Quick Principles

1. **Readability over cleverness** — clear > clever
1. **Flat over nested** — flatten nested conditionals and loops
1. **Built-ins over boilerplate** — use `enumerate`, `zip`, `itertools`, etc.
1. **EAFP over LBYL** — `try/except` for lookups and attribute access
1. **Single responsibility** — functions do one thing well

## Review Workflow

When reviewing selected code:

1. **Identify** the unpythonic pattern (see [reference.md](reference.md) for full table)
1. **Show** before/after inline so the change is clear
1. **Apply** only the specific refactor — avoid bundling unrelated changes
1. **Verify** the refactored code is equivalent and reads naturally

When applying fixes, prefer surgical edits over rewriting entire functions.

## Common Patterns

| Pattern | Flag when you see | Replace with |
|---|---|---|
| Loop append | `result = []; [result.append(x) for x in seq]` | `[x for x in seq]` |
| Flag setting | `flag = False; [cond(x) and set flag]` | `any(cond(x) for x in seq)` |
| Manual index | `i = 0; for x in seq: ...; i += 1` | `for i, x in enumerate(seq)` |
| Len check | `if len(seq) > 0:` | `if seq:` |
| None check | `if val != None:` | `if val is not None:` |
| Dict keys | `for k in dict.keys():` | `for k in dict:` |
| Subprocess | `subprocess.run(["cmd"]) without check=True` | `check=True` or specific exception |
| Bare except | `except:` | `except SomeException:` |
| os.path.join | `os.path.join(a, b)` for two Path objects | `Path(a) / b` |

For the full anti-pattern table and refactoring examples, see [reference.md](reference.md).

## Type Hints

Use `collections.abc` for generics, `typing` for complex signatures:

```python
from collections.abc import Sequence, Iterable
from typing import Any

def process(items: Sequence[str]) -> list[str]:
    return [x.strip() for x in items if x]
```

## Argument Substitution

$ARGUMENTS — when invoked with `/pythonic-code <path>`, use that path as the target.
