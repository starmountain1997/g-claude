# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **Claude Code plugin marketplace** — it distributes skills for Ascend NPU workflows (quantization, inference, evaluation) and structured Git commits. Users install from this repo with `claude plugin install <skill>@starmountain1997/g-claude`.

## Architecture

```
.claude-plugin/marketplace.json   # Plugin catalog — version, description, skill paths for each plugin
skills/                           # Skill source directories
  <plugin>/SKILL.md               # Plugin entry point (referenced by marketplace.json)
  <plugin>/reference.md          # Optional detailed reference
  <plugin>/scripts/              # Optional scripts
scripts/bump-skill-versions.py   # Pre-commit hook: auto-increments version in marketplace.json when skills/ changes
```

## Skill Authoring

See `skills/CLAUDE.md` for skill structure, frontmatter fields, argument substitution, and dynamic context injection syntax.

## Pre-commit Hooks

The `bump-skill-versions` hook runs before every commit — it diffs `skills/` against HEAD, bumps the patch version in `marketplace.json` for any changed plugins, then stages the updated marketplace.json. This ensures version history reflects what actually changed.

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

# Stage and commit a skill change (version bump happens automatically via hook)
git add skills/<name>/ && git commit
```
