#!/usr/bin/env python3
"""Auto-increment version in marketplace.json for changed skills before commit."""

import json
import subprocess
import sys
from pathlib import Path

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")
SKILLS_DIR = Path("skills")


def get_changed_skills() -> set[str]:
    """Return names of skills that have unstaged changes (diff vs HEAD)."""
    try:
        res = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "skills/"],
            capture_output=True,
            text=True,
            check=True,
        )
        # 使用集合推导式直接提取技能名称，避免多行循环
        return {
            p.split("/")[1] for p in res.stdout.splitlines() if p.startswith("skills/")
        }
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Warning: git diff failed: {e}")
        return set()


def bump_version(version_str: str) -> str:
    """Increment version string (e.g. v1.0.0 -> v1.0.1)."""
    try:
        # 使用 map 一次性转换类型
        major, minor, patch = map(int, version_str.lstrip("v").split("."))
        return f"v{major}.{minor}.{patch + 1}"
    except ValueError:
        return "v0.0.1"


def main():
    # 使用海象运算符 (:=) 将赋值与条件判断合二为一
    if not (changed_skills := get_changed_skills()):
        print("No skill changes detected, skipping version bump.")
        return

    if not MARKETPLACE_PATH.exists():
        sys.exit(f"Marketplace not found: {MARKETPLACE_PATH}")

    data = json.loads(MARKETPLACE_PATH.read_text())
    bumped = []

    for plugin in data.get("plugins", []):
        name = plugin.get("name")
        if name in changed_skills:
            old_version = plugin.get("version", "v0.0.0")
            # 链式赋值更新版本号
            plugin["version"] = new_version = bump_version(old_version)
            bumped.append(f"  {name}: {old_version} -> {new_version}")

    if bumped:
        MARKETPLACE_PATH.write_text(json.dumps(data, indent=2) + "\n")
        print("Bumped versions for changed skills:\n" + "\n".join(bumped))
    else:
        print("No matching plugins found in marketplace.")


if __name__ == "__main__":
    main()
