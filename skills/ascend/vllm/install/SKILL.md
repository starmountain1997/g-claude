---
name: vllm-install
description: vLLM/vLLM-Ascend source installation
argument-hint: "install / build / dependency"
---

# vLLM/vLLM-Ascend Source Installation

## Steps

1. Check if installed: `pip show vllm` and `pip show vllm-ascend`. If installed, uninstall with `pip uninstall -y vllm vllm-ascend`
2. Clone source code (ask user where to clone):
   - `git clone https://github.com/vllm-project/vllm.git`
   - `git clone https://github.com/vllm-project/vllm-ascend.git`
3. Read `.github/workflows/pr_test_full.yaml` in vllm-ascend repo to find the corresponding vllm commit id. Switch vllm repo to that commit, then run `VLLM_TARGET_DEVICE=empty pip install -v -e .`
4. After vllm is installed, go to vllm-ascend repo and run `pip install -v -e .`

> **Note**: Both vLLM and vLLM-Ascend are installed via `pip install -e .`
