# msmodelslim Technical Reference

Technical details and configuration guides for msmodelslim quantization.

## 1. Quantization Types & Naming Conventions

Source: [msmodelslim Source](https://gitcode.com/Ascend/msmodelslim) & [Quick Start Doc](https://msmodelslim.readthedocs.io/zh-cn/latest/zh/getting_started/quantization_quick_start/)

### Naming Rule
| Character | Meaning |
|-----------|---------|
| **w** | weight |
| **a** | activation |
| **c** | KV cache |
| **s** | sparse |
| **dynamic** | dynamic quantization |

### Supported Combinations
| Type | Meaning |
|----------|------|
| w4a8 | Weight 4-bit + Activation 8-bit |
| w4a8c8 | Weight 4-bit + Activation 8-bit + KV Cache 8-bit |
| w8a8 | Weight 8-bit + Activation 8-bit |
| w8a8s | Weight 8-bit + Activation 8-bit + Sparse |
| w8a8c8 | Weight 8-bit + Activation 8-bit + KV Cache 8-bit |
| w8a16 | Weight 8-bit + Activation 16-bit (MindIE only) |
| w16a16s | Weight 16-bit + Activation 16-bit + Sparse |

*Dynamic variants: `w4a8_dynamic`, `w8a8_dynamic`.*

---

## 2. Configuration Guide (Deep Dive)

### Granularity (Scope)
`scope` defines the sharing range of the Scale factor.

| Scope | Target | Description | Precision | Typical Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **per_tensor** | Activation | One Scale for the whole tensor | Lowest | Static quantization, max speed |
| **per_channel** | Weight | Independent Scale per output channel | High | Standard for 8-bit weight |
| **per_token** | Activation | Independent Scale per Token (row) | Very High | LLM dynamic quantization |
| **per_group** | Weight | Independent Scale per N parameters | Highest | Requirement for 4-bit weight |

### Calibration Method
`method` determines how to calculate the Scale based on float distribution.

| Method | Description | Precision | Speed | Note |
| :--- | :--- | :--- | :--- | :--- |
| **minmax** | Uses data Max and Min | Medium | Fast | Common for weights |
| **ssz** | Error search optimization (ModelSlim unique) | High | Slower | Recommended for activations |
| **kl** | KL divergence based | High | Slow | Classic truncation algorithm |

### Symmetry
| Mode | Config | Zero Point | Precision | Speed | Scenario |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Symmetric** | `True` | Fixed at 0 | Lower | **Max** | Weights, LLM dynamic activation |
| **Asymmetric** | `False` | Dynamically calculated | Higher | Slower | Activations after ReLU/Non-zero mean |

---

## 3. Expert Strategies for MoE Models

For models like DeepSeek or Qwen MoE:
- **Attention Modules**: Use **W8A8** (`per_channel` weight, `per_token` activation) for accuracy.
- **Expert Modules**: Use **W4A8** (`per_group` weight, `per_token` activation) to save 80%+ memory.
- **Unified A8**: Keep activations at 8-bit to utilize NPU INT8 hardware acceleration.
