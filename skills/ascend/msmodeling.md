# MindStudio Modeling (msmodeling)

MindStudio Modeling is a performance simulation framework used to predict and optimize LLM performance on Ascend NPUs without requiring physical hardware access for the simulation itself.

______________________________________________________________________

## Throughput Optimizer

The `throughput_optimizer` is the primary tool for finding the best vLLM parameters (TP, DP, batch size) under SLO constraints.

### Installation & Setup

Ensure `msmodeling` is available. It is typically located in `ascend/msmodeling` (as a soft link to the source).

```bash
cd ascend/msmodeling
pip install -r requirements.txt
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### Core Usage: Aggregation Mode

Use this to find the best configuration for a standard vLLM deployment where prefill and decode run on the same instances.

```bash
python -m cli.inference.throughput_optimizer <model_id> \
    --device <DEVICE_PROFILE> \
    --num-devices <TOTAL_NPUS> \
    --input-length <AVG_PROMPT_LEN> \
    --output-length <AVG_OUTPUT_LEN> \
    --compile \
    --quantize-linear-action <DTYPE_ACTION> \
    --tpot-limits <MAX_TPOT_MS>
```

**Common Parameters:**

- `model_id`: Hugging Face ID or local path.
- `--device`: Target NPU profile (e.g., `ATLAS_800_A2_376T_64G`). Use `npu-smi info` to identify your hardware.
- `--num-devices`: Total NPUs available for the deployment.
- `--quantize-linear-action`: Matches your quantization choice (e.g., `W8A8_DYNAMIC`, `W4A8_DYNAMIC`, `DISABLED` for BF16).
- `--tpot-limits`: Maximum allowed Time-per-Output-Token in milliseconds (SLO constraint).
- `--ttft-limits`: Maximum allowed Time-to-First-Token in milliseconds (SLO constraint).

### Output Interpretation

The tool outputs a table of the top configurations:

```text
+-----+----------------------+-----------+-----------+-------------+---------------+-----------+------------+
| Top | Throughput (token/s) | TTFT (ms) | TPOT (ms) | concurrency | total_devices |  parallel | batch_size |
+-----+----------------------+-----------+-----------+-------------+---------------+-----------+------------+
|  1  |       2888.45        |  16032.05 |   49.90   |     175     |       8       | tp8pp1dp1 |    175     |
+-----+----------------------+-----------+-----------+-------------+---------------+-----------+------------+
```

- **parallel**: Shows the optimal `tensor_parallel_size` (tp), `pipeline_parallel_size` (pp), and `data_parallel_size` (dp).
- **batch_size**: The recommended `max-num-seqs` for vLLM.
- **concurrency**: Total concurrent requests supported by the system.

### Disaggregated Serving Optimization

For complex deployments separating prefill and decode phases:

```bash
# Optimize Prefill-to-Decode ratio
python -m cli.inference.throughput_optimizer <model_id> \
    --device <DEVICE_PROFILE> \
    --enable-optimize-prefill-decode-ratio \
    --prefill-devices-per-instance <NPUS_PER_PREFILL_INST> \
    --decode-devices-per-instance <NPUS_PER_DECODE_INST>
```

This identifies the optimal P:D instance ratio to maximize total system throughput.
