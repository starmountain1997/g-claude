#!/usr/bin/env python3
"""
Install g-claude skills and optional extras.

Usage:
    python install-g-claude.py [--context7-key <KEY>]

Without arguments: registers the marketplace and installs all skills.
With --context7-key: also installs Context7 MCP for Claude Code and OpenCode.
"""

import json
import os
import subprocess
import sys


MARKETPLACE_REPO = "starmountain1997/g-claude"
MARKETPLACE_NAME = "g-claude"

SKILLS = [
    "ascend",
    "vllm",
    "msmodelslim",
    "aisbench",
    "commit-as-prompt",
]

KARPATHY_MARKETPLACE = "forrestchang/andrej-karpathy-skills"
KARPATHY_PLUGIN = "andrej-karpathy-skills@karpathy-skills"

ANTHROPIC_MARKETPLACE = "anthropics/skills"
ANTHROPIC_PLUGINS = [
    "skill-creator@anthropics/skills",
]


def run(cmd):
    subprocess.run(cmd, capture_output=True)


def install_skills():
    print(f"Adding marketplace: {MARKETPLACE_REPO}")
    run(["claude", "plugin", "marketplace", "add", MARKETPLACE_REPO])

    for skill in SKILLS:
        print(f"Installing skill: {skill}@{MARKETPLACE_NAME}")
        run(["claude", "plugin", "install", f"{skill}@{MARKETPLACE_NAME}"])

    print("All g-claude skills installed.\n")


def install_karpathy():
    print(f"Adding marketplace: {KARPATHY_MARKETPLACE}")
    run(["claude", "plugin", "marketplace", "add", KARPATHY_MARKETPLACE])
    print(f"Installing plugin: {KARPATHY_PLUGIN}")
    run(["claude", "plugin", "install", KARPATHY_PLUGIN])
    print("karpathy-skills installed.\n")


def install_anthropic():
    print(f"Adding marketplace: {ANTHROPIC_MARKETPLACE}")
    run(["claude", "plugin", "marketplace", "add", ANTHROPIC_MARKETPLACE])
    for plugin in ANTHROPIC_PLUGINS:
        print(f"Installing plugin: {plugin}")
        run(["claude", "plugin", "install", plugin])
    print("anthropics/skills plugins installed.\n")


def install_context7(api_key):
    home = os.path.expanduser("~")

    print("Installing Context7 MCP for Claude Code...")
    run(["claude", "mcp", "add", "--scope", "user", "context7", "--",
         "npx", "-y", "@upstash/context7-mcp", "--api-key", api_key])
    print("Claude Code: context7 MCP added.")

    print("Installing Context7 MCP for OpenCode...")
    config_path = os.path.join(home, ".config", "opencode", "config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
        except Exception:
            pass

    config.setdefault("mcp", {})["context7"] = {
        "type": "local",
        "command": ["npx", "-y", "@upstash/context7-mcp", "--api-key", api_key],
        "enabled": True,
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("OpenCode: context7 MCP added.\n")


def main():
    args = sys.argv[1:]
    context7_key = None

    if "--context7-key" in args:
        idx = args.index("--context7-key")
        if idx + 1 < len(args):
            context7_key = args[idx + 1]
        else:
            print("Error: --context7-key requires a value")
            sys.exit(1)

    install_skills()
    install_karpathy()
    install_anthropic()

    if context7_key:
        install_context7(context7_key)
    else:
        print("Tip: pass --context7-key <KEY> to also install Context7 MCP.")


if __name__ == "__main__":
    main()
