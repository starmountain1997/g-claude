---
name: python-test-flow
description: Run Python test flow: ruff check, basedpyright, vulture, autoflake+format+isort, then pytest
disable-model-invocation: true
---

# Python Test Flow

Execute a full quality check on Python code. If no directory is provided via $ARGUMENTS, use the current directory.

## Workflow

1. **Linting**: Run `ruff check` on the target directory.
2. **Type Checking**: Run `basedpyright` on the target directory.
3. **Dead Code**: Run `vulture` to detect dead code.
4. **Formatting**: Execute the bundled formatter script:
   ```bash
   zsh ${CLAUDE_SKILL_DIR}/scripts/python-formatter.sh $ARGUMENTS
   ```
5. **Testing**: Run `pytest` on the target directory.

## Supporting Resources

- For details on tools used, see [reference.md](reference.md)
