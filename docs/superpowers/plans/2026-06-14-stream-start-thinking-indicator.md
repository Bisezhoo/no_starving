# 流式开始顶部思考提示 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收到后端 SSE `meta` 后，在当前助手消息顶部显示“疯狂思考中，请稍等”，并在 `done`、`error` 或请求异常后隐藏。

**Architecture:** 只扩展前端运行时 UI 状态。`AssistantMessage` 增加 `streaming?: boolean`；`ChatPage` 在 `meta` 事件设置 `streaming=true`，在 `done`、`error` 和 catch 分支清除；`AssistantMessage.vue` 在消息顶部渲染提示，`app.css` 复用现有点点动效风格。

**Tech Stack:** Vue 3、TypeScript、Vitest、@vue/test-utils、CSS keyframes。

---

| 项目 | 内容 |
|------|------|
| 计划版本 | v0.2 |
| 最近更新时间 | 2026-06-14 23:41:42 CST |
| 状态 | ✅ 计划已完成 |
| 关联需求 | `智能食谱助手需求分析.md` v0.33 |
| 关联设计 | `智能食谱助手技术设计.md` v0.40 |
| 关联专项设计 | `docs/superpowers/specs/2026-06-14-stream-start-thinking-indicator-design.md` v0.3 |

## 1. 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `frontend/src/types/chat.ts` | 修改 | 增加前端 UI 状态字段 `streaming?: boolean` |
| `frontend/src/components/AssistantMessage.vue` | 修改 | 在 assistant 消息顶部渲染 streaming 提示 |
| `frontend/src/components/ChatPage.vue` | 修改 | 在 `meta` / `done` / `error` / catch 中维护 `streaming` 状态 |
| `frontend/src/styles/app.css` | 修改 | 增加顶部小字和点点动效样式 |
| `frontend/tests/assistant-message.spec.ts` | 修改 | 覆盖 streaming 提示渲染和非 streaming 隐藏 |
| `frontend/tests/chat-page.spec.ts` | 修改 | 覆盖 meta 后显示、delta 期间保留、done/error/异常后隐藏 |
| `智能食谱助手代码走读.md` | 修改 | 编码完成后同步走读、验证结果和关联计划 |
| `docs/superpowers/specs/2026-06-14-stream-start-thinking-indicator-design.md` | 修改 | 随实施进度更新执行计划表 |
| `docs/superpowers/plans/2026-06-14-stream-start-thinking-indicator.md` | 修改 | 随实施进度更新执行计划表 |

## 2. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 前端：编写 `AssistantMessage` streaming 失败测试 | ✅ 已完成 | 已确认 RED：`.assistant-streaming` 不存在 |
| 2 | 前端：实现 `AssistantMessage` streaming 展示 | ✅ 已完成 | 已增加类型字段、模板和 CSS；`assistant-message.spec.ts` 通过 |
| 3 | 前端：编写 `ChatPage` streaming 状态失败测试 | ✅ 已完成 | 已确认 RED：`meta` 后提示未出现 |
| 4 | 前端：实现 `ChatPage` meta/done/error 状态流转 | ✅ 已完成 | 已维护 `meta`、`done`、`error` 和异常分支状态 |
| 5 | 文档与验证收口 | ✅ 已完成 | 已更新代码走读，定向测试和前端构建通过 |

## 3. 任务拆解

### Task 1: AssistantMessage 顶部提示

**Files:**
- Modify: `frontend/tests/assistant-message.spec.ts`
- Modify: `frontend/src/types/chat.ts`
- Modify: `frontend/src/components/AssistantMessage.vue`
- Modify: `frontend/src/styles/app.css`

- [x] **Step 1: 写 streaming 提示失败测试**

在 `frontend/tests/assistant-message.spec.ts` 增加：

