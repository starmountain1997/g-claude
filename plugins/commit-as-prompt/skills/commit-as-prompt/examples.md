# Commit-As-Prompt Examples

## Example 1: Skill file (prompt commit)

```bash
git commit -m "prompt(vllm): add vLLM-Ascend serving skill" \
  -m "WHAT: introduce vllm/ skill with install, run, scenario tuning, and contribute guides.
WHY:  vLLM content was buried inside the ascend skill, making it hard to invoke independently and bloating ascend with serving concerns.
HOW:  extracted vllm-install.md, vllm-run.md, scenario-inquiry.md, vllm-contribute.md, model-download.md into a standalone skill; updated ascend and aisbench to cross-reference it."
```

## Example 2: Security fix (standard commit)

```bash
git commit -m "fix(auth): replace BasicAuth with OAuth2 code flow" \
  -m "WHAT: migrate auth middleware from BasicAuth to OAuth2 authorization code flow.
WHY:  BasicAuth over TLS was flagged in security audit #2345 as non-compliant with the new identity policy.
HOW:  added PKCE challenge, kept legacy token endpoint active behind a feature flag for gradual rollout; verified with existing auth test suite."
```

## Example 3: Refactor without behavior change

```bash
git commit -m "refactor(api): extract pagination logic into shared helper" \
  -m "WHAT: move duplicated cursor-pagination code from three route handlers into paginate().
WHY:  identical logic in /users, /posts, /comments meant three places to fix when the page-size cap changed (happened twice last quarter).
HOW:  single paginate(query, opts) helper; all three handlers delegate to it; behavior is identical, covered by existing integration tests."
```

## Example 4: Documentation / context prompt

```bash
git commit -m "prompt(msmodelslim): add VLM quantization calibration guide" \
  -m "WHAT: document multimodal calibration dataset requirements and vision layer exclusion patterns in msmodelslim-quant.md.
WHY:  text-only calibration datasets silently under-calibrate vision encoders, causing accuracy collapse on image tasks — no prior guidance existed.
HOW:  added Section 3.5.1 with dataset format, size guidelines, and YAML snippets for protecting ViT layers; included a VLM adapter checklist in Section 8.4."
```

______________________________________________________________________

## How `prompt:` commits aggregate into AI context

When a future session reads recent `prompt:` commits, the WHAT/WHY/HOW structure composes naturally:

```
<Context>
1. [WHAT] introduce vllm/ skill with install, run, and serve guides.
   [WHY]  vLLM content was buried in ascend skill, hard to invoke independently.
   [HOW]  extracted 5 files, updated cross-references in ascend and aisbench.

2. [WHAT] add msmodelslim/ skill for quantization.
   [WHY]  quantization workflow was entangled with NPU hardware concerns in ascend.
   [HOW]  moved quant/analysis files, updated E2E workflow refs to /vllm and /aisbench.
</Context>
```

Each commit is a self-contained unit of intent — useful standalone, and composable as a timeline.
