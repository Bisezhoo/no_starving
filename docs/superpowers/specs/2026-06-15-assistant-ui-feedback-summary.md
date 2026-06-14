# Assistant UI 反馈状态汇总设计

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.2 |
| 最近更新时间 | 2026-06-15 00:14:23 CST |
| 文档状态 | ✅ 汇总完成 |
| 汇总范围 | 默认欢迎语、流式思考占位、流式开始顶部思考提示、新消息自动滚动、Tool 调用默认折叠 |
| 关联设计 | `docs/superpowers/specs/2026-06-14-empty-chat-welcome-design.md` v0.3；`docs/superpowers/specs/2026-06-14-stream-thinking-placeholder-design.md` v0.2；`docs/superpowers/specs/2026-06-14-stream-start-thinking-indicator-design.md` v0.3；`docs/superpowers/specs/2026-06-14-chat-auto-scroll-design.md` v0.2；`docs/superpowers/specs/2026-06-14-tool-trace-collapse-design.md` v0.1 |
| 关联代码 | `frontend/src/components/ChatPage.vue`；`frontend/src/components/MessageList.vue`；`frontend/src/components/AssistantMessage.vue`；`frontend/src/components/ToolTracePanel.vue`；`frontend/src/styles/app.css`；`frontend/src/types/chat.ts` |

## 1. 汇总目标

本汇总文档把前端 Chat 页面中与“用户反馈状态”有关的五类设计统一到一份可读文档中，方便后续维护时判断不同状态的职责边界：

1. 空聊天时的默认欢迎语。
2. 用户发送消息后、后端首个有效事件返回前的“思考中”占位。
3. 后端 SSE 流已经开始后、最终完成前的顶部“疯狂思考中，请稍等”提示。
4. 历史加载、新消息插入和流式内容变化后的自动滚动到底部。
5. Tool 调用链路默认折叠为轻量摘要，点击后展开明细。

这些状态都属于前端展示层，不改变后端业务逻辑、Tool 调用规则、SSE 契约或聊天历史真实语义。

## 2. 统一设计原则

1. 前端只负责 UI 反馈，不做业务计算、推荐排序、画像合并或 Tool 参数处理。
2. 运行时 UI 状态不写入 `chat-history.json`，不进入 Agent Memory、画像或推荐历史。
3. 可见状态必须和真实数据区分：欢迎语是空态，不是真实历史；`pending` / `streaming` 是请求过程状态，不是 assistant 回复正文。
4. 调试信息默认弱化：Tool 调用轨迹默认折叠，避免压过推荐正文和卡片。
5. 状态收敛必须明确：成功、失败、流中断都要隐藏临时提示，并展示实际回复、卡片或错误。
6. 最新消息默认可见：历史加载、用户发送、流式回复增长、卡片或 Tool 轨迹更新后，消息列表自动滚动到底部。

## 3. 默认欢迎语

### 3.1 触发条件

页面挂载后调用 `loadChatHistory()`：

| 场景 | 前端行为 |
|------|----------|
| 历史接口返回真实消息 | 直接渲染历史消息，不插入欢迎语 |
| 历史接口返回空数组 | 渲染一条本地 assistant 欢迎消息 |
| 历史接口失败 | 渲染同一条本地 assistant 欢迎消息，输入框保持可用 |

### 3.2 数据边界

默认欢迎语只存在于前端 `messages` 中，用于空态展示：

1. 不写入 `chat-history.json`。
2. 不进入后端上下文。
3. 不进入 Agent Memory。
4. 不触发画像、推荐历史或 LLM 调用。
5. 用户发送新消息时，欢迎语保留在当前 UI 列表中，新的 user / assistant 消息追加在后面。

### 3.3 设计取舍

采用前端空态欢迎消息，而不是让后端历史接口返回默认欢迎语。原因是欢迎语不是用户真实对话历史，若由后端返回或写入历史文件，会混淆“空态提示”和“真实消息”的语义。

## 4. 流式思考占位

### 4.1 状态含义

`pending?: boolean` 表示用户已经发送消息，前端已经创建本轮 assistant 消息，但尚未收到后端首个内容或结束事件。

