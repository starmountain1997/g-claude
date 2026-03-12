# vLLM-Ascend Running & Troubleshooting

Guide for running and debugging vLLM on Ascend NPUs.

## Running & Troubleshooting

**Standard Workflow for New Models**:
1. **Locate Weights**: Always ask the user for the local path to the model weights before proceeding.
2. **Offline Validation**: Create a standalone Python script for offline inference first.
3. **Quantized Model Check**: If the model is quantized, add `--quantization ascend` to all commands.
4. **Eager Mode (Debug)**: Initially run with `--enforce-eager` to verify operator compatibility.
   - **Source-level Fix**: If errors occur (e.g., missing kernels, assertion failures), create a new fix branch in the `vllm-ascend` directory and modify the source code directly to resolve the issue. Re-run validation after each modification.
5. **Performance Optimization**: Once eager mode passes, refer to the official docs for better performance:
   - [Feature Guide](https://docs.vllm.ai/projects/ascend/en/latest/user_guide/feature_guide/index.html): Graph Mode, Weight Prefetch, NPUGraph_EX, etc.
   - [Additional Config](https://docs.vllm.ai/projects/ascend/en/latest/user_guide/configuration/additional_config.html): `enable_npugraph_ex`, `weight_prefetch`, `finegrained_tp_config`, `eplb_config`, etc.
6. **Online Serving**: Convert the validated offline parameters into a `python -m vllm.entrypoints.openai.api_server` command. Add `--quantization ascend` if the model is quantized. **Crucial**: Ask the user for their preferred `model-served-name` and `port` before providing the final command.

**Pre-run check**: Always verify available devices with `npu-smi info`.
