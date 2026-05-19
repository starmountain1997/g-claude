# Hermes 性能分析平台

基于 msagent 的 Ascend NPU 性能分析平台集成方案，提供智能对话和性能数据分析能力。

## 项目结构

```
msagent-integration/
├── backend/                    # 后端服务
│   └── backend.py              # Flask 后端服务
├── frontend/                   # 前端页面
│   └── agent-platform.html     # 性能调优平台前端
├── docs/                       # 文档
│   └── TECHNICAL_DESIGN.md     # 技术设计文档
└── README.md                   # 项目说明
```

## 快速开始

### 环境要求

- Python 3.11+
- msagent（mindstudio-agent）
- Flask 及相关依赖

### 安装依赖

```bash
# 安装 msagent
pip install mindstudio-agent

# 安装 Flask 及依赖
pip install flask requests flask-cors
```

### 启动服务

1. **启动 msagent web 服务**

```bash
# 设置环境变量
set OPENAI_API_KEY=<your-api-key>
set OPENAI_API_BASE=<your-api-base-url>

# 启动 msagent
msagent web
```

2. **启动 Flask 后端服务**

```bash
cd msagent-integration/backend
python backend.py
```

3. **访问前端页面**

```
在浏览器中打开：http://127.0.0.1:8082/agent-platform.html
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 & 后端 | http://127.0.0.1:8082/ |
| msagent API | http://127.0.0.1:2025 |

## 架构概览

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   前端界面       │     │   Flask 后端     │     │   msagent       │
│ agent-platform   │────▶│   :8082          │────▶│   :2025         │
│ .html            │     │                  │     │   Hermes Agent  │
└──────────────────┘     └────────┬─────────┘     └────────┬─────────┘
                                 │                        │
                                 ▼                        ▼
                          ┌──────────────┐      ┌──────────────────┐
                          │  uploads/    │      │   MCP Tools      │
                          │  文件存储    │◀─────│ msprof-mcp       │
                          └──────────────┘      └──────────────────┘
```

## API 接口

### 健康检查

```
GET /health
```

**响应示例：**

```json
{
    "status": "healthy",
    "service": "flask-backend"
}
```

### 文件上传

```
POST /api/upload
Content-Type: multipart/form-data

file: <文件>
```

**响应示例：**

```json
{
    "filepath": "D:\\work\\uploads\\op_summary.csv",
    "filename": "op_summary.csv"
}
```

### 文件夹上传

```
POST /api/upload/folder
Content-Type: multipart/form-data

files: <文件列表>
```

**响应示例：**

```json
{
    "folder_path": "D:\\work\\uploads\\abc12345",
    "file_count": 42
}
```

### 聊天接口（流式）

```
POST /api/chat/stream
Content-Type: application/json

{
    "message": "分析这个文件",
    "files": ["D:\\work\\uploads\\op_summary.csv"]
}
```

**响应头：**

```
X-Request-ID: <uuid>  # 用于后续停止请求的唯一标识
```

**响应（SSE 流式）：**

```
data: {"type": "tool_call", "tool_info": {"tool_name": "msprof-get-csv-info"}, "is_processing": true, "session_id": "<uuid>"}
data: {"type": "message", "content": "正在分析...", "is_processing": true, "session_id": "<uuid>"}
data: {"type": "message", "content": "最终回答内容", "is_processing": false, "session_id": "<uuid>"}
```

### 停止聊天接口

```
POST /api/chat/stop
Content-Type: application/json

{
    "request_id": "<uuid>"
}
```

**响应示例：**

```json
{
    "success": true,
    "message": "任务已停止"
}
```

### 分析接口

