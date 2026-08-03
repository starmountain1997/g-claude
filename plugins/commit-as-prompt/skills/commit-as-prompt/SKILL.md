---
name: commit-as-prompt
description: Stage, review, and create a structured Git commit with WHAT/WHY/HOW message format optimized as AI context. Use when committing code changes.
disable-model-invocation: true
license: MIT
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

## GitHub CLI First

Prefer the GitHub CLI (`gh`) whenever the operation maps to one — pulling issue/PR context, opening a PR, watching CI. Use native `git` only where `gh` has no equivalent (`status`, `diff`, `add`, `commit`). If the remote is not GitHub, skip the `gh` steps and fall back to plain `git`.

## Steps

**1. Review the diff**

Check that only relevant changes are staged. Remove debug logs, commented-out code, or unrelated formatting.

When inspecting a specific file, always use:

```bash
git diff HEAD -- "filename"
```

Omitting `HEAD` misses staged-only changes; omitting `--` causes errors on non-ASCII filenames.

If `$ARGUMENTS` references an issue or PR number, pull its context for the WHY line:

```bash
gh issue view <n> --json title,body,state
gh pr view <n> --json title,body,state
```

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

**5. Push and open a PR**

```bash
git push -u origin HEAD
gh pr create --title "<subject>" --body "WHAT: ...
WHY:  ...
HOW:  ..."
```

Then watch CI and verify the result:

```bash
gh pr checks --watch --fail-fast
gh pr view --web
```

**Input summary:** $ARGUMENTS
