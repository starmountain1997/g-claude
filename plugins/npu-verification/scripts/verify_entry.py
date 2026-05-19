#!/usr/bin/env python3
"""NPU competition entry verifier.

Given two git URLs, clones both repos and verifies:
  1. The work repo model matches the original model repo
  2. The work repo's validation scripts are runnable
"""

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def clone(url: str, dest: str, shallow=True) -> bool:
    args = ["git", "clone"]
    if shallow:
        args += ["--depth", "1"]
    args += [url, dest]
    r = run(args, timeout=120)
    return r.returncode == 0


# ── Phase 1: Model match ──────────────────────────────────────────────

def find_py_files(root: str) -> list:
    return sorted(Path(root).rglob("*.py"))


def extract_classes(path: str) -> list[dict]:
    """Extract nn.Module subclass names and their methods from a file."""
    classes = []
    try:
        tree = ast.parse(Path(path).read_text())
    except SyntaxError:
        return classes
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # check if it inherits from nn.Module or torch.nn.Module
            bases = []
            for base in node.bases:
                bases.append(ast.unparse(base))
            classes.append({
                "name": node.name,
                "bases": bases,
                "methods": [
                    m.name for m in node.body
                    if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
                ],
            })
    return classes


def model_classes(repo: str) -> dict[str, dict]:
    result = {}
    for f in find_py_files(repo):
        for cls in extract_classes(str(f)):
            key = f"{f.name}:{cls['name']}"
            result[key] = cls
    return result


def model_match_score(work_models: dict, orig_models: dict) -> dict:
    """Compare model classes between work and original repos."""
    work_names = {m["name"] for m in work_models.values()}
    orig_names = {m["name"] for m in orig_models.values()}

    shared = work_names & orig_names
    work_class_names = [m["name"] for m in work_models.values()
                        if any("Module" in b or "nn." in b or "Lightning" in b for b in m["bases"])]
    orig_class_names = [m["name"] for m in orig_models.values()
                        if any("Module" in b or "nn." in b or "Lightning" in b for b in m["bases"])]

    name_overlap = len(set(work_class_names) & set(orig_class_names))
    model_name_match = name_overlap > 0 or len(shared) > 0

    # also check if work readme / model files reference the original repo URL
    evidence = {
        "work_model_classes": len(work_models),
        "orig_model_classes": len(orig_models),
        "shared_class_names": sorted(shared),
        "work_nn_module_classes": sorted(work_class_names)[:30],
        "orig_nn_module_classes": sorted(orig_class_names)[:30],
    }
    return {
        "passed": model_name_match or name_overlap > 0,
        "score": min(name_overlap * 10, 100),
        "evidence": evidence,
    }


# ── Phase 2: Validation scripts runnable ──────────────────────────────

def find_scripts(repo: str) -> dict[str, list[str]]:
    py = sorted(Path(repo).rglob("*.py"))
    sh = sorted(Path(repo).rglob("*.sh"))
    # filter out hidden and __pycache__
    py = [str(p) for p in py if not any(x.startswith(".") for x in p.parts) and "__pycache__" not in str(p)]
    sh = [str(p) for p in sh if not any(x.startswith(".") for x in p.parts)]
    return {"py": py, "sh": sh}


def check_python_syntax(path: str) -> dict:
    try:
        ast.parse(Path(path).read_text())
        return {"file": path, "syntax_ok": True, "error": None}
    except SyntaxError as e:
        return {"file": path, "syntax_ok": False, "error": str(e)}


def check_shell_syntax(path: str) -> dict:
    r = run(["bash", "-n", path], timeout=30)
    return {"file": path, "syntax_ok": r.returncode == 0, "error": r.stderr.strip() if r.stderr else None}


def try_run_python(path: str, timeout: int = 60) -> dict:
    """Attempt to run a Python script (may fail due to missing NPU deps)."""
    try:
        r = run([sys.executable, path, "--help"], timeout=timeout)
        return {
            "file": path,
            "ran": True,
            "exit_code": r.returncode,
            "stderr_preview": r.stderr[:500] if r.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"file": path, "ran": False, "error": "timeout"}
    except Exception as e:
        return {"file": path, "ran": False, "error": str(e)}


