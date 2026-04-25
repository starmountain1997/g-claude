# msmodeling Usage

msmodeling simulates theoretical LLM serving performance on Ascend NPUs given a hardware config and a workload. Use it before any real vLLM run to get data-backed starting values for `--max-num-seqs`, `--max-num-batched-tokens`, and `--tensor-parallel-size`.

______________________________________________________________________

## Step 1 — Write the Two Config Files

msmodeling takes two YAML files. Create them from the scenario dimensions collected in `/vllm-ascend` Phase 0.

### `instances.yaml` — Hardware & Parallelism

Maps directly to the NPU hardware from `npu-smi info` and the TP/EP values estimated in Phase 1 Step 3.

```yaml
instance_groups:
  - num_instances: 1                  # number of server replicas
    num_devices_per_instance: 8       # NPUs per replica (= TP size for single-node)
    device_type: TEST_DEVICE          # placeholder; hardware perf comes from model runner
    pd_role: both                     # "both" = aggregated prefill+decode (normal vLLM mode)
                                      # use "prefill"/"decode" only for PD-disaggregation
    parallel_config:
      world_size: 8                   # total NPUs in this instance
      tp_size: 8                      # tensor parallel degree
      dp_size: 1
      ep_size: 1                      # expert parallel (MoE only; 1 for dense models)
      moe_tp_size: 8                  # set equal to tp_size for MoE; 1 for dense
    communication_config:
      host2device_bandwidth: 10000000000   # 10 GB/s  (PCIe bandwidth to host)
      host2device_rate: 0.5
      device2device_bandwidth: 4000000000  # 4 GB/s   (inter-NPU, e.g. HCCS on 910B)
      device2device_rate: 0.5
```

### `common.yaml` — Model, Workload & Serving Limits

The serving knobs here (`max_concurrency`, `max_tokens_budget`) are what you are tuning — they map directly to vLLM parameters.

```yaml
model_config:
  name: Qwen/Qwen3-32B               # HF model ID (used for architecture lookup)
  quantize_linear_action: W8A8_DYNAMIC  # W8A8_DYNAMIC | W4A8 | W4A16 | DISABLED (bf16)
  quantize_attention_action: DISABLED
  num_mtp_tokens: 0                   # speculative decoding draft tokens; 0 = disabled
  enable_preprocessing_modeling: true
  enable_kv_transfer_modeling: true

load_gen:
  load_gen_type: fixed_length
  num_requests: 500                   # total requests to simulate
  num_input_tokens: 512               # from Phase 0: typical input length
  num_output_tokens: 256              # from Phase 0: typical output length
  request_rate: 10.0                  # from Phase 0: target QPS

serving_config:
  max_concurrency: 64       # ← tuning knob → maps to vLLM --max-num-seqs
  block_size: 128
  max_tokens_budget: 8192   # ← tuning knob → maps to vLLM --max-num-batched-tokens
```

> Set `HF_ENDPOINT=https://hf-mirror.com` if the model config cannot be fetched from HuggingFace directly.

______________________________________________________________________

## Step 2 — Run the Simulation

```bash
cd /path/to/msmodeling

python -m serving_cast.main \
  --instance_config_path=instances.yaml \
  --common_config_path=common.yaml
```

______________________________________________________________________

## Step 3 — Read the Output

The simulation prints two blocks.

**Per-request statistics** (E2E, TTFT, TPOT in seconds — note the unit):

```
              E2E_TIME(s)  TTFT(s)  TPOT(s)  ...
AVERAGE           1.23      0.45     0.012   ...
P90               1.87      0.71     0.018   ...
P99               2.10      0.83     0.021   ...
```

**Overall throughput summary**:

```
======== Overall Summary ========
benchmark_duration(s)          48.200
total_requests                 500
request_throughput(req/s)      10.37
output_token_throughput(tok/s) 2654.3
```

______________________________________________________________________

## Step 4 — Map to vLLM Parameters

| msmodeling config field | vLLM parameter | Notes |
| :--- | :--- | :--- |
| `serving_config.max_concurrency` | `--max-num-seqs` | Increase until TTFT/TPOT targets are violated |
| `serving_config.max_tokens_budget` | `--max-num-batched-tokens` | Should be ≥ max_concurrency × avg_output_len |
| `parallel_config.tp_size` | `--tensor-parallel-size` | Must divide `num_attention_heads` evenly |
| `parallel_config.ep_size` | `--pipeline-parallel-size` / EP config | MoE only |
| `model_config.quantize_linear_action: W8A8_DYNAMIC` | `--quantization ascend` | Any non-DISABLED value means quantized |
| `model_config.num_mtp_tokens > 0` | `--speculative-config` | Speculative decoding with MTP draft tokens |

**Tuning loop** — iterate until the simulated P90 TTFT and TPOT are within targets:

1. If P90 TTFT is too high → decrease `max_concurrency` (→ lower `--max-num-seqs`)
1. If throughput is below target → increase `max_concurrency` or `max_tokens_budget`
1. If memory is the bottleneck → increase `tp_size` (→ higher `--tensor-parallel-size`)

Once the simulation meets your latency and throughput targets, record `max_concurrency` and `max_tokens_budget` as the **msmodeling baseline** and carry them into `/vllm-ascend` Phase 2 Step 3.
