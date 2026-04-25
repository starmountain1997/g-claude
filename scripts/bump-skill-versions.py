#!/usr/bin/env python3
"""Auto-increment version in marketplace.json for changed skills before commit."""

import json
import re
import subprocess
import sys
from pathlib import Path

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")
SKILLS_DIR = Path("skills")


def get_changed_skills() -> set[str]:
    """Return names of skills that have unstaged changes (diff vs HEAD)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "skills/"],
            capture_output=True, text=True
        )
        changed = set()
        for line in result.stdout.strip().splitlines():
            parts = line.split("/")
            if len(parts) >= 2:
                skill_name = parts[1]
                changed.add(skill_name)
        return changed
    except Exception as e:
        print(f"Warning: git diff failed: {e}")
        return set()


def bump_version(version_str: str) -> str:
    """Increment version string (e.g. 1.0.0 -> 1.0.1)."""
    parts = version_str.lstrip("v").split(".")
    if len(parts) != 3:
        return "v0.0.1"
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    return f"v{major}.{minor}.{patch + 1}"


def main():
    changed_skills = get_changed_skills()

    if not changed_skills:
        print("No skill changes detected, skipping version bump.")
        sys.exit(0)

    if not MARKETPLACE_PATH.exists():
        print(f"Marketplace not found: {MARKETPLACE_PATH}")
        sys.exit(1)

    data = json.loads(MARKETPLACE_PATH.read_text())
    bumped = []

    for plugin in data.get("plugins", []):
        plugin_name = plugin.get("name", "")
        if plugin_name not in changed_skills:
            continue
        old_version = plugin.get("version", "v0.0.0")
        new_version = bump_version(old_version)
        plugin["version"] = new_version
        bumped.append(f"{plugin_name}: {old_version} -> {new_version}")

    MARKETPLACE_PATH.write_text(json.dumps(data, indent=2) + "\n")

    if bumped:
        print("Bumped versions for changed skills:")
        for line in bumped:
            print(f"  {line}")
    else:
        print("No matching plugins found in marketplace.")


if __name__ == "__main__":
    main()
