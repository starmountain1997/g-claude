---
name: python-with-uv
description: Set up a Python project with uv — use this skill whenever the user wants to start a new Python project, initialize a uv project, scaffold a Python package or app, or wire up a pre-commit + linting setup. Also use when an existing project needs uv mirror config, dev deps, or pre-commit installed.
disable-model-invocation: true
argument-hint: '[python-version]'
---

This skill initializes a new Python project (or brings an existing one up to standard) using `uv` with Aliyun mirror configuration, ruff-based linting/formatting, and a comprehensive pre-commit setup.

### Workflow

1. **Gather options** — if not provided as `$0`, ask:
   - Python version (e.g., `3.12`)
   - Project type: **app** (default, script/service) or **lib** (installable package, uses `--lib`)

2. **Initialize project** (skip if `pyproject.toml` already exists):
   - Run `uv init --python <version> [--lib]` — this also runs `git init` automatically.

3. **Configure Aliyun mirror** — append to `pyproject.toml`:
   ```toml
   [[tool.uv.index]]
   url = "https://mirrors.aliyun.com/pypi/simple"
   default = true
   ```

4. **Configure ruff** — append to `pyproject.toml` to enable import sorting and unused-import removal:
   ```toml
   [tool.ruff.lint]
   select = ["E", "F", "I"]
   ```

5. **Add development dependencies**:
   ```
   uv add ruff pytest radon vulture basedpyright pre-commit mdformat --dev
   ```

6. **Set up pre-commit**:
   - Create `.pre-commit-config.yaml` using [pre-commit-config.yaml](pre-commit-config.yaml) as the template.
   - Replace `$PYTHON_VERSION` with the confirmed version (e.g., `3.12`).
   - Run `pre-commit install` to register the git hooks.

7. **Finalize** — confirm to the user: Python version, mirror, dev tools installed, and pre-commit hooks active.

### Requirements

- `uv` must be installed on the system.
- The directory must be (or become) a git repo — `uv init` handles this for new projects; for existing projects without git, run `git init` before `pre-commit install`.
