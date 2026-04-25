# Pythonic Code Reference

Detailed anti-patterns and idiomatic replacements.

## Anti-Patterns Table

| # | Unpythonic | Pythonic | Notes |
|---|---|---|---|
| 1 | `result = []; [result.append(x) for x in data]` | `result = [x for x in data]` | List comprehension |
| 2 | `result = []; for x in data: if cond(x): result.append(x)` | `result = [x for x in data if cond(x)]` | Filter in comprehension |
| 3 | `flag = False; [cond(x) and set(flag=True)]` | `flag = any(cond(x) for x in data)` | `any` / `all` |
| 4 | `all(cond(x) for x in data) == False` | `not any(cond(x) for x in data)` | De Morgan |
| 5 | `i = 0; for x in data: ...; i += 1` | `for i, x in enumerate(data): ...` | `enumerate` |
| 6 | `for i in range(len(seq)):` | `for x in seq:` or `for i, x in enumerate(seq)` | Avoid index iteration |
| 7 | `if len(seq) > 0:` | `if seq:` | Truthiness |
| 8 | `if len(seq) == 0:` | `if not seq:` | Negated truthiness |
| 9 | `if val != None:` | `if val is not None:` | Identity vs equality |
| 10 | `if val == None:` | `if val is None:` | Identity vs equality |
| 11 | `for key in dict.keys():` | `for key in dict:` | Iterate dict directly |
| 12 | `for val in dict.values():` | `for val in dict.values():` | Already correct, but prefer `dict.items()` when both needed |
| 13 | `for k, v in dict.items():` | `for k, v in dict.items():` | Correct — use when iterating k,v |
| 14 | `result = map(str, items)` (consumed once) | `result = [str(x) for x in items]` | Materialize lazy iterator |
| 15 | `result = filter(cond, items)` | `result = [x for x in items if cond(x)]` | Clarity; or use itertools |
| 16 | `sorted_items = items[:]; sorted_items.sort()` | `sorted_items = sorted(items)` | `sorted` returns new list |
| 17 | `os.path.join(a, b)` where a, b are `Path` | `Path(a) / b` | `pathlib` |
| 18 | `os.path.exists(path)` | `pathlib.Path(path).exists()` | `pathlib` |
| 19 | `os.path.isfile(path)` | `pathlib.Path(path).is_file()` | `pathlib` |
| 20 | `glob.glob("*.py")` | `pathlib.Path(".").glob("*.py")` | `pathlib` |
| 21 | `with open(path) as f: data = f.read().splitlines()` | `data = pathlib.Path(path).read_text().splitlines()` | One-liner |
| 22 | `result = []; for item in data: result.extend(item.subitems)` | `result = [sub for item in data for sub in item.subitems]` | Nested comprehension |
| 23 | `if "key" in dict and dict["key"] == val:` | `if dict.get("key") == val:` | `dict.get` with default |
| 24 | `if "key" in dict: dict.pop(key)` | `dict.pop(key, None)` | Avoids KeyError |
| 25 | `subprocess.run(["cmd"])` without `check=True` | `subprocess.run(["cmd"], check=True)` | Propagate errors |
| 26 | `except:` | `except SomeException:` | Specific exceptions |
| 27 | `except Exception:` | Specific subclass | `ValueError`, `KeyError`, etc. |
| 28 | `except E: raise E` | `raise` (re-raise) | Shorter |
| 29 | `except E: raise E(msg) from e` | `raise E(msg) from e` | Use explicit chaining |
| 30 | `while True: x = get(); if x: break` | `x = next(iter(get() for _ in itertools.count() if x))` or refactor | Avoids infinite loop pattern |
| 31 | `lambda x: x.field` | `operator.attrgetter("field")` | For `sorted`/`min`/`max` with multiple keys |
| 32 | `lambda x: x[0]` | `itemgetter(0)` | For sorted/min/max by index |
| 33 | `result = {}; [result.update({k: v}) for k, v in items]` | `result = dict(items)` | Dict from pairs |
| 34 | `or` chaining with `None` | `x or y or z` where each may be None | Works for falsy non-None too |
| 35 | `datetime.datetime.now()` for comparisons | `datetime.datetime.now()` or `time.monotonic()` | Know your timezone intent |
| 36 | `random.random()` for IDs | `uuid.uuid4()` | No collision risk |
| 37 | `"|".join(list_of_strings)` | `"|".join(list_of_strings)` | Already correct — don't split then join |
| 38 | `x = x + ""` to convert to string | `str(x)` | Explicit |
| 39 | `type(x) == int` | `isinstance(x, int)` | Works for subclasses |
| 40 | `hasattr(obj, "field")` then `getattr` | `getattr(obj, "field", default)` | EAFP over LBYL |

## Walrus Operator (`:=`)

Use sparingly. Good when assignment and use are co-located:

```python
# Good: avoids repeating the expression
if (match := pattern.search(data)) is not None:
    print(match.group(0))

# Bad: just assign, walrus adds noise
(y := x + 1)

# Bad: assignment far from use
if condition:
    data = compute()
process(data)
```

## EAFP vs LBYL

**LBYL** (Look Before You Leap) — check before acting:

```python
if key in my_dict:
    value = my_dict[key]
```

**EAFP** (Easier to Ask Forgiveness than Permission):

```python
try:
    value = my_dict[key]
except KeyError:
    ...
```

EAFP is preferred when the key is *usually* present (common case), or when atomicity matters. LBYL is preferred when the condition is genuinely uncertain and checking is much cheaper than handling the exception.

## Dataclasses

Use `dataclasses` for simple state aggregation instead of `__init__` boilerplate:

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

## Context Managers

All resource management should use context managers:

```python
# Good
with open("file.txt") as f:
    data = f.read()

# Bad — file handle may leak
f = open("file.txt")
data = f.read()
f.close()
```

For multi-step setup/teardown:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    acquire()
    try:
        yield resource
    finally:
        release()
```

## Type Hint Cheat Sheet

```python
from collections.abc import Sequence, Iterable, Callable
from typing import Any, Union

def f(x: Sequence[str]) -> list[str]: ...
def g(x: Iterable[int]) -> None: ...
def h(x: Callable[[int, str], bool]) -> Union[int, None]: ...
def i(x: Any) -> None: ...  # avoid Any
```
