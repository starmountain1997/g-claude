---
name: novel-writter
description: >
  小说创作流水线：从故事"梗"到完稿。包含三阶段子技能——outline（创作大纲）、
  detailed-outline（创作细纲）、writing（正文写作）。根据用户所处的创作阶段自动调度到对应子技能。
  TRIGGER: 用户提到写小说、写故事、故事大纲、世界观设定、人物设定、帮我写科幻/奇幻/悬疑/言情/历史小说、
  故事构思、续写、角色设计、情节设计、梗概拓展、或者给出一段故事创意/梗让你拓展。
  Even if the user just says they have a story idea or a "梗", use this skill.
---

# Novel Writer — 小说创作流水线

三阶段逐级承接：**大纲（分章级）→ 细纲（场景级）→ 正文（叙事文本）**。

## 子技能

| 子技能 | 状态 | 职责 |
|--------|------|------|
| `outline` | ✅ | 从"梗"出发，产出分章大纲（含世界观、人物群像、关系网络、故事线） |
| `detailed-outline` | ✅ | 承接分章大纲，拆解为场景级细纲（含起伏线、情感线、立场演进） |
| `writing` | ✅ | 从场景细纲出发，逐场产出叙事正文（含文本质检体系） |

## 调度规则

根据用户当前的创作阶段，调用对应子技能：

| 用户状态 | 调用 |
|----------|------|
| 给出故事创意/梗，需要大纲 | `Skill(skill: "novel-writter:outline")` |
| 已有大纲，需要逐场景细化 | `Skill(skill: "novel-writter:detailed-outline")` |
| 已有细纲，需要开始写正文 | `Skill(skill: "novel-writter:writing")` |
| 意图不明确 | 询问当前创作阶段，再调用对应子技能 |

如果某个子技能尚未完成开发，直接告知用户并建议先使用已有的前序技能。
