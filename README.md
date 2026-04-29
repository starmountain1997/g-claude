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
claude plugin install commit-as-prompt@g-claude
```

Or install everything at once (also installs karpathy-skills and skill-creator):

```bash
curl -fsSL https://raw.githubusercontent.com/starmountain1997/g-claude/main/scripts/install-g-claude.py | python3 - --update
```

Pass any script arguments after `python3 -`, e.g. `--update`, `--help`, etc.

## Skills

| Skill | Description |
|---|---|
| **ascend** | Ascend NPU hardware entry point — health check, environment setup, shell script template. Starting point for any Ascend workflow. |
| **vllm-ascend** | vLLM-Ascend serving toolchain — install, offline validation, scenario tuning, online serving, contribution guide. |
| **msmodelslim** | Model quantization on Ascend NPUs — W4A8/W8A8/W4A4, one-click and custom YAML, MoE mixed precision, VLM support, accuracy recovery. |
| **aisbench** | AISBench evaluation framework — accuracy benchmarks (GSM8K, MMLU, AIME) and performance benchmarks against vLLM services. |
| **commit-as-prompt** | Structured Git commits with WHAT/WHY/HOW format, optimized as AI context for future sessions. |

## Workflow

The Ascend skills form a pipeline:

```
ascend (NPU check)
  ├──► vllm-ascend (install → serve)
  ├──► msmodelslim (quantize → serve via vllm)
  └──► aisbench   (evaluate accuracy & performance)
```

## License

MIT
