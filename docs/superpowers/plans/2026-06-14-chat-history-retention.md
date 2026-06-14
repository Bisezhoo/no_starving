# 最近一天完整聊天记录 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 保存最近 24 小时且最多 60 条完整聊天消息，并在用户进入 Chat 页面时加载展示。

**Architecture:** 新增 `ChatHistoryStore` 独立管理 `backend/data/chat-history.json`，不改变 `AgentMemory` 的摘要职责。后端 `GET /api/chat/history` 负责加载历史，`POST /api/chat/stream` 在 SSE 收尾时追加本轮 user + assistant 消息；前端 `ChatPage` 在挂载时加载历史并沿用现有消息列表渲染。

**Tech Stack:** Python FastAPI、Pydantic、pytest、pytest-asyncio、httpx；Vue 3、TypeScript、Vitest、@vue/test-utils。

---

| 项目 | 内容 |
|------|------|
| 计划版本 | v0.2 |
| 最近更新时间 | 2026-06-14 21:13:52 CST |
| 状态 | ✅ 计划已完成 |
| 关联需求 | `智能食谱助手需求分析.md` v0.29 |
| 关联设计 | `智能食谱助手技术设计.md` v0.34 |
| 关联专项设计 | `docs/superpowers/specs/2026-06-14-chat-history-retention-design.md` v0.2 |

## 1. 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `backend/app/domain/models.py` | 修改 | 新增聊天历史消息模型 |
| `backend/app/services/chat_history_store.py` | 新增 | 读写 `chat-history.json`，执行 24 小时和 60 条裁剪 |
| `backend/app/main.py` | 修改 | 装配 `chat_history_store` |
| `backend/app/api/chat.py` | 修改 | 新增历史加载接口；流式收尾时保存本轮完整消息 |
| `backend/tests/unit/test_chat_history_store.py` | 新增 | TDD 覆盖缺失文件、损坏 JSON、时间裁剪和数量裁剪 |
| `backend/tests/integration/test_chat_stream.py` | 修改 | 覆盖历史接口和 Chat 完成后保存 |
| `frontend/src/types/chat.ts` | 修改 | 为消息类型增加可选 `createdAt` |
| `frontend/src/api/chat.ts` | 修改 | 新增 `loadChatHistory()` |
| `frontend/src/components/ChatPage.vue` | 修改 | 页面挂载时加载历史消息 |
| `frontend/tests/chat-api.spec.ts` | 修改 | 覆盖历史接口错误处理 |
| `frontend/tests/chat-page.spec.ts` | 修改 | 覆盖进入页面加载历史 |
| `智能食谱助手代码走读.md` | 修改 | 实现完成后同步代码走读 |

## 2. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 更新需求、技术设计、专项设计和实施计划 | ✅ 已完成 | 已明确最近 24 小时与最多 60 条消息 |
| 2 | 后端：为聊天历史存储写失败测试 | ✅ 已完成 | `test_chat_history_store.py` 已先失败后通过 |
| 3 | 后端：实现历史模型和 `ChatHistoryStore` | ✅ 已完成 | 已新增独立存储，执行 24 小时和 60 条裁剪 |
| 4 | 后端：为历史接口和流式保存写失败测试 | ✅ 已完成 | 已覆盖 `GET /api/chat/history` 和 `done` 后保存 |
| 5 | 后端：实现接口装配和 SSE 收尾保存 | ✅ 已完成 | 不改变现有 SSE 事件契约 |
| 6 | 前端：为历史 API 与页面加载写失败测试 | ✅ 已完成 | 已覆盖进入页面时渲染历史消息 |
| 7 | 前端：实现 `loadChatHistory()` 和 `onMounted` 加载 | ✅ 已完成 | 历史加载失败不阻断新消息 |
| 8 | 更新代码走读并运行验证 | ✅ 已完成 | 相关后端 9 passed；前端全量 16 passed；构建通过 |

✅ 计划已完成。

## 3. 任务拆解

### Task 1: 后端聊天历史存储

**Files:**
- Create: `backend/app/services/chat_history_store.py`
- Modify: `backend/app/domain/models.py`
- Create: `backend/tests/unit/test_chat_history_store.py`

- [ ] **Step 1: 写失败测试**

新增测试覆盖：

