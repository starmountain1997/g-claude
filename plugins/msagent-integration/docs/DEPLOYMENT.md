# Hermes 性能分析平台 - 部署指南

## 一、环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 后端服务运行环境 |
| msagent | latest | mindstudio-agent 包 |
| Flask | 2.0+ | Web 框架 |

## 二、快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 进入项目目录
cd msagent-integration

# 2. 复制配置文件并填写参数
cp .env.example .env
# 编辑 .env 文件，填写 OPENAI_API_KEY 和 OPENAI_API_BASE

# 3. 启动服务
docker-compose up -d

# 4. 检查服务状态
curl http://localhost:8082/health

# 5. 访问前端页面
# 浏览器打开: http://localhost:8082/agent-platform.html
```

### 方式二：源码部署

```bash
# 1. 进入项目目录
cd msagent-integration/backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
set OPENAI_API_KEY=<your-api-key>
set OPENAI_API_BASE=<your-api-base-url>

# 4. 启动 msagent
msagent web

# 5. 启动 Flask 后端
python backend.py

# 6. 访问前端页面
# 浏览器打开: http://localhost:8082/agent-platform.html
```

## 三、配置说明

### 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| OPENAI_API_KEY | 是 | - | 大模型 API Key |
| OPENAI_API_BASE | 是 | - | 大模型 API 地址 |
| MSAGENT_API_URL | 否 | http://127.0.0.1:2025 | msagent 服务地址 |
| PORT | 否 | 8082 | Flask 服务端口 |
| UPLOAD_FOLDER | 否 | uploads | 文件上传目录 |

### 配置文件

创建 `.env` 文件：

```bash
# .env 文件内容
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=your-api-base-url
MSAGENT_API_URL=http://127.0.0.1:2025
PORT=8082
```

## 四、服务管理

### 启动服务

```bash
# Docker 方式
docker-compose up -d

# 源码方式
python backend.py
```

### 停止服务

```bash
# Docker 方式
docker-compose down

# 源码方式
# 按 Ctrl+C 停止
```

### 查看日志

```bash
# Docker 方式
docker-compose logs -f

# 源码方式
# 日志直接输出到控制台
```

## 五、健康检查

```bash
# 检查后端服务
curl http://localhost:8082/health

# 检查 msagent 服务
curl http://localhost:2025/health
```

## 六、端口说明

| 服务 | 端口 | 配置位置 |
|------|------|----------|
| Flask 后端 | 8082 | .env 或 PORT 环境变量 |
| msagent web | 2025 | msagent 默认端口 |

## 七、故障排查

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 服务无法启动 | 端口被占用 | 修改 PORT 环境变量 |
| 连接 msagent 失败 | msagent 未启动 | 先启动 msagent web |
| 文件上传失败 | 权限不足 | 检查 uploads 目录权限 |
| API 调用失败 | API Key 错误 | 检查 OPENAI_API_KEY |

### 日志查看

```bash
# 查看后端日志
docker-compose logs backend

# 查看 msagent 日志
docker-compose logs msagent
```
