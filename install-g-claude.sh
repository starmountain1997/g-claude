#!/bin/bash

# 脚本：将 g-claude 项目中的 skills 注册为 Claude Code skill

SCRIPT_DIR="$(dirname "$0")"
SKILLS_DIR="${SCRIPT_DIR}/skills"

# 整体拷贝覆盖
rm -rf "$HOME/.claude/skills"
cp -r "$SKILLS_DIR" "$HOME/.claude/skills"

echo "所有 skills 注册完成"
