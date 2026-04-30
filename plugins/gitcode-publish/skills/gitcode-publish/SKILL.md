---
name: gitcode-publish
description: Publish model README to GitCode with auto-inferred YAML frontmatter tags. Use this skill whenever the user mentions pushing/publishing a model to GitCode, uploading model documentation, adding frontmatter tags to a model README, or preparing a model card for GitCode. Even if they don't say "GitCode" explicitly, trigger when they talk about tagging a model README with HuggingFace-style metadata.
---

# GitCode 模型发布

为模型 README.md 自动推断并添加 YAML frontmatter 标签，然后推送到 GitCode 仓库。

## 工作流程

### 1. 确认两个路径

README 和模型是分开的两个路径，分别询问用户：

**第一步：询问 README 路径**

要发布的 README.md 文件在哪里？支持：

- **本地文件**：`/path/to/README.md` 或 `./my-model/README.md`
- **目录**：`/path/to/model/`（自动找目录下的 `README.md`）
- **新建**：如果用户还没有 README，从模型配置自动生成一个

**第二步：询问模型路径**

模型文件在哪里？支持：

- **HuggingFace model ID**：`Qwen/Qwen2-VL-7B-Instruct`（可从 API 直接拉取真实标签和元数据）
- **ModelScope model ID**：`damo/nlp_structbert_backbone_base_std`（同样可从 API 拉取元数据）
- **本地路径**：`/path/to/model/` 或 `~/.cache/huggingface/hub/models--xxx/`

这两个路径可以相同（README 在模型目录下），也可以完全不同（README 在其他地方编辑，模型在 HF cache 中）。

### 2. 获取模型元数据

**优先级：平台 API > 本地 config 推断**

根据步骤1中的模型路径类型，选择对应的数据源。

#### 2a. HuggingFace model ID → 用 API 获取真实标签

HuggingFace Hub API 返回的 `pipeline_tag`、`tags`、`library_name`、`license` 就是平台上的真实值，无需猜测：

```bash
curl -sL "https://huggingface.co/api/models/MODEL_ID" | python3 -c "
import sys, json
d = json.load(sys.stdin)
card = d.get('cardData', {}) or {}
result = {
    'pipeline_tag': d.get('pipeline_tag', ''),
    'tags': d.get('tags', []),
    'library_name': d.get('library_name', ''),
    'license': card.get('license', ''),
    'model_type': d.get('config', {}).get('model_type', '') if d.get('config') else '',
}
print(json.dumps(result, indent=2, ensure_ascii=False))
"
```

如果 HuggingFace 不可达（网络问题），用 `https://hf-mirror.com` 镜像：

```bash
curl -sL "https://hf-mirror.com/api/models/MODEL_ID" | python3 -c "..."  # 同上
```

#### 2b. ModelScope model ID → 用 API 获取真实标签

```bash
curl -sL "https://modelscope.cn/api/v1/models/MODEL_ID" | python3 -c "
import sys, json
d = json.load(sys.stdin).get('Data', {})
tasks = d.get('Tasks', [])
result = {
    'pipeline_tag': tasks[0].get('Name', '') if tasks else '',
    'tags': d.get('Tags', []),
    'library_name': d.get('Libraries', [''])[0] if d.get('Libraries') else '',
    'license': d.get('License', ''),
    'model_type': d.get('ModelType', [''])[0] if d.get('ModelType') else '',
}
print(json.dumps(result, indent=2, ensure_ascii=False))
"
```

ModelScope API 字段映射：`Tasks[0].Name` → `pipeline_tag`，`Tags` → `tags`，`License` 是可直接使用的许可证文本。

#### 2c. 本地路径 → 从 config.json 推断

先安装检查依赖（如果还没装）：

```bash
python3 -c "from transformers import AutoConfig; print('ok')" 2>&1 || pip3 install transformers --quiet
```

读取模型配置并推断：

```bash
python3 << 'PYEOF'
import json, os

MODEL_PATH = "MODEL_PATH"

from transformers import AutoConfig
config = AutoConfig.from_pretrained(MODEL_PATH, trust_remote_code=True)

result = {
    "model_type": config.model_type,
    "pipeline_tag": "",  # 步骤3中根据映射表推断
    "tags": [],
    "library_name": "transformers",
    "license": "",
    "architectures": getattr(config, 'architectures', None) or [],
}

print(json.dumps(result, indent=2, ensure_ascii=False))
PYEOF
```

#### 2d. 无论哪种方式，都需要读取模型 config（用于步骤5的 README 生成）

如果模型路径是 HF model ID 且本地没有缓存，只下载配置文件（不下载权重）：

```bash
python3 -c "
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from huggingface_hub import snapshot_download
snapshot_download('MODEL_ID', allow_patterns=['config.json', '*.md', 'tokenizer_config.json', 'preprocessor_config.json'], local_dir='/tmp/model-temp')
"
```

然后用 `/tmp/model-temp` 的 config.json 补充模型信息。

