# vLLM-Ascend Management

Guide for installing, running, and debugging vLLM on Ascend NPUs.

## Installation from Source

If `pip show vllm` or `pip show vllm-ascend` indicates an existing installation, uninstall first with `pip uninstall -y vllm vllm-ascend`.

1. **Clone Repositories**:
   - `git clone https://github.com/vllm-project/vllm.git`
   - `git clone https://github.com/vllm-project/vllm-ascend.git`
2. **Switch to Target Commit**: Read `.github/workflows/pr_test_full.yaml` in `vllm-ascend` to identify the required `vllm` commit. Switch `vllm` to that commit.
3. **Install vLLM**: `VLLM_TARGET_DEVICE=empty pip install -v -e .` in the `vllm` directory.
4. **Install vLLM-Ascend**: `pip install -v -e .` in the `vllm-ascend` directory.

## Running & Troubleshooting

**Pre-run check**: Always verify available devices with `npu-smi info`.

1. **Offline Inference (Debug Mode)**:
   - Use `--enforce-eager` to run in single-operator mode for easier debugging.
   - If that works, test in graph mode (default).
2. **Online Inference (Serving)**:
   - Provide the finalized `python -m vllm.entrypoints.openai.api_server` command once offline mode is validated.

## Common Issues

- **OOM**: Reduce `--gpu-memory-utilization` or increase NPU count via `ASCEND_RT_VISIBLE_DEVICES`.
- **Operator Issues**: Check for missing kernel implementations in `vllm-ascend/vllm_ascend/ops`.
