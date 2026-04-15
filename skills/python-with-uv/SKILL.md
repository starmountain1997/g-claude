---
name: python-with-uv
description: Initializes and manages a Python project using uv. Performs 'uv init', configures Aliyun mirror, adds development dependencies, sets up pre-commit, and runs 'uv sync'.
disable-model-invocation: true
argument-hint: '[python-version]'
---

This skill initializes a new Python project or manages an existing one using `uv` with Aliyun mirror configuration and a comprehensive pre-commit setup.

### Workflow

1. **Confirm Python Version**:

   - If a Python version is provided as an argument ($0), use it.
   - If no argument is provided, ask the user: "What Python version do you want to use for this project? (e.g., 3.12)".

1. **Initialize Project**:

   - Run `uv init --python <version>` in the current directory to set up the project structure and `pyproject.toml`.

1. **Configure Aliyun Mirror**:

   Append the following configuration to `pyproject.toml` to use Aliyun as the default pip source:

   ```toml
   [[tool.uv.index]]
               url = "https://mirrors.aliyun.com/pypi/simple"
               default = true
   ```

1. **Add Development Dependencies**:

   - Run `uv add ruff autoflake isort pytest radon vulture basedpyright pre-commit mdformat --dev` to install standard development, linting, and formatting tools.

1. **Sync Dependencies**:

   - Run `uv sync` to ensure the virtual environment and `uv.lock` are fully synchronized.

1. **Setup Pre-commit Configuration**:

   - Create a `.pre-commit-config.yaml` file in the project root.
   - Use the content from [pre-commit-config.yaml](pre-commit-config.yaml) as a template.
   - **Important**: Replace `$PYTHON_VERSION` with the confirmed version (e.g., 3.12) and ensure any directory placeholders (like `./`) match the project structure.

1. **Initialize Pre-commit**:

   - Run `pre-commit install` to set up git hooks.

1. **Finalize**:

   - Inform the user that the project has been successfully initialized with the specified Python version, Aliyun mirror, development tools, and pre-commit hooks.

### Requirements

- `uv` must be installed on the system.
