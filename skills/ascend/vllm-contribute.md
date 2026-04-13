# vLLM-Ascend Contribution Guide

Contribution process and standards for the `vllm-ascend` plugin.

## Developer Certificate of Origin (DCO)

All commits to `vllm-ascend` must include a DCO signature — this is a hard requirement enforced by the project's CI.

Append a `Signed-off-by` line at the end of every commit message:

```text
Signed-off-by: Your Name <your.email@example.com>
```

Retrieve the name and email from `git config`:

```bash
git config user.name
git config user.email
```

If neither is set, ask the user before writing the commit message.

## PR Description

When preparing a Pull Request for `vllm-ascend`, fill in the template below.

**How to get the vLLM version and commit:**

1. Read [vllm-install.md](vllm-install.md) — the "Current Version Tracking" block at the top lists the pinned vLLM version and commit URL.
1. If that block is unpopulated, follow Section 4 of [vllm-install.md](vllm-install.md) to locate the `VLLM_COMMIT` in the CI workflow and derive the version from it.

**Template:**

```markdown
### What this PR does / why we need it?
[Analyze the changes and explain the purpose and necessity]

### Does this PR introduce any user-facing change?
[Yes/No — describe if yes]

### How was this patch tested?
[Describe testing steps, or state "Documentation-only change, no testing required"]
- vLLM version: [vLLM version from vllm-install.md — not the vllm-ascend version]
- vLLM main: [pinned vLLM commit URL from vllm-install.md]
```

Regenerate this description whenever the code changes. Once the user confirms it, apply it with:

```bash
gh pr edit --body "..."
```
