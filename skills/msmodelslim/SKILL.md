---
name: msmodelslim
description: msmodelslim quantization tool debugging
argument-hint: "quantization / quantization error / ascend"
---

> For NPU usage and source code location, see [ascend main skill](../SKILL.md).

Strictly execute the following sequential protocol when model quantization, structural consultation, or quantization debugging is requested.

# Pre-execution Validation

Verify hardware and software dependencies before proceeding.

* **Dependencies**: Execute `!pip show msmodelslim torch_npu transformers` to confirm installations.

Assess the user's scenario to select the appropriate quantization strategy.

* **One-Click**: Default for standard models without extra requirements.
* **Python Script**: Required for unsupported models, extreme precision constraints, long-sequence inference, fine-grained sensitive layer exclusion, or when One-Click throws "No best practice found".

# One-Click Quantization

## Parameter Discovery

Execute `msmodelslim quant -h`. For deeper parameter details, read the local documentation. Do not hallucinate parameters.

## Command Construction

Construct the CLI command. Enforce the target save directory to `/home/model_weights`.

Append `--fa3` or other specific flags if dictated by local source/doc analysis.

## Execution & Lifecycle Management

1. Run the constructed command in the background.
1. Monitor initial output for configuration errors or the specific error: No best practice found for model_type=xxx.
1. If "No best practice found" occurs: Immediately terminate the process and switch to Custom Python Script.
1. If execution successfully begins: Quantization is highly time-consuming. Kill the process immediately once initialization is confirmed.
1. Output the exact, validated command to the user and instruct them to run it in their own terminal.

# Custom Python Script (Advanced/Fallback)

## Reference Model Analysis

Explore the `example/` or `docs/` directories to find a script with the closest architectural match.

If cloning the reference model repository is required for structural comparison, clone strictly for configuration (skip weights):

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone <REPO_URL>
```
## Sensitive Layer Analysis(Optional)

If manual fallback layers (`disable_names`) are required, execute the analysis tool first:

```bash
msmodelslim analyze \
  --model_type <MODEL_TYPE> \
  --model_path <ORIGINAL_MODEL_PATH> \
  --metrics kurtosis \
  --topk 15 \
  --device npu
```

Extract the Top K sensitive layers from the output to populate the `disable_names` variable in the Python script.

## Script Generation & Refinement

Write or modify the Python script using standard msmodelslim APIs (QuantConfig, Calibrator).

Mandatory Default Configurations:

- `act_method`: 3(Auto-mixed)
- `anti_method`: m2(Enbanced SmoothQuant)
- Target directory: `/home/model_weights/<MODEL_NAME>_quantized`

## OOM & Hardware Management

If Out of Memory (OOM) errors occur during testing:

1. DO NOT attempt CPU quantization under any circumstances.
1. DO implement multi-NPU logic.
1. DO consult official docs for low-memory solutions.

## Execution & Lifecycle Management

1. Execute the customized Python script.
1. If errors occur, read the traceback, modify the script, and re-test until it successfully initializes the quantization loop.
1. Once the service pulls up normally and begins the main quantization loop, kill the process immediately.
1. Provide the finalized Python script, required dependencies, and execution instructions to the user for them to run independently.