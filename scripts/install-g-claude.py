#!/usr/bin/env python3
"""Install or update Claude skills and optional extras."""

import argparse
import json
import os
import subprocess

# Dictionary mapping 'Marketplace Repo' to 'List of Plugins'
PLUGINS = {
    "starmountain1997/g-claude": [
        "ascend",
        "vllm-ascend",
        "msmodelslim",
        "aisbench",
        "commit-as-prompt",
        "setup-neovim-plugin",
    ],
    "forrestchang/andrej-karpathy-skills": ["andrej-karpathy-skills@karpathy-skills"],
    "anthropics/skills": ["document-skills@anthropic-agent-skills", "example-skills@anthropic-agent-skills"],
}


def claude(*args):
    """Helper to run Claude CLI commands silently."""
    subprocess.run(["claude", *args], capture_output=True)


def setup_plugins(update=False):
    """Installs or updates all configured marketplaces and plugins."""
    action = "update" if update else "install"

    for repo, items in PLUGINS.items():
        if not update:
            print(f"Adding marketplace: {repo}")
            claude("plugin", "marketplace", "add", repo)

        for item in items:
            # Auto-append the marketplace name if no '@' is specified
            plugin = item if "@" in item else f"{item}@{repo.split('/')[-1]}"
            print(f"{action.title()}ing plugin: {plugin}")
            claude("plugin", action, plugin)

    print(f"\nAll skills successfully {action}ed.")


def install_context7(api_key):
    """Installs Context7 MCP for both Claude Code and OpenCode."""
    print("\nInstalling Context7 MCP for Claude Code...")
    claude(
        "mcp",
        "add",
        "--scope",
        "user",
        "context7",
        "--",
        "npx",
        "-y",
        "@upstash/context7-mcp",
        "--api-key",
        api_key,
    )

    print("Installing Context7 MCP for OpenCode...")
    conf_path = os.path.expanduser("~/.config/opencode/config.json")
    os.makedirs(os.path.dirname(conf_path), exist_ok=True)

    config = {}
    if os.path.exists(conf_path):
        with open(conf_path, "r") as f:
            try:
                config = json.load(f)
            except ValueError:
                pass

    config.setdefault("mcp", {})["context7"] = {
        "type": "local",
        "enabled": True,
        "command": ["npx", "-y", "@upstash/context7-mcp", "--api-key", api_key],
    }

    with open(conf_path, "w") as f:
        json.dump(config, f, indent=2)

    print("Context7 MCP installation complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Claude skills and Context7 MCP."
    )
    parser.add_argument(
        "--update", action="store_true", help="Update skills instead of installing"
    )
    parser.add_argument("--context7-key", help="API key to install Context7 MCP")
    args = parser.parse_args()

    setup_plugins(args.update)

    if args.context7_key:
        install_context7(args.context7_key)
    elif not args.update:
        print("Tip: pass --context7-key <KEY> to also install Context7 MCP.")


if __name__ == "__main__":
    main()
