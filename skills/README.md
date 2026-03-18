# Claude Skills Repository

A collection of specialized skills for extending Claude Code's capabilities.

## Skills

### [Ascend Toolchain](./ascend/SKILL.md)
- **vLLM-Ascend**: Installation and execution on Ascend NPUs.
- **msmodelslim**: Quantization protocols, expert MoE strategies, and advanced configuration guides.
- **NPU Usage**: Debugging and status monitoring.

### [Commit-as-Prompt](./commit-as-prompt/SKILL.md)
- Generates and refines commit messages based on staged changes and reference styles.
- Supports custom context and examples for stylistic consistency.

### [Python Test Flow](./python-test-flow/SKILL.md)
- Specialized workflow for running, fixing, and formatting Python tests.
- Includes automatic script execution for linting and formatting.

## Usage

These skills are automatically discovered by Claude Code when placed in `.claude/skills/` or when manually added. Refer to each skill's `SKILL.md` for specific instructions and available supporting files.
