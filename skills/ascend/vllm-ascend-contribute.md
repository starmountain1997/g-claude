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
