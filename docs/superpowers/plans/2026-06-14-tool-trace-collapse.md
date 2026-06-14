# Tool Trace Collapse Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 Tool 调用轨迹默认缩略为一行小字，点击后再展开明细。

**Architecture:** 折叠状态放在 `ToolTracePanel.vue` 内部，调用方继续只传 `items`。组件测试先覆盖默认折叠、展开、再次收起和空状态，再实现最小前端改动。

**Tech Stack:** Vue 3、TypeScript、Vitest、@vue/test-utils、lucide-vue-next。

---

## 0. 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.1 |
| 最近更新时间 | 2026-06-14 23:46:47 CST |
| 文档状态 | ✅ 已完成 |
| 关联设计 | `docs/superpowers/specs/2026-06-14-tool-trace-collapse-design.md` v0.1 |

## 1. 文件职责

| 文件 | 职责 |
|------|------|
| `frontend/tests/tool-trace-panel.spec.ts` | 新增组件测试，验证默认折叠、点击展开/收起、空状态 |
| `frontend/src/components/ToolTracePanel.vue` | 管理 `isExpanded`，渲染轻量摘要按钮和展开明细 |
| `frontend/src/styles/app.css` | 调整 Tool 轨迹摘要和明细样式 |
| `智能食谱助手需求分析.md` | 同步前端 Tool 调用展示成功标准 |
| `智能食谱助手技术设计.md` | 同步 `ToolTracePanel.vue` 职责和 SSE 展示规则 |
| `智能食谱助手代码走读.md` | 完成后记录实现范围和验证结果 |

## 2. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 编写 `ToolTracePanel` 默认折叠失败测试 | ✅ 已完成 | 旧实现按预期失败：直接出现 Tool 明细，且不存在 `.tool-trace-toggle` |
| 2 | 实现 `ToolTracePanel.vue` 折叠摘要 | ✅ 已完成 | 默认 `isExpanded=false` |
| 3 | 实现展开/收起交互和样式 | ✅ 已完成 | 摘要按钮点击切换 |
| 4 | 运行聚焦测试 | ✅ 已完成 | `tool-trace-panel.spec.ts` 3 tests passed |
| 5 | 运行前端全量测试和构建 | ✅ 已完成 | 前端全量 10 files / 36 tests passed；构建通过 |
| 6 | 更新代码走读文档和计划状态 | ✅ 已完成 | 已记录验证命令与结果 |

✅ 计划已完成。

## 3. TDD 步骤

### Task 1: ToolTracePanel 默认折叠测试

**Files:**
- Create: `frontend/tests/tool-trace-panel.spec.ts`
- Modify: `docs/superpowers/plans/2026-06-14-tool-trace-collapse.md`

- [x] **Step 1: Write the failing test**

```ts
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ToolTracePanel from "../src/components/ToolTracePanel.vue";

const toolCalls = [
  { id: "1", name: "search_meals", status: "success", resultCount: 5, durationMs: 11829 },
  { id: "2", name: "search_meals", status: "success", resultCount: 10, durationMs: 17941 },
];

describe("ToolTracePanel", () => {
  it("collapses tool calls into a compact summary by default", () => {
    const wrapper = mount(ToolTracePanel, {
      props: { items: toolCalls },
    });

    expect(wrapper.text()).toContain("Loaded 2 tools");
    expect(wrapper.text()).not.toContain("search_meals");
    expect(wrapper.text()).not.toContain("success");
    expect(wrapper.text()).not.toContain("11829ms");
  });

  it("expands and collapses tool call details when clicking the summary", async () => {
    const wrapper = mount(ToolTracePanel, {
      props: { items: toolCalls },
    });

    await wrapper.get("button.tool-trace-toggle").trigger("click");

    expect(wrapper.text()).toContain("search_meals");
    expect(wrapper.text()).toContain("success");
    expect(wrapper.text()).toContain("5 results");
    expect(wrapper.text()).toContain("11829ms");

    await wrapper.get("button.tool-trace-toggle").trigger("click");

    expect(wrapper.text()).toContain("Loaded 2 tools");
    expect(wrapper.text()).not.toContain("11829ms");
  });

  it("keeps the existing empty state when there are no tool calls", () => {
    const wrapper = mount(ToolTracePanel, {
      props: { items: [] },
    });

    expect(wrapper.text()).toContain("暂无 Tool 调用");
    expect(wrapper.find("button.tool-trace-toggle").exists()).toBe(false);
  });
});
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
cd frontend && npm test -- tool-trace-panel.spec.ts --run
```