```ts
it("renders animated streaming hint at the top while backend stream is active", () => {
  const wrapper = mount(AssistantMessage, {
    props: {
      message: {
        role: "assistant",
        reply: "推荐番茄鸡蛋面",
        cards: [],
        toolCalls: [],
        warnings: [],
        profileUpdates: [],
        streaming: true,
      },
    },
  });

  expect(wrapper.find(".assistant-streaming").exists()).toBe(true);
  expect(wrapper.find(".assistant-message").element.firstElementChild?.classList.contains("assistant-streaming")).toBe(true);
  expect(wrapper.text()).toContain("疯狂思考中，请稍等");
  expect(wrapper.text()).toContain("推荐番茄鸡蛋面");
  expect(wrapper.findAll(".assistant-streaming .dot")).toHaveLength(3);
});
```

- [x] **Step 2: 运行测试确认失败**

Run:

```bash
cd frontend
npm test -- assistant-message.spec.ts --run
```

Expected: FAIL，`.assistant-streaming` 不存在，提示文本未渲染。

- [x] **Step 3: 实现类型、模板和样式**

`frontend/src/types/chat.ts`：

```ts
export type AssistantMessage = {
  role: "assistant";
  reply: string;
  cards: Card[];
  toolCalls: ToolTraceItem[];
  warnings: string[];
  profileUpdates?: Record<string, unknown>[];
  error?: string;
  pending?: boolean;
  streaming?: boolean;
  createdAt?: string;
};
```

`frontend/src/components/AssistantMessage.vue` 在 `<section class="assistant-message">` 顶部插入：

```vue
<div v-if="message.streaming" class="assistant-streaming">
  <span class="streaming-text">疯狂思考中，请稍等</span>
  <span class="thinking-dots">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </span>
</div>
```

`frontend/src/styles/app.css` 增加轻量样式，复用已有 `.thinking-dots .dot` 动效：

```css
.assistant-streaming {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  line-height: 1.4;
  color: #6b7280;
}

.streaming-text {
  animation: streaming-pulse 1.4s ease-in-out infinite;
}

@keyframes streaming-pulse {
  0%,
  100% {
    opacity: 0.55;
  }
  50% {
    opacity: 1;
  }
}
```

- [x] **Step 4: 运行测试确认通过**

Run:

```bash
cd frontend
npm test -- assistant-message.spec.ts --run
```

Expected: PASS。

### Task 2: ChatPage streaming 状态流转

**Files:**
- Modify: `frontend/tests/chat-page.spec.ts`
- Modify: `frontend/src/components/ChatPage.vue`

- [x] **Step 1: 写 meta/delta/done 失败测试**

在 `frontend/tests/chat-page.spec.ts` 增加：

```ts
it("shows streaming hint after meta and hides it after done", async () => {
  const deferred = createDeferred();
  let streamHandlers: StreamHandlers = {};
  streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
    streamHandlers = handlers;
    await deferred.promise;
  });

  const wrapper = mount(ChatPage);

  await wrapper.find("textarea").setValue("推荐一道晚餐");
  await wrapper.find("form").trigger("submit.prevent");
  await wrapper.vm.$nextTick();

  streamHandlers.meta?.({ requestId: "r1" });
  await wrapper.vm.$nextTick();

  expect(wrapper.text()).toContain("疯狂思考中，请稍等");

  streamHandlers.delta?.({ text: "推荐番茄鸡蛋面" });
  await wrapper.vm.$nextTick();

  expect(wrapper.text()).toContain("疯狂思考中，请稍等");
  expect(wrapper.text()).toContain("推荐番茄鸡蛋面");

  streamHandlers.done?.({
    reply: "推荐番茄鸡蛋面",
    cards: [],
    toolCalls: [],
    warnings: [],
  });
  deferred.resolve();
  await flushPromises();

  expect(wrapper.text()).not.toContain("疯狂思考中，请稍等");
  expect(wrapper.text()).toContain("推荐番茄鸡蛋面");
});
```

- [x] **Step 2: 写 error/异常隐藏测试**

在 `frontend/tests/chat-page.spec.ts` 增加：

