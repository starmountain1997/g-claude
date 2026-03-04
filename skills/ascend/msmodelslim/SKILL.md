---
name: msmodelslim
description: msmodelslim 量化工具源码调试，通过阅读源码定位和解决问题
disable-model-invocation: true
argument-hint: "量化脚本编写 / 量化报错 / 模型结构咨询 / 源码调试"
---

msmodelslim (MindStudio ModelSlim) 昇腾模型压缩工具源码调试。

官方文档：https://msmodelslim.readthedocs.io/zh-cn/latest/

msmodelslim 通过 `pip install -e .` 源码安装。

## 定位源码

1. 先通过 `pip show` 定位源码位置：
```bash
pip show msmodelslim
```
查看 `Location` 字段，即为源码所在目录。

2. 进入该目录，使用 Grep/Read 阅读源码定位问题。

### 目录结构（git clone 的仓库）

## 量化新模型

当用户需要量化新模型时，按以下步骤进行：

### 1. 阅读已有示例
先阅读 `example/` 目录下其他模型的量化脚本，找到一个与待量化模型相近的模型脚本学习。


### 2. 了解模型结构

使用 `GIT_LFS_SKIP_SMUDGE=1` 克隆模型（只获取模型结构，不下载权重）。

优先从 ModelScope 下载，如果 ModelScope 没有再从 HuggingFace 下载：

```bash
# 优先尝试 ModelScope
GIT_LFS_SKIP_SMUDGE=1 git clone https://www.modelscope.cn/Qwen/QwQ-32B.git

# 如果 ModelScope 没有，再尝试 HuggingFace
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/Qwen/QwQ-32B
```

这样可以查看模型配置和结构，无需下载大量权重文件。

### 3. 比对模型结构
阅读 model.safetensors.index.json 或 config.json，了解：
- 模型架构 (Qwen2, Llama, MoE 等)
- 层数、hidden_size、num_attention_heads 等参数
- 是否为 MoE 模型

### 4. 编写量化脚本
参考已有示例，编写新模型的量化脚本。

### 5. 运行并调试
自己运行量化脚本：

```bash
cd /path/to/量化脚本目录
python 你的量化脚本.py
```

如果遇到问题：
1. 阅读报错信息，定位问题
2. 使用 Grep 搜索相关代码
3. 阅读源码理解原理
4. 修改脚本，反复调试直到成功

## 使用方法

请描述你遇到的具体问题，我会帮你定位源码并阅读分析。
