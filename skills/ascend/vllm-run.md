# vLLM-Ascend Running & Troubleshooting

Guide for running and debugging vLLM on Ascend NPUs. Jump to the phase that matches your current progress.

**Pre-run check**: Always verify available devices with `npu-smi info`.

______________________________________________________________________

## Phase 1: Setup & Basic Validation

*Use this if you are starting with a new model or new environment.*

1. **Locate Weights** — Ask the user for the local path to the model weights before proceeding.

1. **Set environment variables**:

   ```bash
   export VLLM_USE_MODELSCOPE=true
   export VLLM_WORKER_MULTIPROC_METHOD=spawn
   ```

   - `VLLM_USE_MODELSCOPE`: Use ModelScope for model downloads (recommended in China)
   - `VLLM_WORKER_MULTIPROC_METHOD=spawn`: Required for NPU multi-process support

1. **Offline Validation** — Create a standalone Python script for offline inference first to ensure the basic setup is functional (see Quick Start below).

1. **Quantized Model Check** — If the model is quantized (W4A8, W8A8, W4A16, W8A16, etc.), add `--quantization ascend` to enable Ascend-specific quantization kernels. Do **not** add this flag for bf16/fp16 models — it will produce wrong output or NaN.

1. **Trust Remote Code** — For models with custom architecture (Qwen3, DeepSeek, GLM, etc.), add `--trust-remote-code`.

**Artifact Storage**: Save all generated Python scripts and shell scripts to the current working directory. Do not save them elsewhere.

### Quick Start: Offline Inference

```python
import os
os.environ["VLLM_USE_MODELSCOPE"] = "true"
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "spawn"

from vllm import LLM, SamplingParams

llm = LLM(
    model="/path/to/your/model",
    tensor_parallel_size=1,          # Number of NPUs for TP
    trust_remote_code=True,           # Required for custom architectures
    # quantization="ascend",           # Uncomment if model is quantized (W4A8/W8A8)
    # max_model_len=4096,              # Override max sequence length
    # enforce_eager=True,              # Debug: disable graph mode
)

sampling_params = SamplingParams(
    max_tokens=512,
    temperature=0.7,
)

outputs = llm.generate(["Your prompt here"], sampling_params)
print(outputs[0].outputs[0].text)
```

______________________________________________________________________

## Phase 2: Compatibility & Debugging (Eager Mode)

*Use this if the model fails to run or produces errors in graph mode.*

1. **Enable Eager Mode** — Add `--enforce-eager` to disable ACL Graph and verify operator compatibility. This isolates kernel issues from graph capture problems. If the model runs correctly in eager mode but fails in graph mode, the issue is in graph capture or a graph-incompatible op.

1. **Check NPU Availability** — Ensure NPUs are not locked by other processes: `npu-smi info`

1. **Source-level Fix** — If errors occur (e.g., missing kernels, assertion failures), create a fix branch in the `vllm-ascend` directory and modify source code directly. Re-run validation after each modification.

### Common CLI Arguments

| Argument | Short | Description |
| :--- | :--- | :--- |
| `--model` | `-m` | Model path or HuggingFace/ModelScope ID |
| `--tensor-parallel-size` | `--tp` | Number of NPUs for tensor parallelism |
| `--gpu-memory-utilization` | | Memory fraction (default 0.9) |
| `--max-model-len` | | Maximum sequence length |
| `--max-num-seqs` | | Maximum concurrent sequences |
| `--enforce-eager` | | Disable graph mode, use eager execution |
| `--quantization` | `-q` | Quantization method (`ascend` for W4A8/W8A8/W4A16/W8A16 models) |
| `--trust-remote-code` | | Allow custom model code (required for Qwen3, DeepSeek, GLM) |
| `--swap-space` | | CPU swap space in GB for KV cache offload |
| `--additional-config` | | JSON string for Ascend-specific config (see AscendConfig below) |
| `--disable-log-stats` | | Disable performance logging |
| `--disable-log-request` | | Disable per-request logging |

______________________________________________________________________

## Phase 3: Performance Optimization

*Use this if you already have a working script and want to improve throughput.*

1. **Disable Eager Mode** — Once eager mode passes, remove `--enforce-eager` to enable ACL Graph mode for better performance.

1. **Graph Mode Selection** — vLLM-Ascend supports two ACL graph capture modes:

   - **PIECEWISE** (default): captures individual ops; safe for most models
   - **FULL**: captures the full model graph; higher throughput, requires all ops to be graph-compatible

   For experimental **XLite** graph mode:

   ```bash
   --additional-config '{"xlite_graph_config": {"enabled": true}}'
   ```

   XLite is incompatible with: speculative decoding, pipeline parallelism, and block sizes other than 128.

1. **Multi-NPU Scaling**:

   ```bash
   --tensor-parallel-size 2   # 2 NPUs
   --tensor-parallel-size 4   # 4 NPUs
   ```

1. **Memory Tuning**:

   ```bash
   --gpu-memory-utilization 0.95    # Use more NPU memory
   --swap-space 16                   # CPU swap for KV cache (GB)
   ```

1. **Fusion Config (Advanced)** — Enable operator fusion passes:

   ```bash
   --additional-config '{"ascend_compilation_config": {"enable_norm_quant_fusion": true, "enable_allreduce_rms_fusion": true}}'
   ```