```python
import pytest
from datetime import UTC, datetime, timedelta

from app.domain.models import UserChatHistoryMessage
from app.services.chat_history_store import ChatHistoryStore


@pytest.mark.asyncio
async def test_missing_chat_history_loads_empty_messages(tmp_path):
    store = ChatHistoryStore(tmp_path)

    assert await store.load_messages() == []


@pytest.mark.asyncio
async def test_chat_history_trims_to_recent_24_hours_and_60_messages(tmp_path):
    store = ChatHistoryStore(tmp_path)
    now = datetime(2026, 6, 14, 20, 0, tzinfo=UTC)
    old = UserChatHistoryMessage(role="user", content="old", createdAt=(now - timedelta(hours=25)).isoformat())
    recent = [
        UserChatHistoryMessage(role="user", content=f"u{index}", createdAt=(now - timedelta(minutes=60 - index)).isoformat())
        for index in range(61)
    ]

    warnings = await store.append_messages([old, *recent], now=now)
    messages = await store.load_messages(now=now)

    assert warnings == []
    assert len(messages) == 60
    assert messages[0].content == "u1"
```

- [ ] **Step 2: 运行失败测试**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/unit/test_chat_history_store.py -q
```

Expected: FAIL，原因是 `ChatHistoryStore` 和聊天历史模型尚不存在。

- [ ] **Step 3: 实现最小存储逻辑**

实现要点：

```python
class ChatHistoryStore:
    HISTORY_FILE = "chat-history.json"
    MESSAGE_LIMIT = 60
    RETENTION_HOURS = 24

    async def load_messages(self, now: datetime | None = None) -> list[ChatHistoryMessage]:
        ...

    async def append_messages(self, messages: list[ChatHistoryMessage], now: datetime | None = None) -> list[str]:
        ...
```

`append_messages()` 读取现有消息、追加新消息、按时间窗口过滤，再保留末尾 60 条，最后原子写回 JSON。写入失败返回 warning，不抛出到主流程。

### Task 2: 后端历史接口和流式保存

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/chat.py`
- Modify: `backend/tests/integration/test_chat_stream.py`

- [ ] **Step 1: 写失败测试**

新增集成测试：

```python
async def test_chat_history_returns_saved_messages(tmp_path):
    app = create_app(agent=FakeAgent(), data_dir=tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/chat/stream", json={"message": "你是谁"})
        response = await client.get("/api/chat/history")

    assert response.status_code == 200
    messages = response.json()["data"]["messages"]
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "你是谁"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["reply"] == "收到：你是谁"
```

- [ ] **Step 2: 实现接口和保存**

实现要点：

1. `create_app()` 始终创建 `ChatHistoryStore`，并挂到 `app.state.chat_history_store`。
2. `GET /api/chat/history` 调用 `load_messages()` 并返回统一结构。
3. `event_stream()` 捕获 `profile_update`、`done`、`error` 数据，流结束后调用 `append_messages()`。
4. 保存失败只作为历史持久化 warning，不改变已发送的 SSE 主响应。

### Task 3: 前端历史加载

**Files:**
- Modify: `frontend/src/types/chat.ts`
- Modify: `frontend/src/api/chat.ts`
- Modify: `frontend/src/components/ChatPage.vue`
- Modify: `frontend/tests/chat-api.spec.ts`
- Modify: `frontend/tests/chat-page.spec.ts`

- [ ] **Step 1: 写失败测试**

新增页面测试：

```typescript
it("loads chat history on mount", async () => {
  loadChatHistoryMock.mockResolvedValueOnce([
    { role: "user", content: "昨天想吃什么？", createdAt: "2026-06-14T10:00:00+00:00" },
    { role: "assistant", reply: "推荐鸡肉饭", cards: [], toolCalls: [], warnings: [], createdAt: "2026-06-14T10:00:01+00:00" },
  ]);

  const wrapper = mount(ChatPage);
  await flushPromises();

  expect(wrapper.text()).toContain("昨天想吃什么？");
  expect(wrapper.text()).toContain("推荐鸡肉饭");
});
```

- [ ] **Step 2: 实现最小前端逻辑**

实现要点：

1. `loadChatHistory()` 调用 `GET /api/chat/history`。
2. `ChatPage.vue` 在 `onMounted` 中加载历史并赋值给 `messages`。
3. 历史加载失败时不抛出到页面，不影响用户发送新消息。

## 4. 验证命令

```bash
cd backend
.venv/bin/python -m pytest tests/unit/test_chat_history_store.py tests/integration/test_chat_stream.py -q
```

```bash
cd frontend
npm test -- chat-api.spec.ts chat-page.spec.ts --run
npm run build
```

## 5. 计划自检

1. 覆盖专项设计中的保存、裁剪、加载、错误降级和前端初始化要求。
2. 未引入账号、多 session、数据库、分页或搜索。
3. 计划中的新增模型、存储、接口和前端函数均有明确文件归属。
