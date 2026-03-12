---
name: commit-as-prompt
description: 创建符合 WHAT/WHY/HOW 规范的 Git 提交，用于生成 AI 可理解的上下文 Prompt。用于创建结构化提交、整理变更、或将提交历史转化为 AI 上下文。
disable-model-invocation: true
argument-hint: "[commit]"
---

# Commit-As-Prompt

此命令帮助您创建格式良好的提交，提交内容可转化为供 AI 参考的问题上下文。

## 快速使用

```
/commit-as-prompt
```

或带提交信息：
```
/commit-as-prompt 修复登录超时问题
```

## 执行步骤

1. **检查工作区变更**
   ```
   git status -s
   git diff
   git diff --cached
   ```

2. **理解并清理代码**
   - 删除无用导入、死代码
   - 移除临时日志 (`console.log`, `debugger` 等)
   - 重命名临时标识 (`V2`, `TEMP`, `TEST` 等)
   - 删除临时测试或脚手架

3. **选择应纳入本次提交的文件**
   ```
   git add -p                 # 按块暂存
   git add <file> ...         # 按文件暂存
   ```

4. **编写提交信息**
   提交类型：
   - **Context Prompt 提交**：`prompt:` 开头，如 `prompt(auth): 支持 OAuth2 登录`
   - **常规提交**：`feat:`, `fix:`, `docs:` 等

   提交正文格式（WHAT/WHY/HOW）：
   ```
   WHAT: ...
   WHY: ...
   HOW: ...
   ```

5. **执行提交**
   ```
   git commit -m “prompt(auth): 支持 OAuth2 登录” -m “WHAT: ...
   WHY: ...
   HOW: ...”
   git push
   ```

## WHAT / WHY / HOW 编写要点

| 字段 | 说明 | 示例 |
|------|------|------|
| **WHAT** | 一句话描述动作与对象，使用祈使动词 | `重构认证中间件以支持 OAuth2 登录` |
| **WHY** | 阐述业务需求、用户需求或缺陷背景 | `符合新的安全策略，允许第三方登录，对应需求 #2345` |
| **HOW** | 整体策略、兼容性、验证方式、风险提示 | `引入 OAuth2 授权码流程替换 BasicAuth；向下兼容旧 Token` |

## 聚合多个提交

多个 `prompt:` 类型提交可聚合为 AI 上下文：

```
git commit -m “prompt(auth): 支持 OAuth2 登录” -m “WHAT: ...
WHY: ...
HOW: ...”

git commit -m “prompt(api): 移除废弃接口” -m “WHAT: ...
WHY: ...
HOW: ...”
```

聚合结果模板：
```
<Context>
1. [WHAT] ...
   [WHY] ...
   [HOW] ...
2. [WHAT] ...
   [WHY] ...
   [HOW] ...
</Context>
```

## 详细规范

- 详细文件挑选原则见 [reference.md](reference.md)
- 提交信息最佳实践见 [examples.md](examples.md)