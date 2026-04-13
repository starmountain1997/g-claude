# vLLM-Ascend Contribution Guide

This guide covers the contribution process and standards for the `vllm-ascend` plugin.

## Developer Certificate of Origin (DCO)

All commits to `vllm-ascend` must include a Developer Certificate of Origin (DCO) signature. This is a mandatory requirement for contributing to the project.

### Commit Message Format

When writing a commit message for `vllm-ascend`, you **must** append a `Signed-off-by` line at the end of the message. The format is:

```text
Signed-off-by: Your Name <your.email@example.com>
```

### Automation

To automate this, the `ascend` skill will retrieve your `user.name` and `user.email` from `git config` and include them in any commit message drafts it generates.

## PR Description Template

When preparing a Pull Request for `vllm-ascend`, use the following template. The AI agent must generate this by analyzing the modifications and **getting the vllm version (not vllm-ascend) following the instruction from @ascend/vllm-install.md**:

```markdown
### What this PR does / why we need it?
[Analyze the changes and explain the purpose and necessity here]

### Does this PR introduce any user-facing change?
[Yes/No, and describe if applicable]

### How was this patch tested?
[Describe testing steps or state "Documentation-only change, no testing required"]
- vLLM version: {Get the vllm version (not vllm-ascend) following the instruction from @ascend/vllm-install.md}
- vLLM main: {Get the pinned commit URL from @ascend/vllm-install.md}
```

The agent must update this description whenever the code is updated to reflect the latest state. Once confirmed by the user, the PR description can be updated using the `gh pr edit` command from the GitHub CLI.
