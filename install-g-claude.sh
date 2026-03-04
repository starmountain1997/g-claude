#!/bin/bash

# 脚本：将 g-claude 项目中的 skills 注册为 Claude Code skill

SCRIPT_DIR="$(dirname "$0")"
SKILLS_DIR="${SCRIPT_DIR}/skills"

# 注册 gen-commit-msg
SKILL_DIR="$HOME/.claude/skills/gen-commit-msg"
SOURCE_FILE="${SKILLS_DIR}/gen-commit-msg.md"
mkdir -p "$SKILL_DIR"
cp "$SOURCE_FILE" "$SKILL_DIR/SKILL.md"
echo "已注册 skill: gen-commit-msg (/gen-commit-msg)"

# 注册 python-test-flow
SKILL_DIR="$HOME/.claude/skills/python-test-flow"
SOURCE_FILE="${SKILLS_DIR}/python-test-flow/python-test-flow.md"
mkdir -p "$SKILL_DIR/scripts"
cp "$SOURCE_FILE" "$SKILL_DIR/SKILL.md"
cp -r "${SKILLS_DIR}/python-test-flow/scripts/"* "$SKILL_DIR/scripts/"
echo "已注册 skill: python-test-flow (/python-test-flow)"
