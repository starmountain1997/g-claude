# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a Claude Code **skills collection** — a set of reusable skills that extend Claude's capabilities. Skills are prompt-based playbooks stored in directories, each with a `SKILL.md` entry point.

When authoring or editing skills, follow the patterns in `Extend Claude with skills.md` (the official Claude Code skills reference).

## Skill Structure

Each skill lives in its own directory:

```
skill-name/
├── SKILL.md          # Required: YAML frontmatter + markdown instructions
├── reference.md      # Optional: detailed reference loaded on demand
├── examples.md       # Optional: example outputs
└── scripts/          # Optional: scripts Claude can execute
```

`SKILL.md` must begin with YAML frontmatter between `---` markers, followed by markdown instructions.

## Key Frontmatter Fields

| Field | When to use |
| :--- | :--- |
| `name` | Slash-command name (lowercase, hyphens only, max 64 chars) |
| `description` | Required for auto-invocation; Claude uses this to decide when to load the skill |
| `disable-model-invocation: true` | Skills with side effects (deploy, commit) that only the user should trigger |
| `user-invocable: false` | Background knowledge Claude loads automatically but users shouldn't invoke |
| `context: fork` | Run the skill in an isolated subagent (no conversation history access) |
| `agent` | Subagent type to use with `context: fork` (e.g., `Explore`, `Plan`) |
| `allowed-tools` | Tools Claude can use without permission prompts while this skill is active |
| `argument-hint` | Autocomplete hint showing expected arguments (e.g., `[issue-number]`) |

## Argument Substitution

- `$ARGUMENTS` — all arguments passed at invocation
- `$ARGUMENTS[N]` or `$N` — positional argument by 0-based index
- `${CLAUDE_SKILL_DIR}` — absolute path to the skill's directory (use for bundled scripts)
- `${CLAUDE_SESSION_ID}` — current session ID

## Dynamic Context Injection

Use `` !`command` `` syntax in skill content to run shell commands before the skill is sent to Claude. Output replaces the placeholder — Claude only sees the result, not the command.

```markdown
### Current status
!`git status -s`
```

## Skill File Size Guideline

Keep `SKILL.md` under 500 lines. Move detailed reference material into separate files and link them from `SKILL.md`.

## Current Skills

- **`ascend/`** — Ascend NPU hardware entry point: NPU health check, environment setup (`ASCEND_RT_VISIBLE_DEVICES`), shell script template. Starting point for any Ascend workflow; delegates to `/vllm-ascend`, `/model-download`, `/msmodelslim`, `/aisbench`.
- **`vllm-ascend/`** — vLLM-Ascend serving toolchain: installation, offline validation, scenario tuning, online serving, contribution guide. Supporting files: `vllm-install.md`, `vllm-run.md`, `scenario-inquiry.md`, `vllm-contribute.md`.
- **`model-download/`** — Download models from ModelScope or HuggingFace to local storage. Used by vllm-ascend, msmodelslim, and aisbench before inference or quantization.
- **`msmodelslim/`** — msmodelslim quantization on Ascend NPUs: W4A8/W8A8/W4A4, one-click and custom YAML, MoE mixed precision, VLM support, sensitive layer analysis. Supporting files: `msmodelslim-quant.md`, `msmodelslim-analysis.md`.
- **`aisbench/`** — AISBench LLM evaluation framework: installation, accuracy benchmarking, and performance benchmarking against vLLM services. Supporting files: `aisbench-install.md`, `aisbench-accuracy.md`, `aisbench-performance.md`, `scripts/make_gsm8k.py`.
- **`commit-as-prompt/`** — Structured Git commit workflow with WHAT/WHY/HOW message format. `disable-model-invocation: true` (user-triggered only via `/commit-as-prompt`). Supporting files: `reference.md`, `examples.md`.
