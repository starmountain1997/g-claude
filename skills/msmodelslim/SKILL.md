---
name: msmodelslim
description: msmodelslim 量化工具调试
argument-hint: "模型量化 / 量化报错 / 模型结构咨询"
---

# 前置环境检查

在执行任何量化准备前，Agent 需要验证或提醒用户检查以下环境：

- NPU 状态：运行 npu-smi info 确保昇腾 NPU 可用。
- 依赖库：确保已安装 msmodelslim、torch_npu、transformers 等必要依赖。

在开始具体的量化操作前，Agent 必须先询问或判断用户的使用场景，并基于此推荐或采用相应的量化策略：

无额外要求/默认场景：建议优先使用 一键量化 (V1)。工具内部会自动集成最合适的算法组合，极大降低使用门槛。

追求极致精度或长序列推理：使用手动编写 Python 脚本的方式，允许用户根据模型特点和需求灵活选择量化算法和参数。

# 一键量化

对于无额外要求或默认场景，msmodelslim 提供了高度封装的 CLI 工具。Agent 应该首先尝试使用命令行工具来处理任务，这种方式最稳妥且不易出错。

Agent 可在终端中执行以下命令查看帮助，了解当前环境支持的可用参数：

```
msmodelslim quant -h
```

或者直接阅读[官方文档](https://www.google.com/search?q=https://msmodelslim.readthedocs.io/zh-cn/latest/zh/feature_guide/quick_quantization_v1/usage/)确定参数。

根据实际模型路径和前一步确定的量化策略（如是否附加 --fa3 等参数），构造准确的量化命令。例如：

```
msmodelslim quant \
    --model_path /path/to/original_model \
    --save_path /path/to/save_quantized_model \
    --w_bit 8 \
    --a_bit 8 \
    --calib_dataset "boolq" \
    --batch_size 1 \
    --device_type "npu"
```

注意，`save_path` 放在 `/homde/model_weights` 目录下。

由于大模型量化过程十分耗时，Agent 在确定正确的运行参数之后，应当停止执行（如果是为了测试参数而启动了进程，请杀掉该进程）。随后，Agent 必须将构造好的正确运行参数和完整的命令行告诉用户，让用户自行在后台或终端中运行。

如果测试或用户反馈执行一键量化命令时抛出异常，特别是当终端提示 No best practice found for model_type=xxx 时（这表示一键工具内部暂无该模型架构的最佳实践配置），或者用户明确需要复杂的代码级策略干预，Agent 必须立即终止当前场景，转入手动编写 Python 脚本。

# 手动编写 Python 脚本

查阅[官方文档](https://msmodelslim.readthedocs.io/zh-cn/latest/)或者使用 `pip show msmodelslim`，了解当前版本 msmodelslim 的脚本化 API（如 QuantConfig, Calibrator 等）的用法。

可以参考 `msmodelslim/example/` 目录下的其他模型量化脚本，找到一个与待量化模型架构最相近的脚本进行学习和微调。

针对参考模型，使用 GIT_LFS_SKIP_SMUDGE=1 克隆模型仓库（只获取模型结构和配置文件，不下载庞大的权重），优先从 ModelScope 下载，如果没有再从 HuggingFace 下载，然后与我们待量化的模型进行比较。

写好脚本后运行并测试，如果报错自行阅读并修改脚本直到可以运行。

如果服务可以正常拉起，因为该耗时较久，可以自行 kill，让用户自行在后台或终端中运行。