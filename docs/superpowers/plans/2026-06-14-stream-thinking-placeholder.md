# 流式思考占位 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让用户发送消息后立即看到“思考中”，并在成功或失败返回时用实际内容替换该占位。

**Architecture:** 本次仅修改前端展示状态。`ChatPage.vue` 负责创建和收敛本轮 assistant 消息的 `pending` 状态；`AssistantMessage.vue` 负责根据 `pending/reply/error` 渲染占位或实际内容；后端 SSE 契约保持不变。

**Tech Stack:** Vue 3、TypeScript、Vitest、Vue Test Utils、Vite。

---

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.2 |
| 最近更新时间 | 2026-06-14 21:57:07 CST |
| 文档状态 | ✅ 已完成 |
| 关联设计 | `docs/superpowers/specs/2026-06-14-stream-thinking-placeholder-design.md` v0.2 |

## 1. 文件职责

| 文件 | 职责 |
|------|------|
| `frontend/src/types/chat.ts` | 为当前前端消息增加可选 `pending` 展示状态 |
| `frontend/src/components/ChatPage.vue` | 发送时创建 `pending=true` assistant 消息；`delta/done/error/catch` 时清除占位 |
| `frontend/src/components/AssistantMessage.vue` | 在无回复、无错误且 `pending=true` 时展示“思考中” |
| `frontend/src/styles/app.css` | 为思考占位提供轻量文本样式 |
| `frontend/tests/chat-page.spec.ts` | 覆盖发送后占位、成功替换、失败替换 |
| `frontend/tests/assistant-message.spec.ts` | 覆盖组件级 pending 占位渲染 |
| `智能食谱助手需求分析.md` | 同步前端流式状态成功标准 |
| `智能食谱助手技术设计.md` | 同步前端职责和流式降级策略 |
| `智能食谱助手代码走读.md` | 实现后同步代码走读和验证结果 |

## 2. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 更新设计和计划文档 | ✅ 已完成 | 已创建本计划并同步总需求/技术设计 |
| 2 | 编写组件和页面失败测试 | ✅ 已完成 | 旧实现按预期失败：缺少“思考中” |
| 3 | 实现最小 pending 状态 | ✅ 已完成 | 不改后端协议 |
| 4 | 运行聚焦测试 | ✅ 已完成 | `npm test -- assistant-message.spec.ts chat-page.spec.ts --run`，8 passed |
| 5 | 运行前端全量测试与构建 | ✅ 已完成 | `npm test -- --run` 22 passed；`npm run build` 通过 |
| 6 | 更新代码走读文档 | ✅ 已完成 | 已同步 v0.13 |

✅ 计划已完成。

## 3. TDD 步骤

### Task 1: AssistantMessage pending 占位

**Files:**

- Modify: `frontend/tests/assistant-message.spec.ts`
- Modify: `frontend/src/components/AssistantMessage.vue`
- Modify: `frontend/src/types/chat.ts`
- Modify: `frontend/src/styles/app.css`

- [x] **Step 1: Write the failing test**

在 `frontend/tests/assistant-message.spec.ts` 中新增：

```ts
it("renders thinking placeholder while assistant reply is pending", () => {
  const wrapper = mount(AssistantMessage, {
    props: {
      message: {
        role: "assistant",
        reply: "",
        cards: [],
        toolCalls: [],
        warnings: [],
        profileUpdates: [],
        pending: true,
      },
    },
  });

  expect(wrapper.text()).toContain("思考中");
  expect(wrapper.find(".assistant-pending").exists()).toBe(true);
});
```

- [x] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- assistant-message.spec.ts chat-page.spec.ts --run`

Actual: FAIL as expected because `AssistantMessage.vue` does not render `.assistant-pending` and `ChatPage.vue` has no pending lifecycle.

- [x] **Step 3: Write minimal implementation**

在 `AssistantMessage` 类型添加 `pending?: boolean`，并在 `AssistantMessage.vue` 增加：

```vue
<p v-if="message.pending && !message.reply && !message.error && !message.cards.length" class="assistant-pending">思考中</p>
```

- [x] **Step 4: Run test to verify it passes**

Run: `cd frontend && npm test -- assistant-message.spec.ts chat-page.spec.ts --run`

Actual: PASS, 2 files / 8 tests passed.

### Task 2: ChatPage pending 生命周期

**Files:**

- Modify: `frontend/tests/chat-page.spec.ts`
- Modify: `frontend/src/components/ChatPage.vue`

- [x] **Step 1: Write failing tests**

新增两个行为：

1. `streamChat` 暂停时，发送后页面立即显示“思考中”。
2. `streamChat` 抛错时，页面显示错误信息且不再显示“思考中”。

- [x] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- assistant-message.spec.ts chat-page.spec.ts --run`

Actual: FAIL as expected because assistant message currently没有 `pending` 状态。

- [x] **Step 3: Write minimal implementation**

发送时创建：

```ts
pending: true,
```

并在 `delta`、`card`、`done`、`error`、`catch` 更新前设置：

```ts
message.pending = false;
```

- [x] **Step 4: Run focused tests**

Run: `cd frontend && npm test -- chat-page.spec.ts assistant-message.spec.ts --run`

Actual: PASS, 2 files / 8 tests passed.

### Task 3: Verification and docs

**Files:**

- Modify: `智能食谱助手代码走读.md`
- Modify: `docs/superpowers/specs/2026-06-14-stream-thinking-placeholder-design.md`
- Modify: `docs/superpowers/plans/2026-06-14-stream-thinking-placeholder.md`

- [x] **Step 1: Run full frontend test**

Run: `cd frontend && npm test -- --run`

Actual: PASS, 7 files / 22 tests passed.

- [x] **Step 2: Run frontend build**

Run: `cd frontend && npm run build`

Actual: PASS, `vue-tsc --noEmit && vite build` completed.

- [x] **Step 3: Update docs**

把设计、计划和代码走读中的执行计划表更新为已完成，并记录验证命令结果。

## 4. 计划自检

| 检查项 | 结果 |
|--------|------|
| 覆盖需求 | 已覆盖即时占位、成功替换、失败替换 |
| 后端契约 | 不修改 SSE 或历史接口 |
| 占位持久化 | `pending` 仅前端运行时使用，历史消息默认不携带 |
| 测试优先 | 每个行为先写失败测试再实现 |