该状态解决的是“请求已经发出，但回复区没有任何可见反馈”的问题。

### 4.2 状态流转

```text
用户提交消息
  -> ChatPage 追加 user 消息
  -> ChatPage 追加 assistant 消息，pending=true
  -> AssistantMessage 显示“思考中”

收到 delta/card/done/error 或请求异常
  -> pending=false
  -> 展示实际文本、卡片、最终快照或错误文案
```

### 4.3 隐藏规则

`AssistantMessage.vue` 只有在以下条件同时满足时才显示“思考中”：

```text
message.pending === true
message.reply 为空
message.error 为空
message.cards.length === 0
```

如果已经有文本、错误或卡片，优先展示真实内容，避免占位遮挡实际结果。

## 5. 流式开始顶部思考提示

### 5.1 状态含义

`streaming?: boolean` 表示后端 SSE 流已经开始，本轮响应仍在持续生成。

它和 `pending` 的区别是：

| 状态 | 含义 | 可见文案 |
|------|------|----------|
| `pending=true` | 请求已发出，但还没有确认后端开始返回 | `思考中` |
| `streaming=true` | 已收到 SSE `meta`，后端流式返回开始但尚未结束 | `疯狂思考中，请稍等` |

### 5.2 状态流转

```text
用户发送消息
  -> pending=true
  -> streaming=false

收到 meta
  -> pending=false
  -> streaming=true
  -> 当前 assistant 消息顶部显示“疯狂思考中，请稍等”

收到 delta/card/tool_call/tool_result/profile_update
  -> streaming 维持 true
  -> 正文、卡片、Tool 摘要继续更新

收到 done/error 或 streamChat 抛异常
  -> pending=false
  -> streaming=false
  -> 隐藏顶部提示
```

### 5.3 渲染位置

顶部思考提示渲染在当前 assistant 消息最上方，高于警告、文本回复、结果卡片和 Tool 轨迹。这样用户能明确知道“当前这条回复还在生成”，而不是把提示误认为正文的一部分。

该提示是前端运行时 UI，不写入历史，也不改变后端 SSE 事件。

## 6. 新消息自动滚动到底部

### 6.1 触发条件

`MessageList.vue` 负责消息列表滚动行为。以下场景都应让 `.message-list` 滚动到底部：

1. 页面加载历史消息后。
2. 页面展示默认欢迎语后。
3. 用户发送消息并插入 user 消息、本轮 assistant 占位后。
4. assistant 流式回复文本增长后。
5. 错误、卡片、Tool 轨迹或画像更新导致当前消息高度变化后。

### 6.2 实现职责

自动滚动逻辑集中在 `MessageList.vue`，`ChatPage.vue` 不直接操作 DOM 滚动。

实现方式：

```text
MessageList.vue
  -> .message-list 增加 ref
  -> onMounted() 调用 scrollToBottom()
  -> watch(messages, deep=true, flush="post")
  -> scrollTop = scrollHeight
```

`flush: "post"` 用于确保 Vue 已经完成 DOM 更新，再读取并写入滚动位置。深度监听会随着 assistant `reply`、`cards`、`toolCalls` 等内容变化触发；当前历史上限为 60 条，首版性能成本可接受。

### 6.3 方案取舍

采用 `MessageList.vue` 内部监听 `messages`，而不是在 `ChatPage.vue` 的每个 SSE 回调里手动滚动。原因是滚动是列表展示职责，集中在列表组件能覆盖历史加载、默认欢迎语、发送消息、流式文本、卡片和 Tool 更新等所有入口。

本次不加入“用户手动上滑时暂停自动滚动”的策略，因为用户当前要求是每次有新消息滚动到最底部。后续若需要阅读历史消息体验，可单独设计“接近底部时才自动滚动”。

## 7. Tool 调用默认折叠

### 7.1 触发条件

`ToolTracePanel.vue` 接收 `items: ToolTraceItem[]`：

| 场景 | 前端行为 |
|------|----------|
| `items.length === 0` | 展示“暂无 Tool 调用” |
| `items.length > 0` | 默认折叠为 `Loaded N tools` |

### 7.2 折叠态

