# g-claude

A Claude Code skills marketplace for Ascend NPU inference, model quantization, LLM evaluation, and structured Git commits.

## Install as a marketplace

```bash
claude plugin marketplace add starmountain1997/g-claude
```

Then install individual skills:

```bash
claude plugin install ascend@g-claude
claude plugin install vllm-ascend@g-claude
claude plugin install msmodelslim@g-claude
claude plugin install aisbench@g-claude
claude plugin install model-download@g-claude
claude plugin install msmodeling@g-claude
claude plugin install npu-verification@g-claude
claude plugin install commit-as-prompt@g-claude
claude plugin install rust-idiomatic@g-claude
```

Or install everything at once (also installs karpathy-skills and skill-creator):

```bash
curl -fsSL https://raw.githubusercontent.com/starmountain1997/g-claude/main/scripts/install-g-claude.py | python3 -
```

Pass any script arguments after `python3 -`, e.g. `--ascend` or `--help`.

For Codex, use the corresponding installer:

```bash
curl -fsSL https://raw.githubusercontent.com/starmountain1997/g-claude/main/scripts/install-g-codex.py | python3 -
```

For OpenCode, install all skills globally:

```bash
curl -fsSL https://raw.githubusercontent.com/starmountain1997/g-claude/main/scripts/install-g-claude.py | python3 - --opencode
```

## Skills

| Skill | Description |
|---|---|
| **ascend** | Ascend NPU hardware and toolchain entry point — health check, environment setup, quantization, NPU-level error debugging. Starting point for any Ascend workflow. |
| **vllm-ascend** | vLLM-Ascend serving toolchain — install, offline inference, OpenAI-compatible serving, throughput/latency tuning, contribution guide. |
| **msmodelslim** | Model quantization on Ascend NPUs — W4A8/W8A8/W4A16/W4A4, one-click and custom YAML, MoE mixed precision, VLM calibration, sensitive layer analysis. |
| **aisbench** | AISBench evaluation framework — accuracy benchmarks (GSM8K, MMLU, GPQA, MATH-500, LiveCodeBench, AIME, C-Eval) and performance benchmarks against vLLM services. |
| **model-download** | Download models from ModelScope or HuggingFace to local storage before inference, quantization, or evaluation. |
| **msmodeling** | MindStudio-Modeling performance evaluation for Ascend NPUs — TensorCast operator-level analysis and ServingCast multi-instance serving simulation. |
| **npu-verification** | Verify NPU competition entries — clone work and original model repos, check model match and runnable validation scripts. |
| **commit-as-prompt** | Stage, review, and create structured Git commits with WHAT/WHY/HOW format, optimized as AI context. |
| **rust-idiomatic** | Concise, idiomatic Rust patterns for implementation, review, testing, and required quality checks. Source: [Rust Users Forum](https://users.rust-lang.org/t/skills-md-for-rust-development/140098/17#p-569555-idiomatic-rust-patterns-1). |

## Workflow

The Ascend skills form a pipeline:

```
ascend (NPU check)
  ├──► model-download  (fetch model from ModelScope/HF)
  ├──► vllm-ascend     (install → serve)
  ├──► msmodelslim     (quantize → serve via vllm)
  ├──► msmodeling      (performance analysis)
  ├──► aisbench        (evaluate accuracy & performance)
  └──► npu-verification (competition entry check)
```

## License

MIT
