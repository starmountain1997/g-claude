# vLLM-Ascend Running & Troubleshooting

Guide for running and debugging vLLM on Ascend NPUs. Jump to the phase that matches your current progress.

**Pre-run check**: Always verify available devices with `npu-smi info`.

______________________________________________________________________

## Phase 1: Offline Validation (Eager Mode)

*Start here. Write an offline inference script with eager mode enabled — this is the safest baseline to confirm the model loads and runs correctly before enabling graph capture.*

1. **Check NPU Availability** — Confirm devices are free and record per-card memory: `npu-smi info`

1. **Analyze Model & Plan Parallelism** — Use `safetensors` to inspect model structure and total parameter count, then combine with hardware info to decide TP / DP / EP. Write and run a script like:

   ```python
   import json, os
         from pathlib import Path
         from safetensors import safe_open
   
         model_dir = Path("/path/to/model")
   
         # ── parameter count from safetensors ──────────────────────────────
         total_params = 0
         layer_shapes: dict[str, tuple] = {}
         for shard in sorted(model_dir.glob("*.safetensors")):
             with safe_open(shard, framework="pt", device="cpu") as f:
                 for key in f.keys():
                     t = f.get_slice(key)
                     shape = tuple(t.get_shape())
                     layer_shapes[key] = shape
                     total_params += 1
                     for d in shape:
                         total_params += d - 1   # replace with math.prod below
   
         # cleaner version
         import math
         total_params = sum(math.prod(s) for s in layer_shapes.values())
         print(f"Total params : {total_params/1e9:.2f} B")
   
         # ── model config ──────────────────────────────────────────────────
         cfg = json.loads((model_dir / "config.json").read_text())
         num_experts   = cfg.get("num_experts") or cfg.get("num_local_experts", 0)
         hidden_size   = cfg.get("hidden_size", 0)
         num_layers    = cfg.get("num_hidden_layers", 0)
         print(f"Hidden size  : {hidden_size},  Layers: {num_layers},  Experts: {num_experts}")
   
         # ── parallelism planning ──────────────────────────────────────────
         # Fill in: total NPUs available, HBM per card in GiB
         num_npus   = 8          # e.g. from `npu-smi info`
         hbm_per_npu_gib = 64   # e.g. 64 GiB per 910B card
   
         bytes_per_param = 2     # bf16; use 1 for W8, 0.5 for W4
         model_gib = total_params * bytes_per_param / 1024**3
         kv_overhead = 0.2       # rough 20 % for KV cache + activations
         needed_gib  = model_gib * (1 + kv_overhead)
   
         tp = 1
         while tp * hbm_per_npu_gib < needed_gib and tp < num_npus:
             tp *= 2
   
         dp = num_npus // tp
         ep = min(num_experts, tp * dp) if num_experts else 1  # EP ≤ total NPUs
   
         print(f"Model size   : {model_gib:.1f} GiB  (needed ≈{needed_gib:.1f} GiB)")
         print(f"Recommended  : TP={tp}  DP={dp}  EP={ep}")
   ```

   Key rules:

   - **TP** (`tensor_parallel_size`): must fit the full model in HBM. TP must divide `num_attention_heads` and `num_key_value_heads` evenly.
   - **EP** (`expert_parallel_size`): for MoE models only. EP must divide `num_experts` evenly and EP ≤ TP × DP.
   - **DP** (`pipeline_parallel_size` is separate): `dp = total_npus / tp`. If dp > 1 you are running data-parallel replicas — usually only for serving.

1. **Write an Offline Script** — Create a standalone Python script for offline inference with `enforce_eager=True`. Use the TP/EP values from the step above. Save it to the current working directory.

1. **Quantized Model Check** — If the model is quantized (W4A8, W8A8, W4A16, W8A16, etc.), set `quantization="ascend"` to enable Ascend-specific quantization kernels. Do **not** set this for bf16/fp16 models — it will produce wrong output or NaN.

1. **Trust Remote Code** — For models with custom architecture (Qwen3, DeepSeek, GLM, etc.), set `trust_remote_code=True`.

1. **Source-level Fix** — If errors occur (e.g., missing kernels, assertion failures), create a fix branch in the `vllm-ascend` directory and modify source code directly. Re-run validation after each modification.

**Artifact Storage**: Save all generated Python scripts and shell scripts to the current working directory. Do not save them elsewhere.

______________________________________________________________________

## Phase 2: Performance Optimization

*Use this once the offline eager-mode script passes. Enable graph mode and tune parameters for the target serving scenario.*

### Step 1 — Disable eager mode and select graph mode

1. **Disable Eager Mode** — Remove `enforce_eager=True` to enable ACL Graph mode.

