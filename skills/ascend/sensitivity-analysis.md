# Sensitivity Analysis for Accuracy Recovery

Protocol for diagnosing which layers are most sensitive to quantization and recovering accuracy via targeted exclusions.

## 0. When to Use This

Run this **only after** AISBench evaluation fails (see [ais_bench.md](ais_bench.md)). Do **not** run preemptively.

## 1. Run Sensitivity Analysis

```bash
msmodelslim analyze \
  --model_type <TYPE> \
  --model_path <PATH> \
  --metrics kurtosis \
  --topk 15 \
  --device npu
```

## 2. Interpret Top-K Layers

Extract the top-ranked layer names from the output. These are the layers most sensitive to quantization.

## 3. Add Exclusions to Quantization Config

Add the sensitive layer names to `disable_names` (or `exclude` patterns) in your quantization YAML config:

```yaml
- type: "linear_quant"
  qconfig: *default_w4a8_dynamic
  include: ["*mlp.experts*"]
  exclude:
    - "*<sensitive_layer_1>*"
    - "*<sensitive_layer_2>*"
    # ... add all top-k layers
```

## 4. Retry Quantization

Re-run quantization with the **same target dtype** as the original attempt. Do not downgrade to a lower compression tier without explicit user confirmation.

## 5. Re-evaluate

Run AISBench again (see [ais_bench.md](ais_bench.md)) to verify accuracy recovery.
