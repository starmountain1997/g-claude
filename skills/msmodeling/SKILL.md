---
name: msmodeling
description: MindStudio-Modeling performance evaluation and deployment strategy tuning on Ascend NPUs. Use to simulate LLM serving throughput and latency before running real vLLM experiments, and to find optimal --max-num-seqs, --max-num-batched-tokens, and --tensor-parallel-size values.
---

# MindStudio-Modeling

MindStudio-Modeling (msmodeling) simulates theoretical LLM serving performance on Ascend NPUs and finds optimal deployment parameters before any real hardware run.

**Entry point**: `python -m serving_cast.main --instance_config_path=<hw.yaml> --common_config_path=<workload.yaml>`

## Contents

- [Installation](msmodeling-install.md)
- [Usage & vLLM integration](msmodeling-usage.md)
