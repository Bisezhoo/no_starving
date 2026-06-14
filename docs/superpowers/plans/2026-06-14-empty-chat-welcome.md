# 空聊天默认欢迎语 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 当 Chat 页面没有历史消息时展示默认食谱助手欢迎语，有历史时不重复插入。

**Architecture:** 只在前端 `ChatPage.vue` 初始化消息列表时处理空态。后端 `GET /api/chat/history`、`chat-history.json`、Agent Memory、画像和推荐历史均不改变；欢迎语是本地 UI 消息，复用现有 `AssistantMessage` 渲染链路。

**Tech Stack:** Vue 3、TypeScript、Vitest、@vue/test-utils。

---

| 项目 | 内容 |
|------|------|
| 计划版本 | v0.1 |
| 最近更新时间 | 2026-06-14 22:28:24 CST |
| 状态 | ⏳ 待执行 |
| 关联需求 | `智能食谱助手需求分析.md` v0.32 |
| 关联设计 | `智能食谱助手技术设计.md` v0.37 |
| 关联专项设计 | `docs/superpowers/specs/2026-06-14-empty-chat-welcome-design.md` v0.2 |

## 1. 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `frontend/tests/chat-page.spec.ts` | 修改 | TDD 覆盖空历史欢迎语、已有历史不插入欢迎语、历史加载失败仍展示欢迎语并可发送 |
| `frontend/src/components/ChatPage.vue` | 修改 | 新增默认欢迎语消息工厂，并在历史为空或加载失败时初始化空态消息 |
| `智能食谱助手代码走读.md` | 修改 | 编码完成后同步默认欢迎语实现说明、关联计划和验证结果 |
| `docs/superpowers/specs/2026-06-14-empty-chat-welcome-design.md` | 修改 | 随实施进度更新执行计划表状态 |
| `docs/superpowers/plans/2026-06-14-empty-chat-welcome.md` | 修改 | 随实施进度更新执行计划表状态 |

## 2. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 前端：编写空历史欢迎语失败测试 | ⏳ 待执行 | 先验证当前空历史页面不会显示欢迎语 |
| 2 | 前端：实现默认欢迎语初始化 | ⏳ 待执行 | 只改 `ChatPage.vue`，不改后端 |
| 3 | 前端：补充历史加载失败与发送测试 | ⏳ 待执行 | 确保失败降级和发送流程可用 |
| 4 | 文档：更新代码走读和计划状态 | ⏳ 待执行 | 同步文档版本、最近更新时间和验证结果 |
| 5 | 验证：运行前端定向测试和构建 | ⏳ 待执行 | `chat-page.spec.ts`、前端构建通过 |

## 3. 任务拆解

### Task 1: 前端空历史欢迎语

**Files:**
- Modify: `frontend/tests/chat-page.spec.ts`
- Modify: `frontend/src/components/ChatPage.vue`

- [ ] **Step 1: 写空历史失败测试**

在 `frontend/tests/chat-page.spec.ts` 的 `describe("ChatPage", ...)` 中新增测试：

```ts
it("shows default welcome message when chat history is empty", async () => {
  loadChatHistoryMock.mockResolvedValueOnce([]);

  const wrapper = mount(ChatPage);
  await flushPromises();

  expect(loadChatHistoryMock).toHaveBeenCalledOnce();
  expect(wrapper.text()).toContain("你好！我是你的 食谱助手（Recipe Assistant）");
  expect(wrapper.text()).toContain("搜索菜肴食谱");
  expect(wrapper.text()).toContain("查找饮品配方");
  expect(wrapper.text()).toContain("有什么想做的菜或想喝的饮品");
});
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```bash
cd frontend
npm test -- chat-page.spec.ts --run
```

Expected: FAIL，新增测试无法找到 `"你好！我是你的 食谱助手（Recipe Assistant）"`，因为当前空历史时 `messages` 仍为空数组。

- [ ] **Step 3: 实现最小欢迎语工厂**

在 `frontend/src/components/ChatPage.vue` 的 `messages` 和 `sending` 声明后新增常量与工厂函数：

```ts
const DEFAULT_WELCOME_REPLY = `你好！我是你的 食谱助手（Recipe Assistant） 🍳🥗

简单来说，我是一位专门帮你查找各种美味菜肴和饮品食谱的智能助手！无论你想做什么菜、调制什么饮品，我都能帮你找到合适的食谱。

🍽️ 我能做什么？
🥘 搜索菜肴食谱 — 根据菜名、食材、菜系或类别来查找各种美食（中餐、意大利菜、墨西哥菜等）
🍹 查找饮品配方 — 搜索鸡尾酒、无酒精饮料等各种饮品配方
📋 提供详细信息 — 包括食材清单、烹饪步骤、份量等
💡 我可以帮你解决这些场景：
🏠 今晚吃什么？ → 帮你推荐菜肴
🛒 冰箱里有鸡肉和洋葱 → 帮你找能做的菜
🎉 朋友聚会调杯酒 → 帮你查鸡尾酒配方
🥗 想吃素食/低卡/某国菜系 → 帮你精准搜索
有什么想做的菜或想喝的饮品，尽管告诉我吧！😊`;

