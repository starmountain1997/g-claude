#!/usr/bin/env python3
"""Install or update Claude skills via native `claude plugin` commands."""

import argparse
import logging
import subprocess


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# All plugins installed via native `claude plugin` commands.
# Format: { "github_repo": ("registered_name", ["plugin1", ...]) }
# - github_repo: "owner/repo" for `claude plugin marketplace add`
# - registered_name: canonical marketplace name for `claude plugin install`
COMMON_MARKETPLACES = {
    "starmountain1997/g-claude": (
        "g-claude",
        [
            "commit-as-prompt",
            "python-with-uv",
            "pythonic-code",
            "setup-neovim-plugin",
            "novel-writter",
        ],
    ),
    "forrestchang/andrej-karpathy-skills": (
        "karpathy-skills",
        ["andrej-karpathy-skills"],
    ),
    "asinkLuno/humanizer": ("humanizer", ["humanizer"]),
    "anthropics/skills": (
        "anthropic-agent-skills",
        ["document-skills", "example-skills"],
    ),
}

ASCEND_MARKETPLACES = {
    "starmountain1997/g-claude": (
        "g-claude",
        [
            "ascend",
            "aisbench",
            "model-download",
            "msmodeling",
            "msmodelslim",
            "vllm-ascend",
            "gitcode-publish",
        ],
    ),
}


def claude_plugin(*args):
    """Run native `claude plugin` command, log it, and return the output."""
    cmd = ["claude", "plugin", *args]
    logging.info("Running: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.warning(f"claude plugin command failed: {result.stderr.strip()}")
        return None
    return result.stdout.strip()


def setup_claude_plugins(if_ascend: bool = False):
    """Install plugins via native `claude plugin` commands."""
    marketplaces = ASCEND_MARKETPLACES if if_ascend else COMMON_MARKETPLACES

    for github_repo, (reg_name, plugins) in marketplaces.items():
        # Add the marketplace first (idempotent — safe to re-add).
        claude_plugin("marketplace", "add", github_repo)
        for plugin_name in plugins:
            claude_plugin("install", f"{plugin_name}@{reg_name}")


def main():
    parser = argparse.ArgumentParser(description="Manage Claude skills.")
    parser.add_argument(
        "--ascend", action="store_true", help="Use Ascend-specific plugin list"
    )
    args = parser.parse_args()

    setup_claude_plugins(args.ascend)


if __name__ == "__main__":
    main()
