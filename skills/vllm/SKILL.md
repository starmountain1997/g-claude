---
name: vllm
description: vLLM/vLLM-Ascend 源码调试，通过阅读源码定位和解决问题
disable-model-invocation: true
argument-hint: "编译错误 / 运行报错 / ACLgraph 问题 / 源码定位"
---

vLLM/vLLM-Ascend 源码调试。

vLLM 和 vLLM-Ascend 都是通过 `pip install -e .` 源码安装的。

## 定位源码

1. 先通过 `pip show` 定位源码位置：
```bash
pip show vllm-ascend
```
查看 `Editable project location` 字段，即为源码所在目录。

2. 进入该目录，使用 Grep/Read 阅读源码定位问题。

请描述你遇到的具体问题，我会帮你定位源码并阅读分析。
