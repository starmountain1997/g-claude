#!/usr/bin/env python3
"""Install or update Claude skills and remove any extras not in the list."""

import argparse
import logging
import subprocess


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Plugins installed via opkg (OpenPackage).
COMMON_PLUGINS = {
    "starmountain1997/g-claude": [
        "commit-as-prompt",
        "python-with-uv",
        "pythonic-code",
        "setup-neovim-plugin",
        "novel-writter",
    ],
    "forrestchang/andrej-karpathy-skills": ["andrej-karpathy-skills@karpathy-skills"],
    "asinkLuno/humanizer": ["humanizer"],
    "asinkLuno/Humanizer-zh": ["Humanizer-zh"],
}

# Marketplaces installed via native `claude plugin` commands.
# Format: { "owner/repo": ["plugin@marketplace", ...] }
NATIVE_MARKETPLACES = {
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
        "gitcode-publish",
    ],
}


def opkg(*args):
    """Run opkg install command, log it, and return the output."""
    cmd = ["opkg", "install", *args]
    logging.info("Running: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"opkg command failed: {result.stderr.strip()}")
        raise RuntimeError(f"opkg command failed: {result.stderr}")
    return result.stdout.strip()


def claude_plugin(*args):
    """Run native `claude plugin` command, log it, and return the output."""
    cmd = ["claude", "plugin", *args]
    logging.info("Running: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.warning(f"claude plugin command failed: {result.stderr.strip()}")
        return None
    return result.stdout.strip()


def setup_claude_plugins(platforms: str, if_ascend: bool = False):
    """Install/update plugins via opkg."""
    plugins = ASCEND_PLUGINS if if_ascend else COMMON_PLUGINS

    for repo, items in plugins.items():
        for item in items:
            args = [f"gh@{repo}", "--plugins", item, "--platforms", platforms]
            opkg(*args)


def setup_native_marketplaces():
    """Install plugins via native `claude plugin` commands (no opkg)."""
    for marketplace, plugins in NATIVE_MARKETPLACES.items():
        # Add the marketplace first (idempotent — safe to re-add).
        claude_plugin("marketplace", "add", marketplace)
        for plugin_ref in plugins:
            claude_plugin("install", plugin_ref)


def main():
    parser = argparse.ArgumentParser(description="Manage Claude skills.")
    parser.add_argument("--platforms", default="opencode")
    parser.add_argument(
        "--ascend", action="store_true", help="Use Ascend-specific plugin list"
    )
    args = parser.parse_args()

    setup_claude_plugins(args.platforms, args.ascend)
    setup_native_marketplaces()


if __name__ == "__main__":
    main()
