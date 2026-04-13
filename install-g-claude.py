#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.join(script_dir, "skills")

    # Remove and copy skills
    home = os.path.expanduser("~")

    claude_skills = os.path.join(home, ".claude", "skills")
    gemini_skills = os.path.join(home, ".gemini", "skills")

    shutil.rmtree(claude_skills, ignore_errors=True)
    shutil.rmtree(gemini_skills, ignore_errors=True)

    shutil.copytree(skills_dir, claude_skills)
    shutil.copytree(skills_dir, gemini_skills)

    print("所有 skills 注册完成")

    if len(sys.argv) < 2:
        print("用法: python install-g-claude.py <CONTEXT7_API_KEY>")
        sys.exit(1)

    context7_api_key = sys.argv[1]

    # Install Context7 MCP for Claude Code
    print("安装 Context7 MCP for Claude Code...")
    try:
        subprocess.run(
            ["claude", "mcp", "add", "--scope", "user", "context7", "--",
             "npx", "-y", "@upstash/context7-mcp", "--api-key", context7_api_key],
            capture_output=True,
        )
        print("Claude Code MCP context7 已添加")
    except Exception as e:
        print(f"Claude Code MCP 已存在或安装失败: {e}")

    # Install Context7 MCP for OpenCode
    print("安装 Context7 MCP for OpenCode...")
    opencode_config_path = os.path.join(home, ".config", "opencode", "config.json")
    os.makedirs(os.path.dirname(opencode_config_path), exist_ok=True)

    config = {}
    if os.path.exists(opencode_config_path):
        try:
            with open(opencode_config_path, "r") as f:
                config = json.load(f)
        except Exception:
            config = {}

    config.setdefault("mcp", {})["context7"] = {
        "type": "local",
        "command": ["npx", "-y", "@upstash/context7-mcp", "--api-key", context7_api_key],
        "enabled": True,
    }

    with open(opencode_config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("OpenCode MCP context7 已添加")
    print("Context7 MCP 安装完成")


if __name__ == "__main__":
    main()