```ts
it("hides streaming hint when stream returns an error after meta", async () => {
  const deferred = createDeferred();
  let streamHandlers: StreamHandlers = {};
  streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
    streamHandlers = handlers;
    await deferred.promise;
  });

  const wrapper = mount(ChatPage);

  await wrapper.find("textarea").setValue("推荐一道晚餐");
  await wrapper.find("form").trigger("submit.prevent");
  await wrapper.vm.$nextTick();

  streamHandlers.meta?.({ requestId: "r1" });
  await wrapper.vm.$nextTick();

  expect(wrapper.text()).toContain("疯狂思考中，请稍等");

  streamHandlers.error?.({ message: "服务暂时不可用" });
  deferred.resolve();
  await flushPromises();

  expect(wrapper.text()).not.toContain("疯狂思考中，请稍等");
  expect(wrapper.text()).toContain("服务暂时不可用");
});
```

- [x] **Step 3: 运行测试确认失败**

Run:

```bash
cd frontend
npm test -- chat-page.spec.ts --run
```

Expected: FAIL，`meta` 不会设置 streaming，提示文本不出现。

- [x] **Step 4: 实现状态流转**

在 `frontend/src/components/ChatPage.vue` 创建 assistant 消息时增加：

```ts
streaming: false,
```

在 `streamChat` handlers 中增加：

```ts
meta: () => {
  updateAssistant((message) => {
    message.pending = false;
    message.streaming = true;
  });
},
```

调整已有 `delta` / `card` 不再清除 `streaming`，只清除 `pending`：

```ts
message.pending = false;
```

在 `error`、`done` 和 catch 分支都增加：

```ts
message.streaming = false;
```

- [x] **Step 5: 运行测试确认通过**

Run:

```bash
cd frontend
npm test -- chat-page.spec.ts --run
```

Expected: PASS。

### Task 3: 文档与验证收口

**Files:**
- Modify: `智能食谱助手代码走读.md`
- Modify: `docs/superpowers/specs/2026-06-14-stream-start-thinking-indicator-design.md`
- Modify: `docs/superpowers/plans/2026-06-14-stream-start-thinking-indicator.md`

- [x] **Step 1: 更新代码走读**

将 `智能食谱助手代码走读.md` 升到下一版本，补充：

```markdown
- 收到 SSE `meta` 后，`ChatPage.vue` 将当前 assistant 消息切换为 `streaming=true`，`AssistantMessage.vue` 在消息顶部展示“疯狂思考中，请稍等”。
- `delta`、`card`、Tool 和画像事件期间保留顶部提示；`done`、`error` 或请求异常后清除 `streaming`。
```

- [x] **Step 2: 更新设计和计划状态**

将 `docs/superpowers/specs/2026-06-14-stream-start-thinking-indicator-design.md` 更新到 v0.3，执行计划表任务 2~5 标记为 `✅ 已完成`。

将本计划更新到 v0.2，执行计划表任务 1~5 标记为 `✅ 已完成`，状态改为 `✅ 计划已完成`。

- [x] **Step 3: 运行最终验证**

Run:

```bash
cd frontend
npm test -- assistant-message.spec.ts chat-page.spec.ts --run
npm run build
```

Expected: 两个前端测试文件通过，前端构建通过。

## 4. 验证命令

```bash
cd frontend
npm test -- assistant-message.spec.ts chat-page.spec.ts --run
npm run build
```

## 5. 计划自检

| 检查项 | 结果 |
|--------|------|
| Spec 覆盖 | 覆盖 `meta` 显示、`delta` 保留、`done`/`error`/异常隐藏 |
| 后端边界 | 不修改后端接口、SSE 契约、JSON 持久化或 Agent 逻辑 |
| 类型一致性 | `streaming?: boolean` 是 `AssistantMessage` 的可选前端状态 |
| TDD 顺序 | 先写失败测试，再实现类型、模板、状态流转和样式 |
| 占位扫描 | 无未决占位；所有代码步骤给出具体文件、代码片段和命令 |
