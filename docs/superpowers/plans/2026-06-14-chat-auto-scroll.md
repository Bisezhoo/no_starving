# 聊天消息自动滚动到底部 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 Chat 消息列表在历史加载、新消息插入和流式内容更新后自动滚动到最底部。

**Architecture:** 自动滚动属于 `MessageList.vue` 的展示职责。组件持有 `.message-list` DOM 引用，监听 `messages` 的深度变化，并在 Vue 完成 DOM 更新后把滚动条设置到 `scrollHeight`；`ChatPage.vue` 继续只负责消息状态和 SSE 事件归并。

**Tech Stack:** Vite + Vue 3 + TypeScript + Vitest + Vue Test Utils。

---

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.2 |
| 最近更新时间 | 2026-06-14 22:55:53 CST |
| 文档状态 | ✅ 计划已完成 |
| 关联设计 | `docs/superpowers/specs/2026-06-14-chat-auto-scroll-design.md` v0.2 |

## 2. 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `frontend/tests/message-list.spec.ts` | 新增 | 覆盖初始渲染、新消息和流式内容变化后的自动滚动 |
| `frontend/src/components/MessageList.vue` | 修改 | 持有列表 DOM 引用并在消息变化后滚动到底部 |
| `智能食谱助手技术设计.md` | 修改 | 同步前端自动滚动交互设计和版本 |
| `智能食谱助手代码走读.md` | 修改 | 同步实现说明和测试结果 |

## 3. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 编写 `MessageList` 自动滚动失败测试 | ✅ 已完成 | 当前组件按预期失败：`scrollTop` 仍为 0 |
| 2 | 修改 `MessageList.vue` 实现自动滚动 | ✅ 已完成 | 不改消息数据结构 |
| 3 | 运行聚焦前端测试 | ✅ 已完成 | `message-list.spec.ts` 与 `chat-page.spec.ts`：8 passed |
| 4 | 运行前端全量测试和构建 | ✅ 已完成 | `npm test -- --run`、`npm run build` 均通过 |
| 5 | 更新代码走读文档 | ✅ 已完成 | v0.17 已记录自动滚动实现和验证结果 |

## 4. Task 1: 自动滚动测试

**Files:**
- Create: `frontend/tests/message-list.spec.ts`

- [ ] **Step 1: Write the failing test**

```ts
import { flushPromises, mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { afterEach, describe, expect, it } from "vitest";
import MessageList from "../src/components/MessageList.vue";
import type { ChatMessage } from "../src/types/chat";

let currentScrollHeight = 0;
let originalScrollHeight: PropertyDescriptor | undefined;

function installScrollHeightStub() {
  originalScrollHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "scrollHeight");
  Object.defineProperty(HTMLElement.prototype, "scrollHeight", {
    configurable: true,
    get() {
      return currentScrollHeight;
    },
  });
}

function restoreScrollHeightStub() {
  if (originalScrollHeight) {
    Object.defineProperty(HTMLElement.prototype, "scrollHeight", originalScrollHeight);
  }
}

afterEach(() => {
  restoreScrollHeightStub();
  currentScrollHeight = 0;
});

describe("MessageList", () => {
  it("scrolls to the bottom on mount and whenever messages change", async () => {
    installScrollHeightStub();
    currentScrollHeight = 200;
    const messages: ChatMessage[] = [{ role: "user", content: "第一条" }];
    const wrapper = mount(MessageList, {
      props: { messages },
    });
    const list = wrapper.find(".message-list").element as HTMLElement;
    await flushPromises();

    expect(list.scrollTop).toBe(200);

    currentScrollHeight = 360;
    messages.push({
      role: "assistant",
      reply: "思考中",
      cards: [],
      toolCalls: [],
      warnings: [],
    });
    await wrapper.setProps({ messages: [...messages] });
    await flushPromises();

    expect(list.scrollTop).toBe(360);

    currentScrollHeight = 520;
    const assistant = messages[1];
    if (assistant.role === "assistant") {
      assistant.reply = "思考中，正在推荐一道晚餐";
    }
    await wrapper.setProps({ messages: [...messages] });
    await nextTick();
    await flushPromises();

    expect(list.scrollTop).toBe(520);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd frontend
npm test -- message-list.spec.ts --run
```

Expected: FAIL，因为当前 `MessageList.vue` 没有列表 DOM 引用，也没有把 `scrollTop` 设置到 `scrollHeight`。

## 5. Task 2: `MessageList.vue` 实现

**Files:**
- Modify: `frontend/src/components/MessageList.vue`

- [ ] **Step 1: Write minimal implementation**

```vue
<template>
  <div ref="listEl" class="message-list">
    <article v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
      <p v-if="message.role === 'user'">{{ message.content }}</p>
      <AssistantMessage v-else :message="message" />
    </article>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import type { ChatMessage } from "../types/chat";
import AssistantMessage from "./AssistantMessage.vue";

const props = defineProps<{ messages: ChatMessage[] }>();
const listEl = ref<HTMLElement | null>(null);

function scrollToBottom() {
  if (listEl.value) {
    listEl.value.scrollTop = listEl.value.scrollHeight;
  }
}

onMounted(scrollToBottom);

watch(() => props.messages, scrollToBottom, { deep: true, flush: "post" });
</script>
```

- [ ] **Step 2: Run focused tests**

Run:

```bash
cd frontend
npm test -- message-list.spec.ts chat-page.spec.ts --run
```

Actual: PASS，2 files / 8 tests passed。

## 6. Task 3: 文档和最终验证

**Files:**
- Modify: `智能食谱助手技术设计.md`
- Modify: `智能食谱助手代码走读.md`

- [ ] **Step 1: Update docs**

更新内容：

1. `智能食谱助手技术设计.md` 版本升级到 v0.39，补充 `MessageList` 自动滚动职责。
2. `智能食谱助手代码走读.md` 版本升级到 v0.17，补充实现说明、测试结果和审查关注点。

- [ ] **Step 2: Run final frontend verification**

Run:

```bash
cd frontend
npm test -- --run
npm run build
```

Actual: 前端测试和构建通过。

## 7. Self-Review

| 检查项 | 结论 |
|--------|------|
| Spec 覆盖 | 覆盖初始渲染、新消息、流式内容变化和职责边界 |
| Placeholder 扫描 | 无 `TBD`、`TODO` 或未定义任务 |
| 类型一致性 | 使用现有 `ChatMessage` 类型，不新增数据结构 |