1. **Graph Mode Selection** — vLLM-Ascend supports two ACL graph capture modes:

   - **PIECEWISE** (default): captures individual ops; safe for most models
   - **FULL**: captures the full model graph; higher throughput, requires all ops to be graph-compatible

### Step 2 — Ask the user about their serving scenario

Before tuning, ask:

> 1. **Sequence length** — What is the typical input + output length?
> 1. **Concurrency** — How many concurrent requests are expected?
> 1. **Latency vs throughput** — Optimizing for TTFT/ITL, or maximizing tokens/s?

Based on the answers, reason through the following parameters:

| Parameter | Meaning & tuning rule |
| :--- | :--- |
| `--max-model-len` | Max tokens (prompt + output) per request. Set to the actual max needed — larger values consume more KV cache memory, leaving less for batching. |
| `--max-num-seqs` | Max concurrent sequences in a batch. Raising this increases throughput but raises memory pressure and latency per request. |
| `--max-num-batched-tokens` | Max total tokens across the batch. Effective cap on batch size. Should be ≥ `max-num-seqs × avg-input-len`. |
| `--gpu-memory-utilization` | Fraction of HBM reserved for KV cache (default 0.9). Raise toward 0.95 when memory is the bottleneck; lower if OOM during init. |
| `--swap-space` | CPU memory (GiB) for swapping evicted KV blocks. Increase if high concurrency causes frequent preemption. |
| `--speculative-config` | JSON config for speculative decoding. Example: `{"num_speculative_tokens": 3, "method": "deepseek_mtp"}`. Search the model tutorial doc (Step 3) for supported methods and recommended values. |
| `--compilation-config` | JSON config for ACL graph capture. Example: `{"cudagraph_capture_sizes": [8,16,24,32,40,48], "cudagraph_mode": "FULL_DECODE_ONLY"}`. Search the model tutorial doc (Step 3) for recommended sizes. |

> **Tip — `cudagraph_capture_sizes` when SP (FlashComm1) + MTP are both enabled:**
> Let `mtp = num_speculative_tokens`. Sizes must satisfy:
> - `(mtp + 1)` divisible by `tp`
> - every size a multiple of `(mtp + 1)`
> - max size = `max_num_seqs × (mtp + 1)`
>
> Example: `num_speculative_tokens=3`, `tp=4` → `mtp+1=4` ✓; `max_num_seqs=12` → sizes `[4,8,…,48]`.

### Step 3 — Check model-specific tuning docs

Find and read the tutorial for this model family before setting environment variables:

```bash
find $(python -c "import vllm_ascend, os; print(os.path.dirname(vllm_ascend.__file__))") \
	-path "*/docs/source*" -name "*.md" | head -5
# or locate the installed docs directly:
ls <vllm-ascend-repo >/docs/source/tutorials/models/
```

Read the relevant `.md` file — it lists recommended `VLLM_ASCEND_*` environment variables, `--additional-config`, `--speculative-config`, `--compilation-config` options, and known limitations for that model family. Use those values; do not guess from memory.

______________________________________________________________________

## Phase 3: Online Serving

*Use this once offline inference is stable and optimized.*

1. **Ask the user** for their preferred `model-served-name` and `port` before writing any command.

1. **Convert to API server** — Translate the validated offline parameters into an `api_server` launch. Wrap in a shell script following the log-capture template in `SKILL.md` — stdout and stderr must be captured to a timestamped log file via `2>&1 | tee`.

1. **Health Check** — Ask the user for the server's reachable address before running (do not assume `localhost` — proxy settings or network topology may require the LAN IP instead):

   ```bash
   curl http:// <host >: <port >/v1/models
   ```

1. **Test Request** — Choose the appropriate smoke test based on model type:

   - **Text / chat model**: send a plain-text completion or chat request via curl.
   - **Multimodal (vision) model**: send both a text-only request and an image request. Use `${CLAUDE_SKILL_DIR}/cat.jpg` as the test image.
   - **TTS / ASR / audio model**: curl syntax varies per endpoint — provide the endpoint path and flag the correct `Content-Type`, then ask the user to run it themselves since audio I/O cannot be verified here.

### Graceful Shutdown

```bash
# Find vLLM process
VLLM_PID=$(pgrep -f "vllm serve")

# Graceful shutdown (SIGINT)
kill -2 "$VLLM_PID"
```

______________________________________________________________________

## Troubleshooting

First, look up the error in the vllm-ascend docs before attempting a fix:

```bash
ls <vllm-ascend-repo >/docs/source/
```

Read relevant files there (FAQ, known issues, model-specific pages). Then reason from the error message and context — do not guess at solutions not supported by the docs or the source code.
