______________________________________________________________________

## name: commit-as-prompt description: Create structured Git commits (WHAT/WHY/HOW) optimized for AI context. Use for clean, meaningful history that can be turned into prompts. disable-model-invocation: true

# Commit-As-Prompt

This skill guides you through creating a high-quality Git commit structured for both humans and AI.

## Current Workspace State

### Status Summary

!`git status -s`

### Changed Files Impact

!`git diff HEAD --stat`

## Task Instructions

1. **Review Changes**: Analyze the diffs to ensure only relevant changes are included. Remove any temporary logs, debuggers, or "dead" code. When running `git diff` on specific files, always use `git diff HEAD -- "filename"` to see all changes (staged or not). Never omit `HEAD` or `--`; omitting `--` causes "ambiguous argument" errors for non-ASCII filenames (e.g., Chinese), and omitting `HEAD` misses staged-only changes.
1. **Stage Files**: If files aren't staged, interact with the user or use `git add -- "filename"` to prepare the commit.
1. **Draft the Commit Message**: Use the provided summary "$ARGUMENTS" as the starting point.
1. **Follow WHAT/WHY/HOW**:
   - **WHAT**: One-sentence imperative description of the change.
   - **WHY**: Business context, user needs, or bug background.
   - **HOW**: Technical strategy, compatibility, and verification steps.
1. **Commit Types**:
   - `prompt(scope):` for commits intended as AI context.
   - Standard `feat:`, `fix:`, etc. for regular work.

## References

- For detailed staging principles, see [reference.md](reference.md)
- For message examples, see [examples.md](examples.md)

______________________________________________________________________

**Input summary:** $ARGUMENTS
