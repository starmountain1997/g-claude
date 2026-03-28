# vLLM-Ascend Installation

Install vLLM from source on Ascend NPUs. The core requirement is version-pinning: `vllm-ascend` only works with a specific `vllm` commit.

______________________________________________________________________

## 1. Cleanup

Remove any conflicting installations before starting:

```bash
pip uninstall -y vllm vllm-ascend
```

______________________________________________________________________

## 2. Clone Repositories

Ask the user where they want to clone the repositories before proceeding. Then clone into that directory:

```bash
cd <user-specified-directory>
git clone https://github.com/vllm-project/vllm.git
git clone https://github.com/vllm-project/vllm-ascend.git
```

______________________________________________________________________

## 3. Select vllm-ascend Version

Ask the user which version of `vllm-ascend` they want to install. List available tags to help them decide:

```bash
git -C vllm-ascend tag --sort=-version:refname | head -20
```

- If the user specifies a version, check it out:
  ```bash
  git -C vllm-ascend checkout <TAG>
  ```
- If the user doesn't know, stay on `main` (already the default after cloning).

______________________________________________________________________

## 4. Pin vllm to the Commit Expected by vllm-ascend

`vllm-ascend` is built against a specific `vllm` commit. Using any other commit causes ABI/API mismatches that are hard to diagnose.

Find the expected commit by opening the vllm-ascend CI workflow:

```bash
# Look for VLLM_COMMIT (or similar) in the CI workflow file
grep -r "VLLM_COMMIT\|vllm.*checkout\|vllm.*sha" vllm-ascend/.github/workflows/
```

Once you have the hash, switch the `vllm` repo to it:

```bash
cd vllm
git checkout <COMMIT_HASH>
cd ..
```

> If the hash is not obvious from the grep output, open `vllm-ascend/.github/workflows/vllm_ascend_test.yaml` (or the equivalent CI file) and search for `VLLM_COMMIT` or a `actions/checkout` step for `vllm-project/vllm` with a `ref:` field.

______________________________________________________________________

## 5. Install vllm Core

Install in editable mode with `VLLM_TARGET_DEVICE=empty` to skip the CUDA/ROCm build step — Ascend uses its own device backend:

```bash
cd vllm
VLLM_TARGET_DEVICE=empty pip install -v -e .
cd ..
```

______________________________________________________________________

## 6. Install vllm-ascend Plugin

```bash
cd vllm-ascend
pip install -v -e .
cd ..
```

The `-e` (editable) flag lets you modify the plugin source for debugging without reinstalling.

______________________________________________________________________

## 7. Verify

```bash
pip list | grep vllm
```

Both `vllm` and `vllm-ascend` should appear, pointing to their local source directories (editable installs show the path).

Run a quick import check:

```bash
python -c "import vllm; import vllm_ascend; print('OK')"
```
