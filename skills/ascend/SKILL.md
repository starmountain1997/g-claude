---
name: ascend
description: Ascend 推理工具链调试，包括 vLLM 和 msmodelslim
disable-model-invocation: true
argument-hint: "vllm-ascend 运行问题 / msmodelslim 量化问题 / npu 使用咨询"
---

Ascend 推理工具链调试入口。

## 常用命令

查看 NPU 使用情况：
```bash
npu-smi info
```

> **提示**：运行 NPU 脚本前，建议先使用 `npu-smi info` 查询可用 NPU。可使用 `ASCEND_RT_VISIBLE_DEVICES` 环境变量指定 NPU 设备，例如：
> ```bash
> ASCEND_RT_VISIBLE_DEVICES=0,1 python script.py
> ```

## 子技能

- **vllm** - vLLM/vLLM-Ascend 源码定位和运行问题排查
- **msmodelslim** - msmodelslim 量化工具调试

请选择或描述你遇到的具体问题。
