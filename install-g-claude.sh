#!/bin/bash

# 脚本：将 g-claude 项目中的 md 文件注册为 Claude Code skill

SCRIPT_DIR="$(dirname "$0")"

# 注册 gen-commit-msg
SKILL_DIR="$HOME/.claude/skills/gen-commit-msg"
SOURCE_FILE="${SCRIPT_DIR}/gen-commit-msg.md"
mkdir -p "$SKILL_DIR"
cp "$SOURCE_FILE" "$SKILL_DIR/SKILL.md"
echo "已注册 skill: gen-commit-msg (/gen-commit-msg)"

# 注册 py-lint
SKILL_DIR="$HOME/.claude/skills/py-lint"
SOURCE_FILE="${SCRIPT_DIR}/py-lint.md"
mkdir -p "$SKILL_DIR"
cp "$SOURCE_FILE" "$SKILL_DIR/SKILL.md"
echo "已注册 skill: py-lint (/py-lint)"