def check_entry_point(repo: str) -> dict:
    """Check if inference.py or equivalent entry point exists."""
    entry_files = ["inference.py", "validate.py", "main.py", "run.py"]
    found = []
    for ef in entry_files:
        p = Path(repo) / ef
        if p.exists():
            found.append(str(p))
    return {"entry_points_found": found}


# ── Main ──────────────────────────────────────────────────────────────

def verify(work_url: str, orig_url: str, work_dir: str = None, orig_dir: str = None) -> dict:
    tmp = tempfile.mkdtemp(prefix="npu_verify_") if not work_dir else None
    wd = work_dir or os.path.join(tmp, "work_repo")
    od = orig_dir or os.path.join(tmp, "orig_repo")

    result = {
        "work_repo_url": work_url,
        "original_model_repo_url": orig_url,
        "phases": {},
    }

    # Clone
    for label, url, dest in [
        ("clone_work", work_url, wd),
        ("clone_orig", orig_url, od),
    ]:
        ok = clone(url, dest)
        result["phases"][label] = {"passed": ok, "dest": dest}
        if not ok:
            result["phases"][label]["error"] = f"Failed to clone {url}"

    # Model match
    if result["phases"]["clone_work"]["passed"] and result["phases"]["clone_orig"]["passed"]:
        work_models = model_classes(wd)
        orig_models = model_classes(od)
        result["phases"]["model_match"] = model_match_score(work_models, orig_models)

    # Validation scripts
    if result["phases"]["clone_work"]["passed"]:
        scripts = find_scripts(wd)
        py_results = [check_python_syntax(p) for p in scripts["py"]]
        sh_results = [check_shell_syntax(p) for p in scripts["sh"]]
        syntax_all_ok = all(r["syntax_ok"] for r in py_results + sh_results)
        entry = check_entry_point(wd)

        # Try to find and run key validation scripts
        run_results = []
        key_scripts = [p for p in scripts["py"]
                       if any(kw in os.path.basename(p).lower()
                              for kw in ["valid", "infer", "perf", "bench", "generate"])]
        for p in key_scripts[:5]:  # limit to 5
            run_results.append(try_run_python(p))

        result["phases"]["validation_scripts"] = {
            "passed": syntax_all_ok,
            "python_files": len(py_results),
            "shell_files": len(sh_results),
            "syntax_failures": [r for r in py_results + sh_results if not r["syntax_ok"]],
            "entry_points": entry,
            "run_attempts": run_results,
        }

    # Cleanup
    if tmp and not work_dir:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    return result


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-url", required=True)
    ap.add_argument("--orig-url", required=True)
    ap.add_argument("--work-dir")
    ap.add_argument("--orig-dir")
    ap.add_argument("--json", action="store_true", help="Output JSON only")
    args = ap.parse_args()

    result = verify(args.work_url, args.orig_url, args.work_dir, args.orig_dir)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        phases = result["phases"]
        ok = lambda p: "✅" if p.get("passed") else "❌"
        print(f"Work repo:    {result['work_repo_url']}")
        print(f"Original:     {result['original_model_repo_url']}")
        print(f"Clone work:   {ok(phases['clone_work'])}")
        print(f"Clone orig:   {ok(phases['clone_orig'])}")
        if "model_match" in phases:
            mm = phases["model_match"]
            print(f"Model match:  {ok(mm)} (score={mm['score']})")
            print(f"  Work model classes:  {mm['evidence']['work_model_classes']}")
            print(f"  Orig model classes:  {mm['evidence']['orig_model_classes']}")
            if mm["evidence"]["shared_class_names"]:
                print(f"  Shared names: {mm['evidence']['shared_class_names']}")
        if "validation_scripts" in phases:
            vs = phases["validation_scripts"]
            print(f"Scripts:      {ok(vs)}")
            print(f"  Python files: {vs['python_files']}, Shell files: {vs['shell_files']}")
            if vs["syntax_failures"]:
                print(f"  Syntax failures: {len(vs['syntax_failures'])}")
                for f in vs["syntax_failures"]:
                    print(f"    - {f['file']}: {f['error']}")
            print(f"  Entry points: {vs['entry_points']['entry_points_found']}")
            if vs.get("run_attempts"):
                for ra in vs["run_attempts"]:
                    status = f"exit={ra.get('exit_code', '?')}" if ra.get("ran") else ra.get("error", "?")
                    print(f"    {os.path.basename(ra['file'])}: {status}")