### 3. 映射 pipeline_tag（仅本地路径需要）

**如果已从 API 获取了 `pipeline_tag`，跳过此步骤。**

读取 `references/pipeline_tags.md` 中的映射表，根据 `model_type` 找到对应的 `pipeline_tag`。

如果 `model_type` 在映射表中找不到，按以下优先级推断：

- model_type 包含 `vl` → `image-text-to-text`
- model_type 包含 `audio`/`speech` → `automatic-speech-recognition`
- model_type 属于编码器模型（bert/roberta/deberta/electra）→ `fill-mask`
- 都不匹配 → 询问用户手动指定

映射完成后，将标准 tags 补充进 `tags` 字段：`["transformers", "<pipeline_tag>", ...architectures]`。

### 4. 展示并确认标签

将推断结果展示给用户。用表格形式：

```
| 字段 | 值 |
|------|-----|
| library_name | transformers |
| pipeline_tag | image-text-to-text |
| tags | transformers, image-text-to-text, pytorch, qwen2_vl, Qwen2VLForConditionalGeneration |
| license | apache-2.0 |
```

让用户确认或修改。用户可以：

- 直接确认，继续下一步
- 修改某个字段的值
- 添加额外字段（如 `license_name`、`datasets`、`metrics` 等）

### 5. 智能合并 README frontmatter

读取用户指定的 `README.md` 文件（注意：不是模型路径下的 README，而是步骤1中用户指定的 README 路径）：

**如果 README 不存在**：创建一个只有 YAML frontmatter 的新文件。

**如果 README 存在但没有 YAML frontmatter**（不以 `---` 开头）：在文件最开头插入 frontmatter。

**如果 README 已有 YAML frontmatter**：智能合并——保留用户手动添加的字段（如自定义 `license_name`），只更新自动推断的字段值。判断依据：

- 自动推断的字段（`library_name`、`pipeline_tag`、`tags`）用新值覆盖
- 如果用户已手动设置 `license`，保留用户的值
- 用户自定义的字段（不在自动推断列表中的）原样保留

最终写入的格式：

```markdown
---
tags:
- transformers
- image-text-to-text
- pytorch
library_name: transformers
pipeline_tag: image-text-to-text
license: apache-2.0
---
[原有 README 内容...]
```

YAML 格式要求：

- `tags` 用列表格式（每行 `- tag-name`），写在最前面
- 其他字段用 `key: value` 格式
- `---` 分隔符独占一行
- frontmatter 结束后空一行再接正文

### 6. 创建或关联 GitCode 仓库

询问用户：**"创建新仓库还是使用已有仓库？"**

#### 选项 A：创建新仓库（通过 API）

Token 从环境变量 `ATOMGIT_USER_TOKEN` 自动读取。如果未设置直接退出。

然后询问：

- **仓库名称**（name）：如 `"Qwen2-VL-7B-Instruct"`
- **仓库路径**（path）：如 `"qwen2-vl-7b-instruct"`（默认与 name 相同）
- **是否私有**（private）：默认 `false`（公开）

调用 API 创建模型仓库：

```bash
curl --location 'https://api.gitcode.com/api/v5/user/repos' \
  --header "private-token: $ATOMGIT_USER_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "<REPO_NAME>",
    "path": "<REPO_PATH>",
    "private": false,
    "repository_type": "model"
  }'
```

仓库地址直接用 token 构造，无需从 API 返回值提取：

```
REPO_URL="https://auth:${ATOMGIT_USER_TOKEN}@gitcode.com/<REPO_PATH>.git"
```

#### 选项 B：使用已有仓库

询问用户仓库路径（如 `yanlp/demo1-1`），然后同样构造带认证的地址：

```
REPO_URL="https://auth:${ATOMGIT_USER_TOKEN}@gitcode.com/<路径>.git"
```

### 7. 推送到 GitCode

```bash
# 初始化 git（在 README 所在目录操作）
cd README_DIR
git init

# 添加 GitCode 远程仓库（URL 已含 token，无需额外认证）
git remote add origin REPO_URL || git remote set-url origin REPO_URL

# 只提交 README.md
git add README.md
git commit -m "publish: add model card with auto-inferred tags"

# 推送到 GitCode（假设 main 分支）
git push -u origin main
```

## 注意事项

- **标签来源优先级**：平台 API > 本地 config 推断。HF/ModelScope API 返回的是平台上真实使用的标签，比本地推断更准确。
- 整个过程不接触模型权重文件（`.safetensors`、`.bin`、`.pt` 等），只操作配置文件和 API 查询
- 如果 `tags` 中包含 `license:xxx` 格式的标签，可将其提取为独立的 `license` 字段
- 如果用户模型不是 transformers 架构（如 MLX、GGUF），告知用户此 skill 当前只支持 transformers 格式的模型卡
- HF API 返回的 tags 包含平台自动标签（`transformers`、`safetensors`、`pytorch`、`text-generation` 等）和用户自定义标签，应完整保留