折叠态是一行轻量状态入口：

```text
SquareTerminal icon + Loaded N tools + ChevronRight icon
```

视觉设计要求：

1. 小字号、低对比颜色。
2. 透明背景、无边框。
3. 不展示 Tool 名称、状态、结果数、耗时或错误。
4. 视觉重量弱于正文、推荐卡片和步骤区。

### 7.3 展开态

点击摘要后展开：

```text
SquareTerminal icon + Loaded N tools + ChevronDown icon

search_meals      success
5 results · 11829ms
```

展开后展示每次 Tool 调用的：

1. `name`
2. `status`
3. `resultCount`
4. `durationMs`
5. `error`

不展示完整 `arguments`，避免调试信息变成大段 JSON。

再次点击摘要后收起，恢复默认一行。

### 7.4 职责边界

折叠状态由 `ToolTracePanel.vue` 内部维护。`AssistantResultBlock.vue` 和旧 `AssistantMessageTabs.vue` 只继续传入 `message.toolCalls`，不重复实现折叠逻辑。

## 8. 状态总览

| UI 状态 | 所属组件 | 真实数据来源 | 是否持久化 | 结束条件 |
|---------|----------|--------------|------------|----------|
| 默认欢迎语 | `ChatPage.vue` | 前端本地常量 | 否 | 用户继续对话后仍保留为 UI 消息 |
| `pending` 思考占位 | `ChatPage.vue` / `AssistantMessage.vue` | 前端请求状态 | 否 | 收到 `delta`、`card`、`done`、`error` 或请求异常 |
| `streaming` 顶部提示 | `ChatPage.vue` / `AssistantMessage.vue` | SSE `meta` 事件 | 否 | 收到 `done`、`error` 或请求异常 |
| 自动滚动到底部 | `MessageList.vue` | `messages` 渲染变化 | 否 | DOM 更新后设置 `scrollTop = scrollHeight` |
| Tool 折叠摘要 | `ToolTracePanel.vue` | `message.toolCalls` | Tool 数据会随 assistant 快照持久化，折叠状态不持久化 | 用户点击展开/收起 |

## 9. 测试覆盖汇总

| 范围 | 核心断言 |
|------|----------|
| 默认欢迎语 | 历史为空时显示；历史存在时不显示；历史失败时显示且仍可发送 |
| `pending` 占位 | 发送后立即显示“思考中”；收到 `delta` 或错误后隐藏 |
| `streaming` 提示 | 收到 `meta` 后显示顶部提示；`delta` 期间保留；`done` / `error` 后隐藏 |
| 自动滚动 | 挂载后滚到底部；新增消息后滚到底部；流式回复内容变化后继续滚到底部 |
| Tool 折叠 | 默认只显示 `Loaded N tools`；点击展开明细；再次点击收起；空数组保留空状态 |

## 10. 维护注意事项

1. 新增后端 SSE 事件时，应明确它是否清除 `pending`、是否维持 `streaming`。
2. 新增 assistant 历史字段时，不应把 `pending` 或 `streaming` 写入后端历史。
3. 调整欢迎语文案时，要保持它是 UI 空态，不把它提交给后端。
4. 调整 Tool 轨迹展示时，应优先保持默认折叠，只有用户主动点击才展示明细。
5. 如果未来支持多会话或多用户，欢迎语仍应由前端根据当前会话历史为空来决定，不应作为后端默认历史消息。
6. 如果未来引入大量历史消息、虚拟列表或“阅读旧消息时不打断用户”的体验，应重新设计自动滚动策略，不要把暂停逻辑分散到 SSE 回调里。

## 11. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 读取五份源设计文档 | ✅ 已完成 | 已覆盖欢迎语、pending、streaming、自动滚动、Tool 折叠 |
| 2 | 汇总统一状态边界和数据流 | ✅ 已完成 | 明确 UI 状态不污染后端历史，自动滚动只改变滚动位置 |
| 3 | 输出汇总 Markdown 文档 | ✅ 已完成 | 本文档 v0.1 |
| 4 | 补充新消息自动滚动设计 | ✅ 已完成 | 本文档 v0.2 |

✅ 计划已完成。
