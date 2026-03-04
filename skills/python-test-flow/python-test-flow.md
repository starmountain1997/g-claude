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
3. Run `vulture` to detect dead code
4. Run autoflake, ruff format, isort (via `scripts/python-formatter.sh`)
5. Run pytest to execute tests

## Usage

Run the script from the project root:

```zsh
zsh ~/.claude/skills/python-test-flow/scripts/python-formatter.sh $ARGUMENTS
```

## Supporting Scripts

- `scripts/python-formatter.sh` - 执行 autoflake, ruff format, isort

## Requirements

- ruff, vulture, autoflake, isort, pytest must be installed
