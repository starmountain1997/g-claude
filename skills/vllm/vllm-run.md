# vLLM-Ascend Running & Troubleshooting

Guide for running and debugging vLLM on Ascend NPUs. Jump to the phase that matches your current progress.

**Pre-run check**: Always verify available devices with `npu-smi info`.

______________________________________________________________________

## Phase 1: Offline Validation (Eager Mode)

*Start here. Write an offline inference script with eager mode enabled — this is the safest baseline to confirm the model loads and runs correctly before enabling graph capture.*

1. **Get the Model Locally** — If the model is not yet on disk, follow [model-download.md](model-download.md) to download it (ModelScope first, HuggingFace as fallback). Record the local path as `$MODEL_PATH`. Do not use an online model ID in any of the steps below.

1. **Check NPU Availability** — Confirm devices are free and record per-card memory: `npu-smi info`

1. **Estimate Parallelism** — Use this script to estimate TP/EP based on model size and NPU HBM:

   ```python
   import json, os
                                                from pathlib import Path
                                                from safetensors import safe_open
                                                import math

                                                model_dir = Path("/path/to/model")

                                                # parameter count from safetensors
                                                total_params = 0
                                                layer_shapes: dict[str, tuple] = {}
                                                for shard in sorted(model_dir.glob("*.safetensors")):
                                                    with safe_open(shard, framework="pt", device="cpu") as f:
                                                        for key in f.keys():
                                                            t = f.get_slice(key)
                                                            shape = tuple(t.get_shape())
                                                            layer_shapes[key] = shape

                                                total_params = sum(math.prod(s) for s in layer_shapes.values())
                                                print(f"Total params : {total_params/1e9:.2f} B")

                                                # model config
                                                cfg = json.loads((model_dir / "config.json").read_text())
                                                num_experts   = cfg.get("num_experts") or cfg.get("num_local_experts", 0)
                                                hidden_size   = cfg.get("hidden_size", 0)
                                                num_layers    = cfg.get("num_hidden_layers", 0)
                                                print(f"Hidden size  : {hidden_size},  Layers: {num_layers},  Experts: {num_experts}")

                                                # parallelism planning
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

   - **TP**: must fit the full model in HBM. TP must divide `num_attention_heads` and `num_key_value_heads` evenly.
   - **EP**: for MoE models only. EP must divide `num_experts` evenly and EP ≤ TP × DP.

1. **Write an Offline Script** — Create a standalone Python script for offline inference with `enforce_eager=True`. Use the TP/EP values from the step above. Save it to the current working directory.

1. **Quantized Model Check** — If the model is quantized (W4A8, W8A8, W4A16, W8A16, etc.), set `quantization="ascend"` to enable Ascend-specific quantization kernels. Do **not** set this for bf16/fp16 models — it will produce wrong output or NaN.

1. **Trust Remote Code** — For models with custom architecture (Qwen3, DeepSeek, GLM, etc.), set `trust_remote_code=True`.

1. **Source-level Fix** — If errors occur (e.g., missing kernels, assertion failures), create a fix branch in the `vllm-ascend` directory and modify source code directly. Re-run validation after each modification.

**Artifact Storage**: Save all generated Python scripts and shell scripts to the current working directory. Do not save them elsewhere.

______________________________________________________________________

## Phase 2: Performance Optimization

*Use this once the offline eager-mode script passes. Enable graph mode and tune parameters for the target serving scenario.*

### Step 1 — Confirm Scenario

If scenario inquiry has not been done yet, load [scenario-inquiry.md](scenario-inquiry.md) and complete the interview first. It will route you back here once done.

If the user arrived here from scenario-inquiry.md, **state the scenario summary** before proceeding (e.g., "High-concurrency ChatBot: 200 QPS steady, TPOT-sensitive, W8A8, TP=8"). This anchors all parameter choices in Steps 2–3.

______________________________________________________________________

### Step 2 — Enable Graph Mode

1. **Disable Eager Mode** — Remove `enforce_eager=True` from the offline script. This activates ACL Graph capture.

1. **Read Model-Specific Docs** — Before setting any flags, look up the model family's tuning guide in the vllm-ascend source:

   ```bash
   find $(python -c "import vllm_ascend, os; print(os.path.dirname(vllm_ascend.__file__))") \
   	-path "*/docs/source*" -name "*.md" | head -5
   # or:
   ls <vllm-ascend-repo>/docs/source/tutorials/models/
   ```

   Read the relevant `.md` — it lists recommended `VLLM_ASCEND_*` env vars, `--additional-config`, `--speculative-config`, `--compilation-config` options, and known limitations. Use those values; do not guess from memory.

1. **Set Graph Capture Sizes** — Configure `cudagraph_capture_sizes` to cover the expected batch sizes. Include the powers-of-two from 1 up to `max-num-seqs`:

   ```python
   # Example: max-num-seqs=256, add common sizes
                              cudagraph_capture_sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256]
   ```

______________________________________________________________________

### Step 3 — Scenario-Based Parameter Tuning

Apply parameters based on the scenario confirmed in Step 1. Use the mapping below:

| Scenario | Key Parameters | Notes |
| :--- | :--- | :--- |
| **High Concurrency + Steady traffic** | `--max-num-seqs` ↑, FULL graph mode | Prioritize throughput; graph capture covers high batch sizes |
| **Long Context / RAG** | `--gpu-memory-utilization 0.95`, enable quantization | Higher HBM allocation for KV cache; quantization reduces model footprint |
| **TTFT-Sensitive + Bursty traffic** | `--max-num-seqs` ↓, `--max-num-batched-tokens` with headroom | Smaller batches reduce prefill queue depth; leave token budget for burst |
| **TPOT-Sensitive (code / agent)** | `--speculative-config` with draft model, tune `cudagraph_capture_sizes` | Speculative decoding cuts per-token latency; capture small batch sizes too |
| **Memory-Constrained** | `--gpu-memory-utilization 0.9`→`0.95`, lower `--max-num-seqs` | Balance KV cache vs. model weight footprint |

If speculative decoding is selected, ask the user for their preferred draft model before writing any command.

______________________________________________________________________

## Phase 3: Online Serving

*Use this once offline inference is stable and optimized.*

1. **Ask the user** for their preferred `model-served-name` and `port` before writing any command.

1. **Convert to API server** — Translate the validated offline parameters into an `api_server` launch. Wrap in a shell script following the log-capture template in `SKILL.md` — stdout and stderr must be captured to a timestamped log file via `2>&1 | tee`.

1. **Health Check** — Ask the user for the server's reachable address before running (do not assume `localhost` — proxy settings or network topology may require the LAN IP instead):

   ```bash
   curl http://<host>:<port>/v1/models
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
ls <vllm-ascend-repo>/docs/source/
```

Read relevant files there (FAQ, known issues, model-specific pages). Then reason from the error message and context — do not guess at solutions not supported by the docs or the source code.
