# 全页面固定聊天布局 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Chat 页面调整为顶部标题区贴页面顶部、底部输入区贴页面底部、中间聊天记录独立滚动的全页面布局。

**Architecture:** 本次只修改前端布局层。`ChatPage.vue` 的三段 DOM 结构保持不变，`frontend/src/styles/app.css` 作为唯一布局控制点，通过全高根节点、外层禁止页面滚动和 Grid 中间行 `minmax(0, 1fr)` 实现稳定滚动边界。

**Tech Stack:** Vite + Vue 3 + TypeScript + Vitest + CSS Grid。

---

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.2 |
| 最近更新时间 | 2026-06-14 22:43:54 CST |
| 文档状态 | ✅ 计划已完成 |
| 关联设计 | `docs/superpowers/specs/2026-06-14-full-page-chat-layout-design.md` v0.2 |

## 2. 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `frontend/tests/chat-layout-css.spec.ts` | 新增 | 通过读取 CSS 锁定全页面三段式布局契约 |
| `frontend/src/styles/app.css` | 修改 | 实现根节点全高、页面不滚动、消息列表独立滚动 |
| `智能食谱助手技术设计.md` | 修改 | 同步前端布局设计和文档版本 |
| `智能食谱助手代码走读.md` | 修改 | 同步本次实现、测试结果和审查关注点 |

## 3. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 编写布局 CSS 契约失败测试 | ✅ 已完成 | 当前 CSS 按预期失败：根节点缺少固定高度 |
| 2 | 修改 `app.css` 实现全页面三段式布局 | ✅ 已完成 | 通过 CSS Grid 固定三段布局，不改 DOM 和业务逻辑 |
| 3 | 运行聚焦前端测试 | ✅ 已完成 | `chat-layout-css.spec.ts` 与 `chat-page.spec.ts`：8 passed |
| 4 | 运行前端构建 | ✅ 已完成 | `npm run build` 通过 |
| 5 | 更新代码走读文档 | ✅ 已完成 | v0.16 已记录布局实现和验证结果 |

## 4. Task 1: 布局契约测试

**Files:**
- Create: `frontend/tests/chat-layout-css.spec.ts`

- [ ] **Step 1: Write the failing test**

```ts
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const __dirname = dirname(fileURLToPath(import.meta.url));
const css = readFileSync(resolve(__dirname, "../src/styles/app.css"), "utf-8");

function ruleFor(selector: string) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = css.match(new RegExp(`${escaped}\\s*\\{([^}]*)\\}`, "m"));
  return match?.[1] ?? "";
}

describe("chat page fixed viewport layout", () => {
  it("keeps the page viewport fixed while the message list scrolls", () => {
    expect(ruleFor("html,\nbody,\n#app")).toContain("height: 100%");
    expect(ruleFor(".app-shell")).toContain("height: 100vh");
    expect(ruleFor(".app-shell")).toContain("overflow: hidden");
    expect(ruleFor(".chat-surface")).toContain("height: 100%");
    expect(ruleFor(".chat-surface")).toContain("grid-template-rows: auto minmax(0, 1fr) auto");
    expect(ruleFor(".message-list")).toContain("min-height: 0");
    expect(ruleFor(".message-list")).toContain("overflow-y: auto");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd frontend
npm test -- chat-layout-css.spec.ts --run
```

Expected: FAIL，因为当前 CSS 使用 `min-height` 和 `overflow: auto`，还没有固定页面高度、禁止外层滚动和 `minmax(0, 1fr)`。

## 5. Task 2: CSS 最小实现

**Files:**
- Modify: `frontend/src/styles/app.css`

- [ ] **Step 1: Write minimal implementation**

```css
html,
body,
#app {
  height: 100%;
}

.app-shell {
  height: 100vh;
  overflow: hidden;
}

.chat-surface {
  grid-template-rows: auto minmax(0, 1fr) auto;
  height: 100%;
}

.message-list {
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
}
```

Implementation note: 保留现有颜色、边框、间距和组件结构；只调整高度与滚动边界。

- [ ] **Step 2: Run focused tests**

Run:

```bash
cd frontend
npm test -- chat-layout-css.spec.ts chat-page.spec.ts --run
```

Expected: PASS。

## 6. Task 3: 文档和最终验证

**Files:**
- Modify: `智能食谱助手技术设计.md`
- Modify: `智能食谱助手代码走读.md`

- [ ] **Step 1: Update docs**

更新内容：

1. `智能食谱助手技术设计.md` 版本升级到 v0.38，补充前端全页面固定布局约定。
2. `智能食谱助手代码走读.md` 版本升级到 v0.16，补充 `app.css` 布局实现、测试结果和计划表状态。

- [ ] **Step 2: Run final frontend verification**

Run:

```bash
cd frontend
npm test -- --run
npm run build
```

Expected: 前端测试和构建通过。

## 7. Self-Review

| 检查项 | 结论 |
|--------|------|
| Spec 覆盖 | 覆盖顶部固定、底部固定、中间滚动、页面不整体滚动和不改业务契约 |
| Placeholder 扫描 | 无 `TBD`、`TODO` 或未定义任务 |
| 类型一致性 | 本次不改 TypeScript 类型；CSS selector 与现有文件一致 |
