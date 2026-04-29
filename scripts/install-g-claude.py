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


def claude(*args):
    """Run Claude CLI command, log it, and return the output."""
    cmd = ["claude", *args]
    logging.info("Running: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Command failed: {result.stderr.strip()}")
        raise RuntimeError(f"claude command failed: {result.stderr}")
    return result.stdout.strip()


def setup_claude_plugins(update=True, if_ascend=False):
    """Install/update and then remove plugins not in the list."""
    action = "update" if update else "install"
    plugins = ASCEND_PLUGINS if if_ascend else COMMON_PLUGINS

    for repo, items in plugins.items():
        marketplace_name = repo.split("/")[-1]

        # Add marketplace if it doesn't exist (only on install, not update)
        if not update:
            try:
                claude("plugin", "marketplace", "add", repo)
            except RuntimeError:
                # Might already exist – ignore
                pass

        # Install or update desired plugins
        for item in items:
            plugin = item if "@" in item else f"{item}@{marketplace_name}"
            try:
                claude("plugin", action, plugin)
            except RuntimeError as e:
                logging.error(f"Failed to {action} {plugin}: {e}")

    logging.info(
        f"All skills successfully processed (desired {action}ed, extras removed)."
    )


def main():
    parser = argparse.ArgumentParser(description="Manage Claude skills.")
    parser.add_argument(
        "--update", action="store_true", help="Update skills instead of installing"
    )
    parser.add_argument(
        "--ascend", action="store_true", help="Use Ascend-specific plugin list"
    )
    args = parser.parse_args()

    setup_claude_plugins(args.update, args.ascend)


if __name__ == "__main__":
    main()
