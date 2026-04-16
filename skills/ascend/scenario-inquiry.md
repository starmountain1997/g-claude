# Scenario Inquiry for vLLM-Ascend Performance Tuning

Before tuning vLLM on Ascend NPUs, you **must** interview the user to identify their specific serving scenario. This information is critical for determining the optimal quantization, parallelism, and batching parameters.

## Step 1: Conduct the Interview

Ask the user to provide details for the following dimensions. Explain that these factors directly impact HBM usage (KV Cache %) and overall throughput.

### 1. Basic Dimensions (基础变量)

- **Input/Output Length (输入/输出长度)**: What is the typical context size? (e.g., 512 tokens in / 256 tokens out, or 32k RAG context).
- **Latency Sensitivity (延迟敏感度)**:
  - Is **TTFT (Time to First Token)** critical (e.g., real-time chat)?
  - Is **TPOT (Time Per Output Token)** critical (e.g., smooth streaming for code/writing)?

### 2. Traffic Dimensions (流量特征)

- **Concurrency (并发量)**: How many concurrent requests (QPS) do you expect at peak?
- **Traffic Pattern (流量模式)**: Is the traffic steady, or does it have significant **Burstiness (突发性)**?

### 3. Resource & Optimization Constraints (资源与优化约束)

- **Quantization (精度与量化)**: What precision is acceptable? (FP16, W8A8, FP8, W4A16).
- **Parallel Strategy (并行策略)**: Are there constraints on the number of NPUs or TP/PP configuration?
- **Speculative Decoding (投机采样)**: Is the user open to using a smaller draft model to accelerate generation (reduces TPOT)?

______________________________________________________________________

## Step 2: Analyze and Map to vLLM Parameters

Once the user provides the answers, use the following mapping logic to prepare for `@ascend/vllm-run.md`:

| Dimension Combination | Recommended Strategy | Key Parameter Impact |
| :--- | :--- | :--- |
| **High Concurrency + Steady Traffic** | Throughput Optimized | Increase `--max-num-seqs`, use Graph Mode (FULL). |
| **Long Context + RAG** | Memory Optimized | Enable Quantization, increase `--gpu-memory-utilization` to 0.95. |
| **TTFT Sensitive + Burst Traffic** | Latency Optimized | Decrease `--max-num-seqs`, ensure headroom in `--max-num-batched-tokens`. |
| **TPOT Sensitive (Code/Agent)** | Decoding Optimized | Enable **Speculative Decoding**, optimize `cudagraph_capture_sizes`. |

______________________________________________________________________

## Next Step: Manual Tuning

Based on the inquiry results, proceed to manual empirical tuning.

1. **Go to [vllm-run.md](vllm-run.md) Phase 2**. The scenario summary from this inquiry becomes the input to Phase 2 Step 1.
2. **Empirical Mapping**: Use the "Scenario-Based Parameter Tuning" table in Phase 2 Step 3 of that document to translate inquiry results into vLLM CLI arguments.
