#!/usr/bin/env python3
"""Install or update Claude skills and remove any extras not in the list."""

import argparse
import logging
import subprocess
import re


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

COMMON_PLUGINS = {
    "starmountain1997/g-claude": [
        "commit-as-prompt",
        "python-with-uv",
        "pythonic-code",
        "setup-neovim-plugin",
    ],
    "forrestchang/andrej-karpathy-skills": ["andrej-karpathy-skills@karpathy-skills"],
    "anthropics/skills": [
        "document-skills@anthropic-agent-skills",
        "example-skills@anthropic-agent-skills",
    ],
}
ASCEND_PLUGINS = {
    "starmountain1997/g-claude": [
        "ascend",
        "aisbench",
        "model-download",
        "msmodeling",
        "msmodelslim",
        "vllm-ascend",
    ],
}


def opkg(*args):
    """Run Claude CLI command, log it, and return the output."""
    cmd = ["opkg", "install", *args]
    logging.info("Running: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Command failed: {result.stderr.strip()}")
        raise RuntimeError(f"claude command failed: {result.stderr}")
    return result.stdout.strip()


def setup_claude_plugins(platforms: str, if_ascend: bool = False):
    """Install/update and then remove plugins not in the list."""
    plugins = ASCEND_PLUGINS if if_ascend else COMMON_PLUGINS

    for repo, items in plugins.items():
        for item in items:
            args = [f"gh@{repo}", "--plugins", item, "--platforms", platforms]
            opkg(*args)


def main():
    parser = argparse.ArgumentParser(description="Manage Claude skills.")
    parser.add_argument("--platforms", default="opencode")
    parser.add_argument(
        "--ascend", action="store_true", help="Use Ascend-specific plugin list"
    )
    args = parser.parse_args()

    setup_claude_plugins(args.platforms, args.ascend)


if __name__ == "__main__":
    main()
