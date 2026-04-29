---
name: pythonic-code
description: Review Python code for idiomatic style and apply refactors. Use this skill whenever you need to refactor Python code, review code for Pythonic patterns, fix anti-patterns, simplify verbose code, or improve readability. Trigger especially when code uses range(len()), manual index tracking, list.append() in loops, len() for truthiness checks, manual file handling without context managers, or dict operations that could use defaultdict or dict.get().
license: MIT
---

# Pythonic Code Review

Review Python for idiomatic style and apply targeted refactors. Flag common anti-patterns and replace with Pythonic alternatives.

## Core Principles

1. **Readability over cleverness** — clear > clever; if you need a comment to explain it, reconsider
1. **Built-ins over boilerplate** — enumerate, zip, itertools, dataclasses, contextlib
1. **EAFP over LBYL** — `try/except` is preferred when the happy path dominates
1. **Flat over nested** — flatten with early returns, comprehensions, or helper functions
1. **Single responsibility** — functions do one thing; if "and" appears in the function purpose, split it

## Review Workflow

When reviewing selected code:

1. **Scan for anti-patterns** — use the table in [reference.md](reference.md) as a checklist
1. **Identify the unpythonic pattern** — name it so the fix is clear
1. **Show before/after inline** — make the change visible, don't just rewrite
1. **Apply surgical edits** — prefer targeted fixes over rewrites; keep diffs small
1. **Verify equivalence** — the refactored code must behave identically

## Common Anti-Patterns (High-Frequency)

These come up constantly — always flag them:

| Flag this | Replace with |
|---|---|
| `for i in range(len(seq))` | `for x in seq` or `for i, x in enumerate(seq)` |
| `result = []; [result.append(x) for x in seq]` | `[x for x in seq]` |
| `if len(seq) > 0:` | `if seq:` |
| `if val != None:` | `if val is not None:` |
| `for k in dict.keys():` | `for k in dict:` |
| `with open(path) as f: data = f.read().splitlines()` | `Path(path).read_text().splitlines()` |
| `flag = False; [... and set(flag=True)]` | `any(cond(x) for x in seq)` |
| `if key in dict: dict.pop(key)` | `dict.pop(key, None)` |
| `subprocess.run(["cmd"])` without `check=True` | `check=True` or explicit exception handling |
| `except:` | `except SpecificException:` |

## When Applying Fixes

**Surgical over wholesale** — edit only the problematic lines. Don't rewrite entire functions unless the whole function is anti-pattern.

**Before/after in comments** — show what changed:

```python
# BEFORE: range(len()) anti-pattern
# for i in range(len(users)):
#     user = users[i]
#     if user.id == user_id:
#         return users[i]

# AFTER: direct iteration
for user in users:
    if user.id == user_id:
        return user
```

**Explain the why** — don't just fix, educate:

```python
return next((user for user in users if user.id == user_id), None)
# Why: next() with default is cleaner than manual loop + None return
```

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

## Walrus Operator (:=) — Use Judiciously

The walrus operator is powerful but easily abused. **Good uses:**

```python
# Assignment and use are co-located, avoids repeating expression
if (match := pattern.search(data)) is not None:
    print(match.group(0))

# Loop variable bound once, used in body
while (line := file.readline()):
    process(line)
```

**Bad uses — avoid:**

```python
# Just assigning — walrus adds noise
(y := x + 1)

# Assignment far from use — obscures control flow
if condition:
    data = compute()
process(data)  # User has to scroll up to find where data came from
```

When in doubt, use explicit assignment. The walrus operator excels when it eliminates a duplicate expression; it's a liability when it replaces simple assignment.

## EAFP vs LBYL

**LBYL** (Look Before You Leap) — check before acting:

```python
if key in my_dict:
    value = my_dict[key]  # Key guaranteed to exist
```

**EAFP** (Easier to Ask Forgiveness than Permission):

```python
try:
    value = my_dict[key]
except KeyError:
    # Handle missing key
```

**When to use EAFP:** Key is usually present (common case), atomicity matters, checking is expensive.

**When to use LBYL:** Condition is genuinely uncertain, checking is cheap, you need different behavior for missing vs present.

## Dataclasses

Use dataclasses for simple state containers instead of `__init__` boilerplate:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# frozen=True for immutable/hashable
@dataclass(frozen=True)
class Config:
    host: str
    port: int
```

For full anti-pattern coverage, see [reference.md](reference.md).
