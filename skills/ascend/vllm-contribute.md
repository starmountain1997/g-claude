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

## Contribution Workflow

1. **Isolate Changes**: Always create a new branch for each contribution.
   ```bash
   git checkout -b feature/YOUR_FEATURE_NAME
   ```
1. **Verify Compatibility**: Ensure your changes are compatible with the pinned `vllm` version as described in [vllm-install.md](vllm-install.md).
1. **Run Tests**: If applicable, run existing tests or add new ones to verify your changes.
1. **DCO Signature**: Ensure every commit has the `Signed-off-by` line.

## PR Description Template

When preparing a Pull Request for `vllm-ascend`, use the following template. The AI agent should generate this by analyzing the modifications:

```markdown
### What this PR does / why we need it?
[Analyze the changes and explain the purpose and necessity here]

### Does this PR introduce any user-facing change?
[Yes/No, and describe if applicable]

### How was this patch tested?
[Describe testing steps or state "Documentation-only change, no testing required"]
- vLLM version: {Get the version from vllm-install.md or current environment}
- vLLM main: {Get the pinned commit URL from vllm-install.md Section 4}
```

The agent must update this description whenever the code is updated to reflect the latest state.
