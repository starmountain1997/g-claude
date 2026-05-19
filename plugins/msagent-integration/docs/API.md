# Hermes 性能分析平台 - API 接口文档

## 一、基础信息

- **服务地址**: http://localhost:8082
- **API 版本**: v1
- **Content-Type**: application/json（除非特别说明）

## 二、接口列表

### 1. 健康检查

| 属性 | 值 |
|------|-----|
| 路径 | `/health` |
| 方法 | `GET` |
| 描述 | 检查服务健康状态 |

**请求示例**:

```bash
curl http://localhost:8082/health
```

**响应示例**:

```json
{
    "status": "healthy",
    "service": "flask-backend",
    "version": "v2.3"
}
```

### 2. 文件上传

| 属性 | 值 |
|------|-----|
| 路径 | `/api/upload` |
| 方法 | `POST` |
| 描述 | 上传单个性能数据文件 |
| Content-Type | multipart/form-data |

**请求示例**:

```bash
curl -X POST http://localhost:8082/api/upload \
  -F "file=@op_summary.csv"
```

**响应示例**:

```json
{
    "filepath": "D:\\work\\uploads\\op_summary.csv",
    "filename": "op_summary.csv",
    "success": true
}
```

### 3. 文件夹上传

| 属性 | 值 |
|------|-----|
| 路径 | `/api/upload/folder` |
| 方法 | `POST` |
| 描述 | 上传整个性能数据文件夹 |
| Content-Type | multipart/form-data |

**请求示例**:

```bash
curl -X POST http://localhost:8082/api/upload/folder \
  -F "folder_name=profiler_data" \
  -F "files=@file1.csv" \
  -F "files=@file2.json"
```

**响应示例**:

```json
{
    "folder_path": "D:\\uploads\\abc12345",
    "file_count": 2,
    "success": true
}
```

### 4. 聊天接口（流式）

| 属性 | 值 |
|------|-----|
| 路径 | `/api/chat/stream` |
| 方法 | `POST` |
| 描述 | 流式聊天接口，支持实时响应 |
| Content-Type | text/event-stream |

**请求体**:

```json
{
    "message": "分析这个性能数据",
    "files": ["D:\\uploads\\abc12345\\op_summary.csv"]
}
```

**请求示例**:

```bash
curl -X POST http://localhost:8082/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "分析这个文件", "files": ["D:\\uploads\\test.csv"]}'
```

**响应（SSE 流式）**:

```
data: {"type": "tool_call", "tool_info": {"tool_name": "msprof-get-csv-info", "count": 1}, "thinking": "正在调用工具: msprof-get-csv-info...", "is_processing": true, "session_id": "session-xxx"}

data: {"type": "message", "content": "工具执行结果...", "tool_info": null, "is_processing": true, "session_id": "session-xxx"}

data: {"type": "message", "content": "最终回答内容", "tool_info": null, "is_processing": false, "session_id": "session-xxx"}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 消息类型：tool_call/message/error |
| content | string | 消息内容 |
| tool_info | object | 工具信息（tool_call 时存在） |
| thinking | string | 思考过程描述 |
| is_processing | boolean | 是否处理中（true=执行过程，false=最终回答） |
| session_id | string | 会话 ID |

### 5. 聊天接口（非流式）

| 属性 | 值 |
|------|-----|
| 路径 | `/api/chat` |
| 方法 | `POST` |
| 描述 | 非流式聊天接口，等待完整响应 |

**请求体**:

```json
{
    "message": "分析这个文件",
    "files": ["D:\\uploads\\test.csv"]
}
```

**响应示例**:

```json
{
    "response": "分析结果文本..."
}
```

### 6. 停止聊天

| 属性 | 值 |
|------|-----|
| 路径 | `/api/chat/stop` |
| 方法 | `POST` |
| 描述 | 停止正在执行的聊天任务 |

**请求体**:

```json
{
    "request_id": "session-xxx"
}
```

**响应示例**:

```json
{
    "success": true,
    "message": "任务已停止"
}
```

### 7. 分析接口

| 属性 | 值 |
|------|-----|
| 路径 | `/api/analyze` |
| 方法 | `POST` |
| 描述 | 分析性能数据文件 |

**请求体**:

```json
{
    "files": ["file1.csv", "file2.json"]
}
```

**响应示例**:

```json
{
    "response": "分析结果..."
}
```

## 三、错误响应格式

所有接口返回的错误格式统一：

```json
{
    "type": "error",
    "content": "错误描述信息",
    "error_code": "ERROR_CODE",
    "session_id": "session-xxx"
}
```

## 四、状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 五、示例代码

### Python 示例

```python
import requests
import json

# 文件上传
with open('op_summary.csv', 'rb') as f:
    response = requests.post('http://localhost:8082/api/upload', files={'file': f})
    print(response.json())

# 流式聊天
response = requests.post(
    'http://localhost:8082/api/chat/stream',
    json={'message': '分析这个文件', 'files': ['D:\\uploads\\test.csv']},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        print(data)
```

### JavaScript 示例

```javascript
// 文件上传
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8082/api/upload', {
    method: 'POST',
    body: formData
}).then(res => res.json()).then(console.log);

// 流式聊天
const response = await fetch('http://localhost:8082/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: '分析这个文件', files: ['D:\\uploads\\test.csv'] })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const data = JSON.parse(decoder.decode(value).replace('data: ', ''));
    console.log(data);
}
```
