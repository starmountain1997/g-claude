#!/bin/bash
# Hermes 性能分析平台 - 启动脚本

set -e

cd "$(dirname "$0")"

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"
if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "Error: Python 3.11+ is required. Found: $python_version"
    exit 1
fi

# 检查依赖
if ! python3 -c "import msagent" 2>/dev/null; then
    echo "Error: msagent is not installed."
    echo "Install it with: pip install mindstudio-agent"
    exit 1
fi

# 加载 .env 文件（如果存在）
if [ -f .env ]; then
    echo "Loading environment from .env..."
    set -a
    source .env
    set +a
fi

# 检查必要的环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set"
fi

if [ -z "$OPENAI_API_BASE" ]; then
    echo "Warning: OPENAI_API_BASE is not set"
fi

echo "Starting msagent web service..."
echo "  Host: 127.0.0.1"
echo "  Port: 2026"
echo "  UI Port: 3000"
echo ""
echo "Press Ctrl+C to stop."
echo ""

python3 src/start_msagent.py