### Performance Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `VLLM_ASCEND_ENABLE_FLASHCOMM1` | 0 | FlashComm1 for TP allreduce; beneficial at high concurrency (>1000 tokens) |
| `VLLM_ASCEND_FLASHCOMM2_PARALLEL_SIZE` | 0 | FlashComm2 O-matrix TP group size (0=disabled) |
| `VLLM_ASCEND_ENABLE_MATMUL_ALLREDUCE` | 0 | MatmulAllReduce fusion for TP — A2 only, eager mode only |
| `VLLM_ASCEND_ENABLE_MLAPO` | 1 | MLAPO optimization for DeepSeek W8A8 (better perf, more memory) |
| `VLLM_ASCEND_ENABLE_NZ` | 1 | FRACTAL_NZ weight format: 0=disabled, 1=quantized models only, 2=always |
| `VLLM_ASCEND_ENABLE_CONTEXT_PARALLEL` | 0 | Context parallelism for long-sequence prefill |
| `VLLM_ASCEND_ENABLE_FUSED_MC2` | 0 | Fused MC2 for MoE W8A8: 1=prefill fused dispatch (EP≤32), 2=decode fused dispatch (D-node only) |
| `VLLM_ASCEND_ENABLE_NPUGRAPH_EX` | 0 | NPU graph backend optimization |

> **Deprecated**: `VLLM_ASCEND_ENABLE_PREFETCH_MLP` is superseded by `weight_prefetch_config` in `--additional-config`.

______________________________________________________________________

## Phase 4: Online Serving

*Use this once offline inference is stable and optimized.*

1. **Convert to API server** — Take the validated offline parameters and launch the API server:

   ```bash
   python -m vllm.entrypoints.openai.api_server \
     --model /path/to/model \
     --tensor-parallel-size 2 \
     --trust-remote-code \
     --quantization ascend \
     --host 0.0.0.0 \
     --port 8000 2>&1 | tee serve_<model>.log
   ```

1. **Health Check** — Verify server is ready:

   ```bash
   curl http://localhost:8000/v1/models
   ```

1. **Test Request**:

   ```bash
   curl http://localhost:8000/v1/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "your-model-name",
       "prompt": "Hello, how are you?",
       "max_completion_tokens": 100,
       "temperature": 0
     }'
   ```

1. **Final Deployment** — Ask the user for their preferred `model-served-name` and `port` before providing the final command.

### Graceful Shutdown

```bash
# Find vLLM process
VLLM_PID=$(pgrep -f "vllm serve")

# Graceful shutdown (SIGINT)
kill -2 "$VLLM_PID"
```

______________________________________________________________________

## Troubleshooting

### Startup Issues

| Symptom | Likely Cause | Solution |
| :--- | :--- | :--- |
| Port bind failed | Port already in use | Kill stale processes: `pkill -f vllm` |
| HCCL bind error | NPU conflict | Run `npu-smi info` to check availability |
| "Stuck" at startup | ACL graph capture in progress | Wait for "Graph capturing finished" in logs; can take several minutes for large models |
| False-ready (crashes on first request) | Runtime error masked during init | Always run a smoke test request immediately after server reports ready |
| "XLite not compatible with..." | XLite used with unsupported feature | Disable XLite, or disable speculative decoding / pipeline parallelism |

### Runtime Issues

| Symptom | Likely Cause | Solution |
| :--- | :--- | :--- |
| Missing kernel errors | Unsupported operator in graph mode | Add `--enforce-eager` to isolate; fix kernel or avoid unsupported op |
| Wrong output / nan | `--quantization ascend` on a bf16 model | Remove `--quantization ascend` for non-quantized models |
| OOM during model load | Model too large for NPU memory | Reduce `--gpu-memory-utilization`, increase `--swap-space`, or use more NPUs |
| OOM during inference | KV cache exhausted | Reduce `--max-model-len` or `--max-num-seqs` |
| Slow first token | Graph compilation on first shape | Normal on first request; subsequent requests will be fast |
| Fine-grained TP error | oproj/lmhead TP used outside graph mode | `oproj_tensor_parallel_size` requires graph mode and D-node in PD setup |

### Environment Issues

| Symptom | Likely Cause | Solution |
| :--- | :--- | :--- |
| Code changes not picked up | Wrong import path | Check `python -c "import vllm; print(vllm.__file__)"` |
| Architecture not recognized | Missing model registry entry | Add mapping to `vllm/model_executor/models/registry.py` |
| Remote code import fails | transformers version mismatch | Don't upgrade transformers; prefer native vLLM model implementation |
| `SOC_VERSION` not found | npu-smi not on PATH or NPU not detected | Set `SOC_VERSION` manually (e.g., `Ascend910B3`) |

______________________________________________________________________

## Reference: Common Model Configurations

### Qwen3 Dense

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-8B-Instruct \
  --trust-remote-code \
  --tensor-parallel-size 2 2>&1 | tee serve_qwen3_dense.log
```

### Qwen3 Quantized (W4A8)

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-8B-W4A8 \
  --trust-remote-code \
  --quantization ascend \
  --tensor-parallel-size 2 2>&1 | tee serve_qwen3_w4a8.log
```

### DeepSeek V3 (MoE, W8A8)

```bash
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-V3 \
  --trust-remote-code \
  --quantization ascend \
  --tensor-parallel-size 8 2>&1 | tee serve_deepseek_v3_w8a8.log
```

### DeepSeek V3 with Multi-Token Prediction (MTP)

MTP (speculative decoding via draft tokens) is supported for DeepSeek-V2/V3. Pass via `--speculative-config`:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-V3 \
  --trust-remote-code \
  --quantization ascend \
  --tensor-parallel-size 8 \
  --speculative-config '{"method": "deepseek_mtp", "num_speculative_tokens": 1}' \
  2>&1 | tee serve_deepseek_v3_mtp.log
```

> MTP is incompatible with XLite graph mode.
