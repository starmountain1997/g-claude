# vLLM-Ascend Running & Troubleshooting

Guide for running and debugging vLLM on Ascend NPUs.

## Running & Troubleshooting

**Standard Workflow for New Models**:
1. **Locate Weights**: Always ask the user for the local path to the model weights before proceeding.
2. **Offline Validation**: Create a standalone Python script for offline inference first.
3. **Eager Mode (Debug)**: Initially run with `--enforce-eager` to verify operator compatibility.
   - **Source-level Fix**: If errors occur (e.g., missing kernels, assertion failures), create a new fix branch in the `vllm-ascend` directory and modify the source code directly to resolve the issue. Re-run validation after each modification.
4. **Graph Optimization**: Once eager mode passes, research `vllm-ascend/docs` to identify the best performance parameters (e.g., block size, specific graph optimizations) for full graph mode.
5. **Online Serving**: Convert the validated offline parameters into a `python -m vllm.entrypoints.openai.api_server` command. **Crucial**: Ask the user for their preferred `model-served-name` and `port` before providing the final command.

**Pre-run check**: Always verify available devices with `npu-smi info`.