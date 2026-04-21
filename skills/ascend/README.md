# Ascend Inference Toolchain Skill

Claude Code skill for the full Ascend NPU inference stack — from installation and performance tuning to quantization and accuracy evaluation. Covers every stage of deploying and optimizing LLMs on Ascend NPUs.

______________________________________________________________________

## 覆盖场景

| 场景 | 入口文档 |
|:---|:---|
| 模型下载（ModelScope / HuggingFace） | `model-download.md` |
| vLLM-Ascend 安装与版本锁定 | `vllm-install.md` |
| 性能目标调研（延迟 / 吞吐 / 并发） | `scenario-inquiry.md` |
| 部署调优（Eager → Graph → Online Serving） | `vllm-run.md` |
| 模型量化（W4A8 / W8A8 / W4A4 等） | `msmodelslim-quant.md` |
| 敏感层分析与精度恢复 | `msmodelslim-analysis.md` |
| 精度评测（AISBench） | `aisbench-install.md` / `aisbench-accuracy.md` |
| 性能评测（AISBench） | `aisbench-performance.md` |
| 社区贡献（DCO 签名 / PR 模板） | `vllm-contribute.md` |

______________________________________________________________________

## 核心工作流

### 推理部署路径

```
scenario-inquiry.md          ← 明确延迟/吞吐/并发目标
        │
        ▼
vllm-run.md Phase 2          ← 经验调参并验证
```

### 量化路径

```
用户指定 dtype
    │
    ▼
msmodelslim-quant.md         ← 量化（one-click 或 custom YAML）
    │
    ▼
vllm-run.md                  ← 部署量化模型
    │
    ▼
aisbench-accuracy.md         ← 精度评测
    │
    ├─ PASS → 完成
    └─ FAIL → msmodelslim-analysis.md → 重新量化 → 重新评测
                    │
                    └─ 再次 FAIL → 停止，询问用户是否回退 dtype
```

______________________________________________________________________

## Skill 结构

```
ascend/
├── SKILL.md                      # 入口：硬件检查 + 公共约定 + 任务路由
├── model-download.md             # 模型下载：ModelScope 优先，HuggingFace 回退
├── scenario-inquiry.md           # 场景调研：延迟/吞吐/并发多维访谈
├── vllm-install.md               # 安装：源码编译 + 版本锁定
├── vllm-run.md                   # 部署调优：Eager 验证 → Graph 优化 → Online Serving
├── vllm-contribute.md            # 社区贡献：DCO 签名与 PR 模板
├── msmodelslim-quant.md          # 量化主流程：端到端迭代工作流 + 参数选择指南
├── msmodelslim-analysis.md       # 敏感层分析：精度恢复回退路径
├── aisbench-install.md           # AISBench 安装
└── aisbench-accuracy.md          # 精度评测：配置、运行、结果排查
```

______________________________________________________________________

## 公共约定

每次任务开始前强制执行硬件检查：

```bash
npu-smi info  # 确认 NPU 健康且无占用进程
```

所有推理 / 量化命令通过 shell 脚本执行并重定向日志：

```bash
./run.sh YOUR_COMMAND  # stdout + stderr 写入带时间戳的 log 文件
```

所有工具包（`vllm`、`vllm-ascend`、`msmodelslim`、`ais_bench`）均为 editable 安装，使用前先 `pip show <package>` 确认路径。

______________________________________________________________________

## 自动触发条件

对话涉及以下关键词时 Skill 自动加载：

- 昇腾 NPU / Ascend / 910B
- vLLM-Ascend / vllm_ascend
- msmodelslim / 模型量化
- W4A8 / W8A8 / W4A4 等量化类型
- AISBench / 精度评测

也可手动调用：`/ascend`
