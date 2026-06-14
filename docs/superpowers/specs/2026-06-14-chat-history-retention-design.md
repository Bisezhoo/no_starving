# 最近一天完整聊天记录加载设计

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.2 |
| 最近更新时间 | 2026-06-14 21:13:52 CST |
| 文档状态 | ✅ 已实现 |
| 关联需求 | `智能食谱助手需求分析.md` v0.29 |
| 关联设计 | `智能食谱助手技术设计.md` v0.34 |
| 确认方式 | 用户确认保存最近一天完整聊天记录，并增加 60 条消息上限 |

## 1. 背景

当前系统只持久化轻量 `AgentMemory`，用于恢复“第一个怎么做”“再推荐一个”等上下文。`AgentMemory` 会摘要化用户原文、截断助手回复，并保存候选卡片引用，因此不等同于页面可恢复的完整聊天记录。

用户希望进入页面时能看到最近一天的完整聊天记录，同时避免本地 JSON 无限制增长。该能力属于 UI 历史恢复，不应改变 Agent Memory 的摘要定位。

## 2. 目标

1. 后端保存最近 24 小时内的完整聊天消息。
2. 后端最多保留最近 60 条消息；用户消息和助手消息各算 1 条。
3. 前端进入 Chat 页面时自动加载历史消息，并按现有消息列表样式展示。
4. 完整聊天记录与 `agent-memory.json` 分离，使用独立 `chat-history.json`。
5. 历史加载不触发 LLM、Tool、画像合并或推荐历史追加。

## 3. 非目标

1. 不引入账号、用户隔离、多 `session`、数据库或跨设备同步。
2. 不支持历史搜索、分页、导出、清空记录或按日期分组。
3. 不把完整聊天记录传给 LLM 作为上下文；LLM 仍使用轻量 Agent Memory。
4. 不保存 SSE 增量事件流水，只保存页面恢复所需的最终消息快照。

## 4. 设计方案

新增后端 `ChatHistoryStore`，与 `MemoryStore` 使用同一个 `backend/data` 目录，但职责独立：

1. `chat-history.json` 保存完整 UI 消息数组，每条消息包含 `role`、`createdAt` 和对应消息内容。
2. `GET /api/chat/history` 返回 `{ code: 200, message: "success", data: { messages: ChatMessage[] } }`。
3. `POST /api/chat/stream` 在本轮 SSE 收尾时追加用户消息和助手最终消息，然后按最近 24 小时与最多 60 条裁剪。
4. 如果流中收到 `done`，保存助手最终 `reply`、`cards`、`toolCalls`、`warnings` 和画像变化。
5. 如果流中只产生 `error`，保存助手错误消息，便于刷新后看到失败记录。
6. 客户端中途断开且没有形成 `done` 或 `error` 时，不保证保存本轮部分内容。

## 5. 数据模型

```ts
type ChatHistoryMessage =
  | {
      role: "user";
      content: string;
      createdAt: string;
    }
  | {
      role: "assistant";
      reply: string;
      cards: Card[];
      toolCalls: ToolTraceItem[];
      warnings: string[];
      profileUpdates?: Record<string, unknown>[];
      error?: string;
      createdAt: string;
    };
```

裁剪规则：

1. 以 `createdAt >= now - 24h` 作为时间窗口。
2. 时间过滤后只保留数组末尾 60 条消息。
3. 读取时过滤过期和非法消息；写入时执行过滤并覆盖 `chat-history.json`。
4. 单条非法消息不影响其他历史消息加载。

## 6. 前端数据流

```text
ChatPage mounted
  -> loadChatHistory()
  -> GET /api/chat/history
  -> messages 初始化为后端返回的消息

用户发送新消息
  -> ChatPage 立即 push 用户消息和助手占位消息
  -> POST /api/chat/stream
  -> SSE 回调更新助手消息
  -> 后端在收尾时保存本轮完整消息
```

历史加载失败时，前端保留空消息列表并展示当前可用页面，不阻断新消息发送。

## 7. 测试方案

| 测试 | 断言 |
|------|------|
| `ChatHistoryStore` 缺失文件 | 返回空数组 |
| `ChatHistoryStore` 损坏 JSON | 返回空数组 |
| 时间裁剪 | 超过 24 小时的消息不返回 |
| 数量裁剪 | 超过 60 条时只保留最近 60 条 |
| Chat SSE 正常完成 | 保存用户消息和助手最终消息 |
| Chat SSE 运行期错误 | 保存用户消息和助手错误消息 |
| `GET /api/chat/history` | 返回统一响应格式和消息数组 |
| Chat 页面进入 | 调用历史接口并渲染历史消息 |

## 8. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 更新需求、技术设计和专项计划文档 | ✅ 已完成 | 本文档同步主文档 v0.29 / v0.34 |
| 2 | 编写后端历史存储失败测试 | ✅ 已完成 | 已覆盖 24 小时和 60 条裁剪 |
| 3 | 实现 `ChatHistoryStore` 和历史加载接口 | ✅ 已完成 | 单独文件，避免污染 `AgentMemory` |
| 4 | 编写前端历史加载失败测试 | ✅ 已完成 | 已覆盖页面进入时加载 |
| 5 | 实现前端 `loadChatHistory()` 和页面初始化 | ✅ 已完成 | 保持前端只做展示和 API 调用 |
| 6 | 更新代码走读并运行验证 | ✅ 已完成 | 相关后端 9 passed；前端全量 16 passed；构建通过 |

✅ 计划已完成。

## 9. 方案取舍

推荐独立 `chat-history.json`，而不是复用 `agent-memory.json`。原因是完整聊天记录属于 UI 恢复数据，保留用户原文和助手完整回复；Agent Memory 属于模型上下文恢复数据，会摘要化、截断并控制敏感信息暴露。两个边界分开能降低后续维护成本，也避免完整聊天记录被误传给 LLM。
