---
name: msmodeling
description: MindStudio-Modeling performance evaluation framework for Ascend NPUs. Split into TensorCast (per-model, operator-level analysis) and ServingCast (system-level, multi-instance serving simulation). Use when you need to analyze model performance on hardware or optimize serving deployment.
license: MIT
---

# MindStudio-Modeling

MindStudio-Modeling provides two simulation tools for different purposes:

## Quick Selection

| Need | Sub-skill |
|------|-----------|
| Predict single model inference time | [tensor-cast](tensor-cast/) |
| Operator-level breakdown (which op is bottleneck) | [tensor-cast](tensor-cast/) |
| Memory footprint analysis | [tensor-cast](tensor-cast/) |
| Find optimal TP/DP/EP parallelism for a model | [tensor-cast](tensor-cast/) |
| Multi-instance throughput under SLO constraints | [serving-cast-simulation](serving-cast-simulation/) |
| Prefill/Decode disaggregation planning | [serving-cast-simulation](serving-cast-simulation/) |
| Determine how many instances needed for target throughput | [serving-cast-simulation](serving-cast-simulation/) |
| TTFT/TPOT optimization under latency limits | [serving-cast-simulation](serving-cast-simulation/) |
| Capacity planning before deployment | [serving-cast-simulation](serving-cast-simulation/) |

## Sub-Skills

### [tensor-cast](tensor-cast/) — Per-Model Performance Simulation

Analyzes how a single model performs on hardware at the operator level. For inference time prediction, operator breakdown, memory analysis, and TP/DP/EP optimization.

### [serving-cast-simulation](serving-cast-simulation/) — System-Level Serving Simulation

Simulates multi-instance serving with request workloads. For multi-instance throughput, capacity planning, and TTFT/TPOT optimization.

## Simple Rule of Thumb

- **TensorCast:** You want to understand how a *model* performs on hardware
- **ServingCast:** You want to understand how a *serving system* performs with multiple instances and requests