function createDefaultWelcomeMessage(): AssistantMessage {
  return {
    role: "assistant",
    reply: DEFAULT_WELCOME_REPLY,
    cards: [],
    toolCalls: [],
    warnings: [],
    profileUpdates: [],
  };
}
```

将 `onMounted` 改为：

```ts
onMounted(async () => {
  try {
    const history = await loadChatHistory();
    if (messages.value.length === 0) {
      messages.value = history.length > 0 ? history : [createDefaultWelcomeMessage()];
    }
  } catch {
    if (messages.value.length === 0) {
      messages.value = [createDefaultWelcomeMessage()];
    }
  }
});
```

该实现保留现有“如果用户已发送消息，就不覆盖消息列表”的保护；历史失败时也不清空用户已输入产生的消息。

- [ ] **Step 4: 运行测试确认通过**

Run:

```bash
cd frontend
npm test -- chat-page.spec.ts --run
```

Expected: PASS，`ChatPage` 相关测试全部通过。

### Task 2: 历史存在和历史失败保护

**Files:**
- Modify: `frontend/tests/chat-page.spec.ts`
- Modify: `frontend/src/components/ChatPage.vue`

- [ ] **Step 1: 写历史存在时不插入欢迎语测试**

在 `frontend/tests/chat-page.spec.ts` 中补充测试：

```ts
it("does not insert default welcome message when chat history exists", async () => {
  loadChatHistoryMock.mockResolvedValueOnce([
    { role: "user", content: "昨天想吃什么？", createdAt: "2026-06-14T10:00:00+00:00" },
    {
      role: "assistant",
      reply: "推荐鸡肉饭",
      cards: [],
      toolCalls: [],
      warnings: [],
      createdAt: "2026-06-14T10:00:01+00:00",
    },
  ]);

  const wrapper = mount(ChatPage);
  await flushPromises();

  expect(wrapper.text()).toContain("昨天想吃什么？");
  expect(wrapper.text()).toContain("推荐鸡肉饭");
  expect(wrapper.text()).not.toContain("你好！我是你的 食谱助手（Recipe Assistant）");
});
```

- [ ] **Step 2: 写历史加载失败时展示欢迎语且可发送测试**

在 `frontend/tests/chat-page.spec.ts` 中补充测试：

```ts
it("shows default welcome message and still sends when chat history fails", async () => {
  loadChatHistoryMock.mockRejectedValueOnce(new Error("history unavailable"));
  streamChatMock.mockImplementationOnce(async (_message: string, handlers: StreamHandlers) => {
    handlers.done?.({
      reply: "推荐鸡肉饭",
      cards: [],
      toolCalls: [],
      warnings: [],
    });
  });

  const wrapper = mount(ChatPage);
  await flushPromises();

  expect(wrapper.text()).toContain("你好！我是你的 食谱助手（Recipe Assistant）");

  await wrapper.find("textarea").setValue("推荐一道晚餐");
  await wrapper.find("form").trigger("submit.prevent");
  await flushPromises();

  expect(streamChatMock).toHaveBeenCalledWith("推荐一道晚餐", expect.any(Object));
  expect(wrapper.text()).toContain("推荐一道晚餐");
  expect(wrapper.text()).toContain("推荐鸡肉饭");
});
```

- [ ] **Step 3: 运行测试确认行为**

Run:

```bash
cd frontend
npm test -- chat-page.spec.ts --run
```

Expected: PASS，空历史、有历史、历史失败和现有流式消息测试全部通过。

### Task 3: 文档与验证收口

**Files:**
- Modify: `智能食谱助手代码走读.md`
- Modify: `docs/superpowers/specs/2026-06-14-empty-chat-welcome-design.md`
- Modify: `docs/superpowers/plans/2026-06-14-empty-chat-welcome.md`

- [ ] **Step 1: 更新代码走读文档**

将 `智能食谱助手代码走读.md` 文档版本提升到下一版本，最近更新时间使用实际执行时间，并在实现范围或前端走读段落补充：

```markdown
- 前端在 `ChatPage.vue` 页面挂载时加载历史；当历史为空或加载失败时，用本地 `AssistantMessage` 展示默认食谱助手欢迎语。
- 默认欢迎语只属于 UI 空态，不写入 `chat-history.json`，不进入 Agent Memory、画像、推荐历史或 LLM 上下文。
```

同时把关联计划追加：

```markdown
`docs/superpowers/plans/2026-06-14-empty-chat-welcome.md` v0.2
```

- [ ] **Step 2: 更新专项设计和实施计划状态**

将 `docs/superpowers/specs/2026-06-14-empty-chat-welcome-design.md` 更新为 v0.3，执行计划表中任务 2~5 标记为 `✅ 已完成`，并写明测试和构建结果。

将本计划更新为 v0.2，执行计划表中任务 1~5 标记为 `✅ 已完成`，状态改为 `✅ 计划已完成`。

- [ ] **Step 3: 运行最终验证**

Run:

```bash
cd frontend
npm test -- chat-page.spec.ts --run
npm run build
```

Expected: `chat-page.spec.ts` 通过，`npm run build` 完成，无 TypeScript 或 Vite 构建错误。

## 4. 验证命令

```bash
cd frontend
npm test -- chat-page.spec.ts --run
npm run build
```

## 5. 计划自检

| 检查项 | 结果 |
|--------|------|
| Spec 覆盖 | 覆盖空历史、历史存在、历史加载失败、发送消息、非持久化边界 |
| 后端边界 | 不修改后端接口、JSON 文件、Agent Memory、画像或推荐历史 |
| 类型一致性 | 欢迎语复用现有 `AssistantMessage` 类型，不新增消息类型 |
| TDD 顺序 | 先写失败测试，再实现最小代码，再补失败保护测试和验证 |
| 占位扫描 | 无未决占位；所有代码步骤给出具体文件、代码片段和命令 |
