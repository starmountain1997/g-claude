---
name: python-test-flow
description: Run Python test flow: ruff check, vulture, autoflake+format+isort, then pytest
disable-model-invocation: true
argument-hint: [directory]
allowed-tools: Bash(zsh *)
---

Run Python test flow on the project.

## Workflow

1. Find all Python files (excluding .venv)
2. Run `ruff check` to lint
3. Run `basedpyright` for type checking
4. Run `vulture` to detect dead code
5. Run autoflake, ruff format, isort (via `scripts/python-formatter.sh`)
6. Run pytest to execute tests

## Usage

Run the script from the project root:

```zsh
zsh ~/.claude/skills/python-test-flow/scripts/python-formatter.sh $ARGUMENTS
```

## Supporting Scripts

- `scripts/python-formatter.sh` - 执行 autoflake, ruff format, isort

## Requirements

- ruff, basedpyright, vulture, autoflake, isort, pytest must be installed