```
POST /api/analyze
Content-Type: application/json

{
    "files": ["file1.csv", "file2.json"]
}
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| OPENAI_API_KEY | 大模型 API Key | 需用户设置 |
| OPENAI_API_BASE | 大模型 API 地址 | 需用户设置 |
| MSAGENT_API_URL | msagent API 地址 | http://127.0.0.1:2025 |

### 模型配置

当前使用的模型：`glm-4.7`（可通过 msagent 配置切换）

## 功能特性

### 核心功能

- ✅ **智能对话**：支持与 Hermes 助手进行自然语言交互
- ✅ **流式输出**：支持 SSE 流式响应，实时显示 AI 生成内容（打字机效果）
- ✅ **上下文记忆**：支持多轮对话上下文记忆
- ✅ **思考过程显示**：实时显示 Agent 的思考过程和工具调用，默认展开
- ✅ **分步显示**：每个工具调用独立显示，向下新增不覆盖
- ✅ **折叠/展开**：思考过程可折叠查看，节省界面空间
- ✅ **内容分类显示**：区分工具调用、执行过程、日志数据和最终回答
- ✅ **执行过程滚动窗口**：工具执行结果显示在带标题的滚动窗口中（高度限制）
- ✅ **文件夹上传**：支持上传整个性能数据文件夹，保留结构
- ✅ **性能数据分析**：上传性能数据文件进行分析
- ✅ **文件自动上传**：发送消息时自动上传已选择的文件

### 界面特性

- 🎨 **现代化 UI**：渐变色设计，流畅的动画效果
- 📎 **文件上传**：支持拖拽上传，显示文件列表
- 💬 **对话气泡**：用户消息和 AI 消息区分显示
- 🤖 **思考过程卡片**：卡片式布局，清晰展示处理步骤
- 📊 **状态指示**：服务连接状态实时显示
- 📋 **执行过程标题**：工具调用过程带明确的"执行过程"小标题

### 技术特性

- 🔧 **MCP 工具集成**：支持多种性能分析工具
- 🔄 **错误处理**：完善的错误处理和状态反馈
- 📝 **Unicode 支持**：正确处理中文显示，修复编码问题
- 🎯 **工具名称解析**：支持多种数据结构，自动去重
- 🔀 **消息分类**：智能区分工具调用开始、工具执行结果、最终回答

## 支持的 MCP 工具

| 工具名 | 功能描述 |
|--------|----------|
| msprof-get-csv-info | 获取 CSV 文件基本信息 |
| msprof-execute-sql-query | 执行 SQL 查询 |
| msprof-analyze-advisor | 综合性能分析 |
| msprof-find-slices | 在 trace_view.json 中搜索切片 |
| msprof-get-operator-details | 获取算子详细信息 |
| msprof-get-op-type-details | 获取算子类型统计 |
| msprof-analyze-overlap | 分析 Overlap 过程 |
| ls | 列出目录文件 |
| read_file | 读取文件内容 |

## 技术架构

### 三层架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     前端应用                                        │
│  - 文件上传模块  - 智能对话模块  - 分析结果展示  - 思考过程展示     │
│  - 内容分类渲染  - 流式输出处理                                     │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTP REST API
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Flask 后端服务                            │
│  - API 路由层  - 文件处理层  - msagent 代理层  - 流式数据处理层    │
│  - 消息分类层  - 会话管理层                                        │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTP REST API
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       msagent web 服务                           │
│  - LangGraph API Server  - Hermes Agent  - MCP 工具调用  - LLM    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ API
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          大模型服务                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | HTML + CSS + JavaScript | 响应式界面，无框架依赖 |
| 后端 | Flask + Python | 轻量级 Web 框架 |
| 通信 | SSE (Server-Sent Events) | 流式数据传输 |
| AI | msagent + MCP | Agent 框架和工具集成 |
| 模型 | GLM-4.7 (或 Qwen2.5-7B-Instruct) | 大语言模型 |

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| **v2.3** | 2026-05-11 | **消息分类优化**：修复工具调用结果和最终回答的分类问题，添加 `tool_in_progress` 状态追踪，确保工具结果显示在执行过程区域，最终回答正确显示 |
| **v2.2** | 2026-05-11 | **思考过程默认展开**：用户可实时看到工具调用和执行过程，支持点击折叠/展开 |
| **v2.1** | 2026-05-11 | **流式输出修复**：修复 LangGraph 流式格式解析，实现真正的流式输出打字机效果 |
| v2.0 | 2026-05-10 | **文件夹上传**：实现文件夹上传功能，支持 webkitdirectory，保留文件夹结构，使用短 UUID 避免路径过长 |
| v1.9 | 2026-05-10 | **停止机制**：实现真正的停止机制，添加任务管理和超时处理 |
| v1.8 | 2026-05-09 | **重复回答修复**：修复重复回答问题，实现增量内容更新 |
| v1.7 | 2026-05-09 | **工具名称解析**：优化工具名称解析，支持多种数据格式，添加去重机制 |
| v1.6 | 2026-05-08 | **分步显示**：修复内容覆盖问题，实现分步显示 |
| v1.5 | 2026-05-08 | **Unicode 修复**：修复 Unicode 编码问题 |
| v1.4 | 2026-05-08 | **折叠功能**：添加思考过程折叠/展开功能 |
| v1.3 | 2026-05-07 | **思考过程显示**：实现思考过程显示 |
| v1.2 | 2026-05-07 | **上下文记忆**：添加上下文记忆功能 |
| v1.1 | 2026-05-07 | **流式输出**：实现 SSE 流式输出 |
| v1.0 | 2026-05-07 | **初始版本**：基础功能实现 |

## 依赖关系

```
前端页面 (8082)
    ↓ HTTP
Flask 后端 (8082)
    ↓ HTTP
msagent web (2025)
    ↓ API
大模型服务
```

## 技术文档

详细的技术设计文档请参考：[TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md)

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 前端无法连接后端 | CORS 配置问题 | 检查 Flask 后端 CORS 配置 |
| msagent 连接失败 | OPENAI_API_KEY 未设置 | 设置环境变量 |
| 文件上传失败 | 文件大小限制或权限问题 | 检查上传目录权限 |
| 响应超时 | 网络问题或模型响应慢 | 增加超时时间 |
| 流式输出不显示 | JSON 解析失败 | 检查后端日志 |
| Unicode 显示乱码 | 编码问题 | 更新到最新版本 |
| 思考过程无法点击 | 事件冒泡问题 | 更新到最新版本 |
| 内容被覆盖 | 容器复用问题 | 更新到最新版本 |
| 最终回答不显示 | 消息分类错误 | 更新到 v2.3+ |
| 工具结果显示异常 | tool_in_progress 状态问题 | 更新到 v2.3+ |

### 日志查看

```bash
# 检查 msagent web 服务状态
curl http://127.0.0.1:2025/health

# 检查 Flask 后端状态
curl http://127.0.0.1:8082/health

# 检查前端页面
curl http://127.0.0.1:8082/agent-platform.html
```

## 许可证

MIT License
