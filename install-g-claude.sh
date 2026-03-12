#!/bin/bash

SCRIPT_DIR="$(dirname "$0")"
SKILLS_DIR="${SCRIPT_DIR}/skills"

rm -rf "$HOME/.claude/skills"
cp -r "$SKILLS_DIR" "$HOME/.claude/skills"

echo "所有 skills 注册完成"

if [ -z "$1" ]; then
    echo "用法: $0 <CONTEXT7_API_KEY>"
    exit 1
fi

CONTEXT7_API_KEY="$1"

echo "安装 Context7 MCP for Claude Code..."
claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key "$CONTEXT7_API_KEY" 2>/dev/null || echo "Claude Code MCP 已存在或安装失败"

echo "安装 Context7 MCP for OpenCode..."
OPENCODE_CONFIG="$HOME/.config/opencode/config.json"
mkdir -p "$(dirname "$OPENCODE_CONFIG")"

if [ -f "$OPENCODE_CONFIG" ]; then
    if grep -q "context7" "$OPENCODE_CONFIG" 2>/dev/null; then
        echo "OpenCode MCP context7 已存在"
    else
        cat > "$OPENCODE_CONFIG.tmp" << EOF
{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp", "--api-key", "$CONTEXT7_API_KEY"],
      "enabled": true
    }
  }
}
EOF
        python3 -c "
import json
import sys
try:
    with open('$OPENCODE_CONFIG', 'r') as f:
        config = json.load(f)
except:
    config = {}
config.setdefault('mcp', {})['context7'] = {
    'type': 'local',
    'command': ['npx', '-y', '@upstash/context7-mcp', '--api-key', '$CONTEXT7_API_KEY'],
    'enabled': True
}
with open('$OPENCODE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
        rm -f "$OPENCODE_CONFIG.tmp"
        echo "OpenCode MCP context7 已添加"
    fi
else
    cat > "$OPENCODE_CONFIG" << EOF
{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp", "--api-key", "$CONTEXT7_API_KEY"],
      "enabled": true
    }
  }
}
EOF
    echo "OpenCode MCP context7 已创建"
fi

echo "Context7 MCP 安装完成"
