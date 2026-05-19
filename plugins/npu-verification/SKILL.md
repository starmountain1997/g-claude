---
name: npu-verification
description: >
  Verify NPU competition entries. Given a work_repo_url and an original_model_repo_url,
  clone both repos, check whether the work repo's model matches the original model,
  and check whether the validation scripts are runnable. Use this whenever the user
  provides two repo URLs and asks to verify, validate, check, or compare them —
  especially in the context of Ascend NPU, model tuning, or competition scoring.
---

# NPU Competition Entry Verifier

## Workflow

When the user provides a `work_repo_url` and `original_model_repo_url`, run the
bundled verification script:

```bash
python3 <skill-dir>/scripts/verify_entry.py \
  --work-url "<work_repo_url>" \
  --orig-url "<original_model_repo_url>"
```

Add `--json` for machine-readable output.

## What gets checked

### Phase 1 — Model match
- Extract all `nn.Module` subclass names from both repos
- Check for shared class names between work and original repos
- Score based on class name overlap

### Phase 2 — Validation scripts runnable
- Find all `.py` and `.sh` files in the work repo
- Syntax check every Python file with `ast.parse`
- Syntax check every shell script with `bash -n`
- Detect entry points (`inference.py`, `validate.py`, `main.py`, `run.py`)
- Attempt to run key scripts (inference, validation, perf, benchmark) to see if
  they at least parse imports correctly

## Interpreting results

- **Model match passed**: At least one model class name overlaps, or the work
  repo has nn.Module classes that share names with the original. A score of 0
  means the work repo likely implements a completely different model.
- **Scripts passed**: All Python and shell files have valid syntax. If the
  scripts have syntax errors, they won't run on NPU. Run attempts may fail due
  to missing NPU hardware — this is expected; look at whether the error is an
  import/dependency error (expected without NPU) or a genuine code error.

## Output

The script outputs a summary to stdout (or JSON with `--json`). Key fields:
- `phases.model_match.passed` — whether model classes match
- `phases.model_match.score` — match score 0-100
- `phases.validation_scripts.passed` — whether all scripts have valid syntax
- `phases.validation_scripts.syntax_failures` — list of files with syntax errors
- `phases.validation_scripts.run_attempts` — results of attempting to run key scripts
