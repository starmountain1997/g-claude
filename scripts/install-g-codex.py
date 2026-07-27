#!/usr/bin/env python3
"""Install or update Codex plugins via native `codex plugin` commands."""

import argparse
import logging
import subprocess


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# All plugins installed via native `codex plugin` commands.
# Format: { "github_repo": ("registered_name", ["plugin1", ...]) }
# - github_repo: "owner/repo" for `codex plugin marketplace add`
# - registered_name: canonical marketplace name for `codex plugin add`
COMMON_MARKETPLACES = {
    "starmountain1997/g-claude": (
        "g-claude",
        [
            "commit-as-prompt",
        ],
    ),
    "forrestchang/andrej-karpathy-skills": (
        "karpathy-skills",
        ["andrej-karpathy-skills"],
    ),
    "asinkLuno/humanizer": ("humanizer", ["humanizer"]),
    "axtonliu/axton-obsidian-visual-skills": (
        "obsidian-visual-skills",
        ["obsidian-visual-skills"],
    ),
    "asinkLuno/WEFT": ("weft", ["weft-yaml"]),
    "anthropics/skills": (
        "anthropic-agent-skills",
        ["document-skills", "example-skills"],
    ),
    "DietrichGebert/ponytail": ("ponytail", ["ponytail"]),
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

MARKETPLACE_REFS = {
    "asinkLuno/WEFT": "release",
}


def codex_plugin(*args):
    """Run a native `codex plugin` command, log it, and return the output."""
    cmd = ["codex", "plugin", *args]
    logging.info("Running: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.warning(f"codex plugin command failed: {result.stderr.strip()}")
        return None
    return result.stdout.strip()


def setup_codex_plugins(if_ascend: bool = False):
    """Install plugins via native `codex plugin` commands."""
    marketplaces = ASCEND_MARKETPLACES if if_ascend else COMMON_MARKETPLACES

    for github_repo, (reg_name, plugins) in marketplaces.items():
        # Add the marketplace first (idempotent — safe to re-add).
        marketplace_args = ["marketplace", "add", github_repo]
        if git_ref := MARKETPLACE_REFS.get(github_repo):
            marketplace_args.extend(["--ref", git_ref])
        codex_plugin(*marketplace_args)
        for plugin_name in plugins:
            codex_plugin("add", f"{plugin_name}@{reg_name}")

    if not if_ascend:
        subprocess.run(
            [
                "npx",
                "-y",
                "skills",
                "add",
                "vercel-labs/agent-skills",
                "--skill",
                "*",
                "--agent",
                "codex",
                "--global",
                "--yes",
            ]
        )


def main():
    parser = argparse.ArgumentParser(description="Manage Codex plugins.")
    parser.add_argument(
        "--ascend", action="store_true", help="Use Ascend-specific plugin list"
    )
    args = parser.parse_args()

    setup_codex_plugins(args.ascend)


if __name__ == "__main__":
    main()
