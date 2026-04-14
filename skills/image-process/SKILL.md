---
name: image-process
description: 图像处理工具，支持抠图（背景移除）、裁剪透明边缘等。当用户提出“抠图”、“移除背景”、“处理图片”等请求时调用此技能。
allowed-tools: Bash(python *)
---

# 图像处理 (Image Process)

此技能提供高效的图像处理功能，特别是使用 Python 和 OpenCV 进行快速抠图和裁剪。

## 核心功能

### 1. 快速抠图并裁掉边缘 (Matting & Auto-Crop)

使用 `GrabCut` 算法快速提取前景并生成透明背景，同时自动裁剪掉四周的透明区域。适用于单一主体。

```bash
python ${CLAUDE_SKILL_DIR}/scripts/matting.py [输入图片] [输出图片.png]
```

### 2. 专业抠图与多实体分割 (Pro Matting & Multi-Entity)

提供边缘羽化和多物体自动识别功能。

#### 使用方法

```bash
# 整体抠图（带边缘平滑）
python ${CLAUDE_SKILL_DIR}/scripts/matting_pro.py input.jpg output_prefix

# 自动识别多个实体，并分别保存为独立文件
python ${CLAUDE_SKILL_DIR}/scripts/matting_pro.py input.jpg output_prefix --split
```

#### 核心优势
- **边缘平滑 (Feathering)**: 通过高斯模糊优化 Alpha 遮罩，消除硬边缘和锯齿。
- **多物体识别**: 自动检测图中所有主要实体。
- **自动分件**: 使用 `--split` 参数可将图中每个物体抠出并单独存为文件。

#### 注意事项
- 输出文件必须是 `.png` 格式以支持透明度。
- 目前算法假设目标主体位于图像中央，四周保留有少许背景。
- 复杂背景可能需要多次迭代或更高级的深度学习模型（如 `rembg`）。

## 实现原理

1. **GrabCut 算法**: 基于颜色分布和边缘信息的交互式分割。程序会自动初始化一个矩形框，识别并移除框外的背景。
2. **Alpha 通道注入**: 将分割出的掩码转换为 Alpha 通道，使背景变为完全透明。
3. **内容裁剪**: 通过查找 Alpha 通道中的非零像素（即非透明区域），计算出最小包含框，并将图像裁剪至该框大小，消除冗余边缘。

## 示例请求
- “帮我把这张图片的背景抠掉”
- “扣出这张图的主体，做成透明底并裁剪边缘”
- “/image-process matting input.jpg output.png”
