---
name: commit-as-prompt
description: Stage, review, and create a structured Git commit with WHAT/WHY/HOW message format optimized as AI context. Use when committing code changes.
disable-model-invocation: true
---

# Commit-As-Prompt

Creates a Git commit whose message is useful to both humans and future AI sessions — structured, purposeful, and self-contained.

## Workspace Snapshot

### Unstaged / Staged Changes
!`git status -s`

### Diff Summary
!`git diff HEAD --stat`

## Commit Message Format

```
<type>(<scope>): <imperative subject>

WHAT: <one sentence — what changed>
WHY:  <business context, user need, or bug background>
HOW:  <technical approach; note compatibility concerns or verification steps>
```

**Type prefixes:**
- `prompt(scope):` — commits intended as AI context (skill files, prompts, docs that feed future sessions)
- `feat`, `fix`, `refactor`, `docs`, `chore` — standard Conventional Commits for regular code

See [examples.md](examples.md) for full worked examples.

## Steps

**1. Review the diff**

Check that only relevant changes are staged. Remove debug logs, commented-out code, or unrelated formatting.

When inspecting a specific file, always use:
```bash
git diff HEAD -- "filename"
```
Omitting `HEAD` misses staged-only changes; omitting `--` causes errors on non-ASCII filenames.

**2. Stage**

If files aren't staged yet, add them:
```bash
git add -- "filename"
```
If the workspace mixes unrelated changes, split into separate commits.

**3. Draft the message**

Use `$ARGUMENTS` as your starting point if provided. Otherwise derive the subject from the diff.

Fill in WHAT/WHY/HOW. The WHY is the most important line — don't repeat the subject, explain the *reason* it was worth changing. See [reference.md](reference.md) for principles.

**4. Commit**

```bash
git commit -m "<subject>" -m "WHAT: ...
WHY:  ...
HOW:  ..."
```

**Input summary:** $ARGUMENTS
