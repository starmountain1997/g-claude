#!/usr/bin/env python3
"""Auto-increment version in plugin.json for changed plugins before commit."""

import json
import subprocess
import sys
from pathlib import Path

PLUGINS_DIR = Path("plugins")
STATE_FILE = Path(".git/bump-skill-versions-state.json")


def get_changed_plugins() -> set[str]:
    """Return names of plugins that have staged changes (diff cached vs HEAD)."""
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "HEAD", "--", "plugins/"],
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            p.split("/")[1] for p in res.stdout.splitlines() if p.startswith("plugins/")
        }
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Warning: git diff failed: {e}")
        return set()


def bump_version(version_str: str) -> str:
    """Increment version string (e.g. v1.0.0 -> v1.0.1)."""
    try:
        major, minor, patch = map(int, version_str.lstrip("v").split("."))
        return f"v{major}.{minor}.{patch + 1}"
    except ValueError:
        return "v0.0.1"


def main():
    changed_plugins = get_changed_plugins()
    if not changed_plugins:
        print("No plugin changes detected, skipping version bump.")
        return

    # Load state to avoid re-bumping within the same commit session
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass

    bumped = []

    for name in changed_plugins:
        if name in state:
            continue  # already bumped in this session

        plugin_json = PLUGINS_DIR / name / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            print(f"Warning: no plugin.json found for {name}, skipping.")
            continue

        data = json.loads(plugin_json.read_text())
        old_version = data.get("version", "v0.0.0")
        new_version = bump_version(old_version)
        data["version"] = new_version
        plugin_json.write_text(json.dumps(data, indent=2) + "\n")
        bumped.append(f"  {name}: {old_version} -> {new_version}")
        state[name] = new_version

    if bumped:
        STATE_FILE.write_text(json.dumps(state))
        print("Bumped versions for changed plugins:\n" + "\n".join(bumped))
    else:
        print("No matching plugins found.")


if __name__ == "__main__":
    main()
