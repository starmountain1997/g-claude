# Python Test Flow Tools

This skill uses a suite of tools to ensure code quality and correctness.

## Tools Overview

- **ruff check**: Fast Python linter and code transformation tool.
- **basedpyright**: Static type checker for Python, a fork of pyright with stricter defaults.
- **vulture**: Finds unused code in Python programs.
- **autoflake**: Removes unused imports and variables.
- **ruff format**: Fast Python formatter, compatible with Black.
- **isort**: Sorts imports alphabetically and automatically separated into sections and by type.
- **pytest**: Framework that makes it easy to write small, readable tests.

## Recommended Workflow

1. **Linting**: Run `ruff check` first to catch obvious errors.
1. **Type Checking**: Run `basedpyright` to ensure type safety.
1. **Dead Code**: Use `vulture` to identify potentially unreachable code.
1. **Formatting**: Run the `python-formatter.sh` script to clean up imports and format code.
1. **Testing**: Finally, run `pytest` to verify logic.
