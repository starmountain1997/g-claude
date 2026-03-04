---
name: msmodelslim
description: msmodelslim 量化工具，使用一键量化或编写脚本
disable-model-invocation: true
argument-hint: "模型量化 / 量化报错 / 模型结构咨询 / 源码调试"
---

msmodelslim (MindStudio ModelSlim) 昇腾模型压缩工具。

官方文档：https://msmodelslim.readthedocs.io/zh-cn/latest/

## 一键量化（优先使用）

推荐先尝试[一键量化](https://msmodelslim.readthedocs.io/zh-cn/latest/zh/feature_guide/quick_quantization_v1/usage/)，命令格式：`msmodelslim quant [ARGS]`

使用 `-h` 参数查看帮助，了解可用参数：

```bash
msmodelslim quant -h
```

或者阅读[官方文档](https://msmodelslim.readthedocs.io/zh-cn/latest/zh/feature_guide/quick_quantization_v1/usage/)确定参数后执行。

由于量化十分耗时，当确定参数之后，可以杀掉进程，然后将正确的运行参数告诉用户，让用户自行运行。

## 编写量化脚本

如果一键量化不满足需求，再自己编写脚本。

### 1. 阅读官方文档

### 2. 了解模型结构

使用 `GIT_LFS_SKIP_SMUDGE=1` 克隆模型（只获取模型结构，不下载权重）。

优先从 ModelScope 下载，如果 ModelScope 没有再从 HuggingFace 下载：

```bash
# 优先尝试 ModelScope
GIT_LFS_SKIP_SMUDGE=1 git clone https://www.modelscope.cn/Qwen/QwQ-32B.git

# 如果 ModelScope 没有，再尝试 HuggingFace
GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/Qwen/QwQ-32B
```

### 3. 比对模型结构
阅读 config.json，了解：
- 模型架构 (Qwen2, Llama, MoE 等)
- 层数、hidden_size、num_attention_heads 等参数
- 是否为 MoE 模型

### 4. 编写脚本
参考 `example/` 目录下其他模型的量化脚本，找到一个与待量化模型相近的脚本学习。

### 5. 运行并调试

如果遇到问题：
1. 阅读报错信息
2. 使用 Grep 搜索相关代码
3. 阅读源码理解原理

## 源码定位

如果需要定位问题，通过 pip show 查看源码位置：

```bash
pip show msmodelslim
```

请描述你遇到的具体问题。
