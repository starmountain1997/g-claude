---
name: ascend
description: Entry point for Ascend NPU inference toolchain. Use when running vLLM on Ascend/NPU, quantizing models with msmodelslim, or debugging NPU errors.
argument-hint: vllm issue / quantization / npu usage
---

# Ascend Inference Toolchain

This skill manages Ascend NPU-related tasks, troubleshooting, and toolchain usage.

## Hardware Check

Run at the start of every session before any quantization or inference task:

```bash
npu-smi info
```

Verify:

- All expected NPUs appear and show **Health: OK**
- No NPU is occupied by another process (check "Process ID" column)
- If an NPU is occupied, ask the user whether to free it by killing vllm/python processes:
  ```bash
  kill -9 $(pgrep -f vllm) 2>/dev/null
  kill -9 $(pgrep -f python) 2>/dev/null
  ```

## Common Environment Setup

`ASCEND_RT_VISIBLE_DEVICES` controls which NPUs are visible to **both** vLLM and msmodelslim. Set this before any command that touches NPUs.

## Common Requirement: Run via Shell Script with Log Output

All actual run/quantization/inference commands must be saved to a shell script and executed through it. The script must redirect both stdout and stderr to a log file so that output is preserved for debugging.

**Template:**

```bash
cat >run.sh <<'EOF'
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/run_$(date +%Y%m%d_%H%M%S).log"

# Environment setup
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3

# Run and log
"$@" 2>&1 | tee "$LOG_FILE"
EOF
chmod +x run.sh
./run.sh YOUR_COMMAND
```

**Key points:**

- Both stdout and stderr are captured in the log file via `2>&1 | tee "$LOG_FILE"`
- Log file is named with a timestamp so each run gets a unique file
- The script must be `chmod +x` before execution
- Do **not** run commands directly in the terminal; always go through the script so output is saved
- Do **not** run the script in the background (no `&`, no `nohup`, no `run_in_background`); run it in the foreground so output streams to the terminal in real time

## Tool Disambiguation

> **`msmodeling` vs `msmodelslim` — these are two completely different tools:**
>
> | Tool | Full name | Purpose | CLI entry point |
> | :--- | :--- | :--- | :--- |
> | **msmodeling** | MindStudio Modeling | **Simulation** — predicts optimal TP/DP/batch size *without touching hardware* | `python -m cli.inference.throughput_optimizer` |
> | **msmodelslim** | MindStudio ModelSlim | **Quantization** — converts model weights to W4A8/W8A8/W4A4 etc. | `msmodelslim quant` |
>
> If the task involves *deployment parameter tuning*, use **msmodeling**.
> If the task involves *compressing model weights*, use **msmodelslim**.

## Task Specifics

For detailed instructions on specific tools, refer to:

- **Model Download**: Before inference or quantization, get the model locally. See [model-download.md](model-download.md) — ModelScope first, HuggingFace as fallback. Always ask the user where to store before downloading. Never use online model IDs in vLLM or msmodelslim commands.
- **vLLM-Ascend**:
  - **Installation**: See [vllm-install.md](vllm-install.md).
  - **Running & Tuning**: **Always start with [scenario-inquiry.md](scenario-inquiry.md)** to define your performance goals and serving scenario. It will guide you through the optimal path: either [msmodeling.md](msmodeling.md) (Simulation) or [vllm-run.md](vllm-run.md) (Manual Tuning & Deployment).
- **vLLM-Ascend Contribution**: See [vllm-contribute.md](vllm-contribute.md) for DCO signature requirements and PR description template.
- **msmodeling**: See [msmodeling.md](msmodeling.md) for performance simulation and vLLM parameter optimization (TP/DP/batch size).
- **msmodelslim**: See [msmodelslim-quant.md](msmodelslim-quant.md) for quantization protocols.
- **AISBench Evaluation**: See [aisbench-install.md](aisbench-install.md) for installation and [aisbench-accuracy.md](aisbench-accuracy.md) for accuracy benchmarking.

## Core Tips

- **Editable Installs**: All toolkits — `vllm`, `vllm-ascend`, `msmodelslim`, and `ais_bench` — are installed in editable mode. Before referencing or modifying any of them, run `pip show <package>` to locate the source directory. Never assume a fixed path.
- **Source Debugging**: Use `pip show <package>` to find the editable source location for deep debugging.
- **Debugging Branch**: Before any debugging session, create a new git branch to isolate changes:
  ```bash
  git checkout -b debug/TOPIC
  ```
