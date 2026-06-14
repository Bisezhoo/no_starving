# 流式思考占位设计

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.2 |
| 最近更新时间 | 2026-06-14 21:57:07 CST |
| 文档状态 | ✅ 已实现 |
| 关联需求 | `智能食谱助手需求分析.md` v0.31 |
| 关联设计 | `智能食谱助手技术设计.md` v0.36 |
| 确认方式 | 用户确认采用方案 A：前端 assistant 消息增加 `pending` 状态 |

## 1. 背景

当前 `ChatPage.vue` 在用户提交消息后会立即插入一条空的 assistant 消息，但该消息在收到 `delta`、`done` 或 `error` 前没有可见内容。用户体验上表现为“请求已发出但回复区无变化”，不符合流式输出应先给出即时反馈的预期。

本次需求要求：流式输出收到请求后先展示“思考中”，如果后续有返回内容则替换为实际回复，如果返回失败则替换为错误信息。

## 2. 目标

1. 用户提交消息后，前端立即在本轮 assistant 消息中展示“思考中”。
2. 收到第一段 `delta` 时，隐藏“思考中”，展示流式文本。
3. 收到 `card` 或 `done` 时，隐藏“思考中”，展示结构化卡片或最终 `reply`、`cards`、`toolCalls`、`warnings` 快照。
4. 收到 SSE `error`、HTTP 非 2xx 错误、无响应体或流中断异常时，隐藏“思考中”，展示错误信息。
5. `pending` 只用于前端当前请求展示，不写入后端历史，不改变 SSE 事件契约。

## 3. 非目标

1. 不修改 `POST /api/chat/stream` 的请求或响应格式。
2. 不新增后端 `thinking` / `status` SSE 事件。
3. 不改变 `chat-history.json` 的持久化结构。
4. 不新增全局状态管理库。
5. 不改变推荐卡片、Markdown 渲染、Tool 轨迹或画像展示逻辑。

## 4. 设计方案

采用前端展示层最小改造：

1. `AssistantMessage` 类型增加可选字段 `pending?: boolean`。
2. `ChatPage.vue` 创建本轮 assistant 消息时设置 `pending: true`。
3. `ChatPage.vue` 在以下事件中执行 `pending = false`：
   - `delta`：追加首段或后续流式文本前清除占位。
   - `card`：写入结构化卡片前清除占位，避免卡片已经可见时仍显示思考占位。
   - `done`：写入最终快照前清除占位。
   - `error`：写入错误文案前清除占位。
   - `catch`：HTTP 错误、连接失败、流中断等异常写入前清除占位。
4. `AssistantMessage.vue` 在 `message.pending && !message.reply && !message.error && !message.cards.length` 时展示固定文案“思考中”。
5. `app.css` 增加轻量 `.assistant-pending` 样式，保持与现有工具型 Chat UI 一致。

## 5. 数据流

```text
用户提交消息
  -> ChatPage push user message
  -> ChatPage push assistant message with pending=true
  -> AssistantMessage 展示“思考中”

SSE delta/card/done
  -> ChatPage pending=false
  -> 写入 reply/cards/toolCalls/warnings
  -> AssistantMessage 展示实际内容

HTTP/SSE error
  -> ChatPage pending=false
  -> 写入 error
  -> AssistantMessage 展示错误文案
```

## 6. 错误与边界

1. 如果请求在建立 SSE 前失败，`streamChat()` 抛出的后端 JSON 错误会替换“思考中”。
2. 如果 SSE 中途断开且未收到 `done`，`streamChat()` 抛出的“生成中断，请重试”会替换“思考中”；已收到的 `reply` 保留。
3. 如果历史消息来自后端，默认不带 `pending`，不会显示“思考中”。
4. 如果极端情况下存在 `pending=true` 且已经有 `reply`、`error` 或 `cards`，优先显示实际内容，不再显示占位。

## 7. 测试方案

| 测试 | 断言 |
|------|------|
| 发送后流式返回前 | 页面立即出现“思考中” |
| 收到 `delta` | “思考中”消失，实际文本出现 |
| 请求失败 | “思考中”消失，错误信息出现 |
| 组件展示 | `pending=true` 且无内容时显示“思考中”；已有 `reply` 时不显示占位 |

## 8. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 同步需求和技术设计文档 | ✅ 已完成 | 已更新 v0.31 / v0.36 |
| 2 | 编写失败测试 | ✅ 已完成 | 旧实现 3 个断言按预期失败 |
| 3 | 实现前端 pending 状态 | ✅ 已完成 | 仅改展示层和类型，后端契约不变 |
| 4 | 运行前端测试与构建 | ✅ 已完成 | 聚焦测试 8 passed；前端全量 22 passed；构建通过 |
| 5 | 更新代码走读文档 | ✅ 已完成 | 已同步 v0.13 |

✅ 计划已完成。

## 9. 方案取舍

推荐方案 A（前端 `pending` 状态）优于仅靠空消息推断，因为它不会把历史中的空 assistant 消息误判为仍在思考；也优于新增后端状态事件，因为当前 SSE 已能通过 `delta`、`done`、`error` 表达状态收敛，扩展后端契约会增加测试和兼容成本。