Expected: FAIL because the current component renders `search_meals` and `success` immediately and has no `.tool-trace-toggle` button.

Actual: FAIL，2 failed / 1 passed，失败原因与预期一致。

### Task 2: ToolTracePanel 折叠实现

**Files:**
- Modify: `frontend/src/components/ToolTracePanel.vue`
- Modify: `frontend/src/styles/app.css`

- [x] **Step 1: Write minimal implementation**

```vue
<template>
  <div v-if="!items.length" class="trace-list">
    <p class="muted">暂无 Tool 调用</p>
  </div>
  <div v-else class="tool-trace-panel">
    <button class="tool-trace-toggle" type="button" :aria-expanded="isExpanded" @click="toggleExpanded">
      <SquareTerminal :size="16" aria-hidden="true" />
      <span>Loaded {{ items.length }} tools</span>
      <ChevronDown v-if="isExpanded" :size="15" aria-hidden="true" />
      <ChevronRight v-else :size="15" aria-hidden="true" />
    </button>

    <div v-if="isExpanded" class="trace-list trace-list-expanded">
      <article v-for="item in items" :key="item.id || `${item.name}-${item.status}`" class="trace-item">
        <div>
          <strong>{{ item.name }}</strong>
          <span>{{ item.status }}</span>
        </div>
        <small>
          <span v-if="item.resultCount !== undefined">{{ item.resultCount }} results</span>
          <span v-if="item.durationMs !== undefined"> · {{ item.durationMs }}ms</span>
        </small>
        <p v-if="item.error" class="warning">{{ item.error }}</p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ChevronDown, ChevronRight, SquareTerminal } from "lucide-vue-next";
import type { ToolTraceItem } from "../types/chat";

defineProps<{ items: ToolTraceItem[] }>();

const isExpanded = ref(false);
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};
</script>
```

```css
.tool-trace-panel {
  display: grid;
  gap: 6px;
}

.tool-trace-toggle {
  border: 0;
  background: transparent;
  color: #66746e;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  justify-self: start;
  padding: 2px 0;
  font-size: 13px;
}

.tool-trace-toggle:hover {
  color: #182026;
}

.trace-list-expanded {
  margin-top: 2px;
}
```

- [x] **Step 2: Run focused test to verify it passes**

Run:

```bash
cd frontend && npm test -- tool-trace-panel.spec.ts --run
```

Expected: PASS for the new `ToolTracePanel` tests.

Actual: PASS，`tool-trace-panel.spec.ts` 3 tests passed。

### Task 3: 回归验证与文档收尾

**Files:**
- Modify: `智能食谱助手代码走读.md`
- Modify: `docs/superpowers/specs/2026-06-14-tool-trace-collapse-design.md`
- Modify: `docs/superpowers/plans/2026-06-14-tool-trace-collapse.md`

- [x] **Step 1: Run frontend regression tests**

Run:

```bash
cd frontend && npm test -- tool-trace-panel.spec.ts cards.spec.ts assistant-message.spec.ts --run
cd frontend && npm test -- --run
cd frontend && npm run build
```

Expected: all commands exit 0.

Actual: `tool-trace-panel.spec.ts cards.spec.ts assistant-message.spec.ts` 14 tests passed；前端全量 10 files / 36 tests passed；`npm run build` 通过。

- [x] **Step 2: Update implementation docs**

Mark design and plan tasks complete, then add code walkthrough notes:

```markdown
`frontend/src/components/ToolTracePanel.vue`：

- Tool 调用默认折叠为 `Loaded N tools` 小字状态行，弱化调试信息对推荐正文的干扰。
- 点击状态行后展示每次 Tool 调用的名称、状态、结果数、耗时和错误信息；再次点击收起。
- 空 Tool 调用继续展示“暂无 Tool 调用”。
```

## 4. 自检

1. 设计覆盖：默认折叠、点击展开、点击收起、空状态均有任务和测试。
2. 占位扫描：本文档无 `TBD` / `TODO` / 未定义路径。
3. 类型一致：继续使用现有 `ToolTraceItem`，不新增 API 字段。
