#!/bin/bash

# 脚本：将 gen-commit-msg.md 注册为 Claude Code skill

SKILL_DIR="$HOME/.claude/skills/gen-commit-msg"
SOURCE_FILE="$(dirname "$0")/gen-commit-msg.md"

# 创建 skill 目录
mkdir -p "$SKILL_DIR"

# 复制文件为 SKILL.md
cp "$SOURCE_FILE" "$SKILL_DIR/SKILL.md"

echo "已注册 skill: gen-commit-msg"
echo "可通过 /gen-commit-msg 调用"
