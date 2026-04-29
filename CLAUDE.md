# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **Claude Code plugin marketplace** — it distributes skills for Ascend NPU workflows (quantization, inference, evaluation) and structured Git commits. Users install from this repo with `claude plugin install <skill>@starmountain1997/g-claude`.

## Architecture

```
.claude-plugin/marketplace.json   # Marketplace catalog — lists plugins with source pointers
plugins/                          # Plugin directories
  <name>/
    .claude-plugin/plugin.json    # Plugin manifest — version, description, skill paths
    skills/<name>/SKILL.md        # Skill entry point
    skills/<name>/reference.md    # Optional detailed reference
    skills/<name>/scripts/        # Optional scripts
scripts/bump-skill-versions.py   # Pre-commit hook: auto-increments version in plugin.json when plugins/ changes
```

## Skill Authoring

Skills follow the standard Claude Code skill format: a `SKILL.md` file with YAML frontmatter (`name`, `description`, `argument-hint`, `disable-model-invocation`, etc.) in a directory named after the skill. See the [Plugins documentation](https://code.claude.com/docs/en/plugins) for frontmatter fields, argument substitution, and dynamic context injection syntax.

## Pre-commit Hooks

The `bump-skill-versions` hook runs before every commit — it diffs `plugins/` against HEAD, bumps the patch version in each changed plugin's `.claude-plugin/plugin.json`, then stages the updated file. This ensures version history reflects what actually changed.

Other hooks: `mdformat` (markdown), `ruff-format` (Python).

## Skill Pipeline

```
ascend          → NPU health check, env setup (starting point)
  ├── vllm-ascend        → vLLM install, serve, offline validation
  ├── msmodelslim        → model quantization (W4A8/W8A8/W4A4)
  │     └── msmodeling  → throughput/latency simulation
  ├── model-download     → ModelScope / HuggingFace download
  └── aisbench          → accuracy (GSM8K, MMLU, AIME) and performance benchmarks
```

## Common Commands

```bash
# Install/update all skills (from repo root)
python install-g-claude.py --update

# Run pre-commit hooks manually
pre-commit run --all-files

# Stage and commit a plugin change (version bump happens automatically via hook)
git add plugins/<name>/ && git commit
```
