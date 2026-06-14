# 流式开始顶部思考提示设计

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.3 |
| 最近更新时间 | 2026-06-14 23:40:16 CST |
| 文档状态 | ✅ 已实现并验证通过 |
| 关联需求 | `智能食谱助手需求分析.md` v0.33 |
| 关联设计 | `智能食谱助手技术设计.md` v0.40 |
| 关联计划 | `docs/superpowers/plans/2026-06-14-stream-start-thinking-indicator.md` v0.2 |
| 确认方式 | 用户确认后端流式返回开始后，在当前助手消息顶部显示“疯狂思考中，请稍等”，流式完成或报错后隐藏 |

## 1. 背景

当前前端已有 `pending` 状态：用户发送消息后立即创建一条 assistant 消息，并在首个内容事件到来前展示“思考中”。收到 `delta`、`card`、`done` 或 `error` 后，`pending` 会被清除。

用户希望更明确地区分“请求已发送但后端还没开始返回”和“后端流式返回已经开始但仍在持续生成”。因此需要在后端 SSE 流开始后，在当前助手消息顶部显示一行带动效的小字“疯狂思考中，请稍等”，并在最终完成或报错后隐藏。

## 2. 目标

1. 收到后端 SSE `meta` 事件后，在当前 assistant 消息顶部显示“疯狂思考中，请稍等”。
2. 提示文字应出现在助手回复正文、结构化卡片和辅助信息上方。
3. 在后续 `delta`、`card`、`tool_call`、`tool_result`、`profile_update` 事件期间，提示继续显示。
4. 收到 `done` 或 `error` 事件后隐藏提示。
5. `streamChat()` 抛出异常时隐藏提示，并展示现有错误文案。
6. 不修改后端 SSE 事件契约，不新增后端接口。

## 3. 非目标

1. 不改变后端 Agent 推理流程、Tool 调用或 SSE 事件顺序。
2. 不把提示文字写入 `chat-history.json` 或后端历史消息。
3. 不替换空聊天欢迎语。
4. 不引入新的动画库。
5. 不调整推荐卡片、Markdown 渲染或 Tool 轨迹内容。

## 4. 设计方案

采用前端状态扩展方案。给 `AssistantMessage` 增加 UI 专用字段：

```ts
streaming?: boolean;
```

`streaming` 表示当前 assistant 消息已经收到后端流式开始信号，但本轮响应尚未结束。它只存在于前端运行时，不属于后端历史契约。

状态流转：

```text
用户发送消息
  -> 创建 assistant 消息，pending=true，streaming=false

收到 meta
  -> pending=false
  -> streaming=true
  -> 顶部显示“疯狂思考中，请稍等”

收到 delta/card/tool_call/tool_result/profile_update
  -> streaming 维持 true
  -> 正文、卡片、Tool 轨迹继续正常更新

收到 done/error 或 streamChat 抛异常
  -> pending=false
  -> streaming=false
  -> 隐藏顶部提示
```

渲染位置：

```vue
<section class="assistant-message">
  <div v-if="message.streaming" class="assistant-streaming">
    <span>疯狂思考中，请稍等</span>
    <span class="thinking-dots">...</span>
  </div>
  <!-- warnings / reply / cards 继续按现有顺序展示 -->
</section>
```

样式保持轻量：小字号、低干扰颜色、点点跳动或轻微透明度动效。动画仅使用 CSS `@keyframes`，不引入依赖。

## 5. 方案取舍

| 方案 | 优点 | 风险 | 结论 |
|------|------|------|------|
| 前端基于 `meta` 设置 `streaming` | 精确表达后端流已经开始；不改后端；实现最小 | 依赖后端持续发送 `meta` 作为首个事件 | 采用 |
| 复用现有 `pending` 文案 | 改动最少 | `pending` 会在首个内容事件后消失，无法覆盖整个流式生成阶段 | 不采用 |
| 后端新增专门 `thinking` 事件 | 语义最清晰 | 需要改后端契约和测试，当前需求没有必要 | 不采用 |

## 6. 测试方案

| 测试 | 断言 |
|------|------|
| `AssistantMessage` streaming 状态 | `message.streaming=true` 时顶部显示“疯狂思考中，请稍等”和动效元素 |
| `AssistantMessage` 非 streaming 状态 | `message.streaming=false` 时不显示顶部提示 |
| `ChatPage` 收到 `meta` | 当前 assistant 消息显示顶部提示 |
| `ChatPage` 收到 `delta` | 顶部提示仍显示，回复正文同时显示 |
| `ChatPage` 收到 `done` | 顶部提示隐藏，最终回复保留 |
| `ChatPage` 收到 `error` 或请求异常 | 顶部提示隐藏，错误文案展示 |

## 7. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 更新需求、技术设计和专项设计文档 | ✅ 已完成 | 明确基于 `meta` 的前端 streaming 状态 |
| 2 | 编写 `AssistantMessage` streaming 失败测试 | ✅ 已完成 | 已确认旧组件缺少 `.assistant-streaming` |
| 3 | 编写 `ChatPage` 流式状态失败测试 | ✅ 已完成 | 已确认旧页面 `meta` 后提示未出现 |
| 4 | 实现前端 streaming 状态和 CSS 动效 | ✅ 已完成 | 不修改后端 SSE 契约 |
| 5 | 更新代码走读并运行验证 | ✅ 已完成 | `assistant-message.spec.ts`、`chat-page.spec.ts` 和前端构建通过 |

## 8. 设计自检

1. 设计未修改后端事件契约，仅复用已有 `meta`、`done`、`error`。
2. `streaming` 是前端 UI 状态，不进入聊天历史持久化。
3. 提示显示和隐藏边界覆盖正常完成、SSE 错误和请求异常。
4. 实现范围限定在前端消息状态、组件渲染、样式和前端测试。
