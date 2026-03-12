# Commit-As-Prompt 示例

## 示例 1：OAuth2 登录支持

```bash
git commit -m "prompt(auth): 支持 OAuth2 登录" -m "WHAT: 重构认证中间件以支持 OAuth2 登录
WHY: 符合新的安全策略，允许第三方登录，对应需求 #2345
HOW: 引入 OAuth2 授权码流程替换 BasicAuth；向下兼容旧 Token；通过单元测试验证；需更新客户端配置"
```

## 示例 2：移除废弃接口

```bash
git commit -m "prompt(api): 移除废弃接口" -m "WHAT: 移除废弃 API 端点
WHY: 为 v2.0 版本做清理，减少维护成本
HOW: 下线 v1 Legacy 端点并更新 API 文档；版本标识提升至 v2；通知客户端迁移"
```

## 示例 3：常规功能提交

```bash
git commit -m "feat(ui): 添加深色模式切换" -m "WHAT: 在设置页面添加深色/浅色模式切换开关
WHY: 用户反馈在暗光环境下使用体验不佳，需求 #1234
HOW: 使用 CSS 变量实现主题切换；localStorage 持久化用户偏好；添加 smooth 过渡效果"
```

## 示例 4：修复提交

```bash
git commit -m "fix(auth): 修复 Token 过期后刷新失败" -m "WHAT: 修复 Refresh Token 刷新时返回 401 的问题
WHY: 生产环境出现用户频繁掉线，影响留存率，issue #567
HOW: 检查 Token 有效期判断逻辑；修复并发刷新时的竞态条件；添加重试机制"
```

## 聚合 Prompt 输出

多个 `prompt:` 提交聚合后生成：

```text
<Context>
1. [WHAT] 重构认证中间件以支持 OAuth2 登录
   [WHY] 符合新的安全策略，允许第三方登录，对应需求 #2345
   [HOW] 引入 OAuth2 授权码流程替换 BasicAuth；向下兼容旧 Token；通过单元测试验证；需更新客户端配置
2. [WHAT] 移除废弃 API 端点
   [WHY] 为 v2.0 版本做清理，减少维护成本
   [HOW] 下线 v1 Legacy 端点并更新 API 文档；版本标识提升至 v2；通知客户端迁移
</Context>
```
