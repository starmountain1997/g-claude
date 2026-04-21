---
name: ascend
description: Ascend NPU hardware and toolchain entry point. Use when checking NPU health, setting up the Ascend environment, quantizing models with msmodelslim, or debugging NPU-level errors. Also the starting point for any Ascend workflow — triggers the hardware check before vLLM serving or evaluation begins.
argument-hint: npu check / quantization / environment setup
---

# Ascend NPU Toolchain

This skill handles Ascend NPU hardware verification, environment configuration, and model quantization.

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

## Task Specifics

- **vLLM Serving**: Use the `/vllm` skill — installation, model download, scenario tuning, and online serving.
- **Quantization**: Use the `/msmodelslim` skill — W4A8/W8A8/W4A4, mixed precision, VLM support, accuracy recovery.
- **Evaluation**: Use the `/aisbench` skill — accuracy and performance benchmarks against a running vLLM service.

## Core Tips

- **Editable Installs**: All toolkits — `vllm`, `vllm-ascend`, `msmodelslim`, and `ais_bench` — are installed in editable mode. Run `pip show <package>` to locate the source directory. Never assume a fixed path.
