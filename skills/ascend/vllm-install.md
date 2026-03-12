# vLLM-Ascend Installation

Guide for installing vLLM from source on Ascend NPUs.

## Installation from Source

If `pip show vllm` or `pip show vllm-ascend` indicates an existing installation, uninstall first with `pip uninstall -y vllm vllm-ascend`.

1. **Clone Repositories**:
   - `git clone https://github.com/vllm-project/vllm.git`
   - `git clone https://github.com/vllm-project/vllm-ascend.git`
2. **Switch to Target Commit**: Read `.github/workflows/pr_test_full.yaml` in `vllm-ascend` to identify the required `vllm` commit. Switch `vllm` to that commit.
3. **Install vLLM**: `VLLM_TARGET_DEVICE=empty pip install -v -e .` in the `vllm` directory.
4. **Install vLLM-Ascend**: `pip install -v -e .` in the `vllm-ascend` directory.
