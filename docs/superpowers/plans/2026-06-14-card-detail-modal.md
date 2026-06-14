# 卡片详情弹窗 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将菜谱和饮品的完整详情从结果区下方长列表迁移到按卡片打开的详情弹窗。

**Architecture:** 后端继续返回完整 `Card[]`，前端只调整展示层。卡片组件负责发出“查看详情”事件，`AssistantResultBlock.vue` 负责维护当前选中卡片并渲染单卡弹窗，CSS 提供遮罩、面板和滚动约束。

**Tech Stack:** Vue 3 `<script setup>`、TypeScript、Vitest、Vue Test Utils、原生 CSS。

---

## 1. 文件职责

| 文件 | 职责 |
|------|------|
| `frontend/tests/cards.spec.ts` | 覆盖详情按钮、默认不平铺详情、打开/关闭弹窗、本地化步骤优先和滑块兼容 |
| `frontend/src/components/MealCard.vue` | 菜谱卡片概要展示，点击按钮向父组件发出 `view-detail` |
| `frontend/src/components/CocktailCard.vue` | 饮品卡片概要展示，点击按钮向父组件发出 `view-detail` |
| `frontend/src/components/AssistantResultBlock.vue` | 维护 `selectedCard`，移除下方详情平铺区，渲染单卡详情弹窗 |
| `frontend/src/styles/app.css` | 提供详情按钮、弹窗遮罩、面板、关闭按钮、食材和步骤列表样式 |
| `智能食谱助手需求分析.md` | 同步前端成功标准和功能需求 |
| `智能食谱助手技术设计.md` | 同步前端展示层级与组件职责 |
| `智能食谱助手代码走读.md` | 编码后记录实现范围、测试结果和审查关注点 |

## 2. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 更新需求、技术设计和本计划文档 | ✅ 已完成 | 已同步 v0.36 / v0.43 / 本计划 |
| 2 | 编写 `cards.spec.ts` 失败测试 | ✅ 已完成 | 红灯：旧实现缺少按钮和弹窗，且直接平铺详情 |
| 3 | 实现卡片详情按钮事件 | ✅ 已完成 | `MealCard.vue`、`CocktailCard.vue` |
| 4 | 实现 `AssistantResultBlock.vue` 详情弹窗 | ✅ 已完成 | 仅展示单卡详情 |
| 5 | 添加弹窗和按钮样式 | ✅ 已完成 | 桌面/移动端均限制弹窗高度并允许滚动 |
| 6 | 运行前端测试与构建 | ✅ 已完成 | 聚焦 + 全量 + build 均通过 |
| 7 | 更新代码走读文档 | ✅ 已完成 | `智能食谱助手代码走读.md` v0.19 |

## 3. Task 1: 文档同步

**Files:**
- Modify: `智能食谱助手需求分析.md`
- Modify: `智能食谱助手技术设计.md`
- Modify: `docs/superpowers/specs/2026-06-14-card-detail-modal-design.md`
- Modify: `docs/superpowers/plans/2026-06-14-card-detail-modal.md`

- [x] **Step 1: 将需求文档版本升到 v0.35**

更新文档头部最近更新时间，并补充成功标准：

```markdown
| S21 | 菜谱和饮品卡片只展示概要信息；点击卡片内“查看详情”按钮后，通过弹窗查看当前单个卡片的完整食材/配料和步骤，结果区下方不再平铺长详情列表 | 前端组件测试 + 手工验收 |
```

- [x] **Step 2: 将技术设计版本升到 v0.42**

更新第 13 节前端展示层级：结果卡片区负责概要展示，完整详情归属单卡弹窗。

## 4. Task 2: 失败测试

**Files:**
- Modify: `frontend/tests/cards.spec.ts`

- [x] **Step 1: 写默认不平铺详情的失败测试**

在 `cards.spec.ts` 中新增测试，期望默认渲染时不出现步骤文本：

```ts
it("does not render card details inline before opening the detail modal", () => {
  const wrapper = mount(AssistantResultBlock, {
    props: {
      message: createAssistantMessage([
        {
          ...createMealCard("1", "Chicken Rice", ["步骤 1：把鸡肉和米饭一起煮熟。"]),
          ingredients: [{ name: "Chicken", measure: "1 lb" }],
        },
      ]),
    },
  });

  expect(wrapper.text()).toContain("Chicken Rice");
  expect(wrapper.text()).toContain("查看详情");
  expect(wrapper.text()).not.toContain("步骤 1：把鸡肉和米饭一起煮熟。");
  expect(wrapper.text()).not.toContain("Chicken · 1 lb");
});
```

- [x] **Step 2: 写打开和关闭弹窗的失败测试**

```ts
it("opens and closes a detail modal for a single card", async () => {
  const wrapper = mount(AssistantResultBlock, {
    props: {
      message: createAssistantMessage([
        {
          ...createMealCard("1", "Chicken Rice", ["步骤 1：把鸡肉和米饭一起煮熟。"]),
          ingredients: [{ name: "Chicken", measure: "1 lb" }],
        },
      ]),
    },
  });

  await wrapper.get("button.card-detail-button").trigger("click");

  expect(wrapper.find(".detail-modal").exists()).toBe(true);
  expect(wrapper.find(".detail-modal").text()).toContain("Chicken Rice");
  expect(wrapper.find(".detail-modal").text()).toContain("Chicken · 1 lb");
  expect(wrapper.find(".detail-modal").text()).toContain("步骤 1：把鸡肉和米饭一起煮熟。");

  await wrapper.get("button.detail-modal-close").trigger("click");

  expect(wrapper.find(".detail-modal").exists()).toBe(false);
});
```

- [x] **Step 3: 写本地化步骤优先的失败测试**

把旧测试从“结果详情区”语义改成“弹窗详情”语义：

```ts
it("prefers localized instructions in the detail modal", async () => {
  const wrapper = mount(AssistantResultBlock, {
    props: {
      message: createAssistantMessage([
        {
          type: "meal",
          id: "1",
          title: "Chicken Rice",
          imageUrl: "",
          tags: [],
          ingredients: [],
          instructions: ["Cook chicken with rice."],
          localizedInstructions: ["步骤 1：把鸡肉和米饭一起煮熟。"],
        },
      ]),
    },
  });

  await wrapper.get("button.card-detail-button").trigger("click");

  expect(wrapper.find(".detail-modal").text()).toContain("步骤 1：把鸡肉和米饭一起煮熟。");
  expect(wrapper.find(".detail-modal").text()).not.toContain("Cook chicken with rice.");
});
```

- [x] **Step 4: 运行测试确认红灯**

Run:

```bash
cd frontend && npm test -- cards.spec.ts --run
```

Expected: FAIL，旧实现没有 `.card-detail-button` 和 `.detail-modal`，并且默认会直接渲染步骤详情。

Actual: FAIL，6 failed，失败原因符合预期：缺少“查看详情”按钮、缺少 `.detail-modal`，旧实现仍平铺 `steps-block`。

## 5. Task 3: 卡片按钮与事件

**Files:**
- Modify: `frontend/src/components/MealCard.vue`
- Modify: `frontend/src/components/CocktailCard.vue`

- [x] **Step 1: `MealCard.vue` 增加事件和按钮**

关键实现：

```vue
<button class="card-detail-button" type="button" @click="$emit('view-detail', card)">
  查看详情
</button>
```

脚本中定义 emit：

```ts
const emit = defineEmits<{ (event: "view-detail", card: MealCard): void }>();
```

- [x] **Step 2: `CocktailCard.vue` 增加同样事件和按钮**

关键实现：

```vue
<button class="card-detail-button" type="button" @click="$emit('view-detail', card)">
  查看详情
</button>
```

脚本中定义 emit：

```ts
const emit = defineEmits<{ (event: "view-detail", card: CocktailCard): void }>();
```

## 6. Task 4: 单卡详情弹窗

**Files:**
- Modify: `frontend/src/components/AssistantResultBlock.vue`

- [x] **Step 1: 增加 `selectedCard` 状态和打开/关闭方法**

```ts
const selectedCard = ref<Card | null>(null);

const openDetail = (card: Card) => {
  selectedCard.value = card;
};

const closeDetail = () => {
  selectedCard.value = null;
};
```

- [x] **Step 2: 卡片组件接收事件**

```vue
<MealCard v-if="isMealCard(card)" :card="card" @view-detail="openDetail" />
<CocktailCard v-else-if="isCocktailCard(card)" :card="card" @view-detail="openDetail" />
```

- [x] **Step 3: 移除原下方 `hasSteps` 详情辅助区**

删除 `v-if="hasSteps"` 的 `result-section`，保留 `stepsFor(card)` 作为弹窗使用。

- [x] **Step 4: 增加弹窗模板**

```vue
<div v-if="selectedCard" class="detail-modal-backdrop" @click.self="closeDetail">
  <article class="detail-modal" role="dialog" aria-modal="true" :aria-label="`${selectedCard.title} 详情`">
    <header class="detail-modal-header">
      <div>
        <p class="detail-modal-eyebrow">推荐详情</p>
        <h3>{{ selectedCard.title }}</h3>
      </div>
      <button class="detail-modal-close" type="button" @click="closeDetail">关闭</button>
    </header>
    <p v-if="selectedCard.localizedSummary" class="muted">{{ selectedCard.localizedSummary }}</p>
    <ul v-if="selectedCard.ingredients?.length" class="detail-ingredient-list">
      <li v-for="ingredient in selectedCard.ingredients" :key="ingredient.name">
        {{ ingredient.name }}<span v-if="ingredient.measure"> · {{ ingredient.measure }}</span>
      </li>
    </ul>
    <ol v-if="stepsFor(selectedCard).length" class="detail-step-list">
      <li v-for="step in stepsFor(selectedCard)" :key="step">{{ step }}</li>
    </ol>
  </article>
</div>
```

## 7. Task 5: 样式

**Files:**
- Modify: `frontend/src/styles/app.css`

- [x] **Step 1: 添加按钮样式**

```css
.card-detail-button {
  width: 100%;
  border: 1px solid #c9d4cf;
  border-radius: 8px;
  background: #ffffff;
  color: #1f6f55;
  padding: 8px 12px;
}
```

- [x] **Step 2: 添加弹窗样式**

```css
.detail-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: grid;
  place-items: center;
  padding: 18px;
  background: rgba(24, 32, 38, 0.42);
}

.detail-modal {
  width: min(720px, 100%);
  max-height: min(82vh, 760px);
  overflow-y: auto;
  border-radius: 8px;
  background: #ffffff;
  padding: 18px;
}
```

## 8. Task 6: 验证

**Files:**
- Test: `frontend/tests/cards.spec.ts`

- [x] **Step 1: 聚焦测试**

Run:

```bash
cd frontend && npm test -- cards.spec.ts --run
```

Expected: PASS。

Actual: PASS，1 file / 9 tests passed。

- [x] **Step 2: 前端全量测试**

Run:

```bash
cd frontend && npm test -- --run
```

Expected: PASS。

Actual: PASS，10 files / 36 tests passed。

- [x] **Step 3: 前端构建**

Run:

```bash
cd frontend && npm run build
```

Expected: PASS。

Actual: PASS，`vue-tsc --noEmit && vite build` 通过。

## 9. Task 7: 代码走读

**Files:**
- Modify: `智能食谱助手代码走读.md`
- Modify: `docs/superpowers/specs/2026-06-14-card-detail-modal-design.md`
- Modify: `docs/superpowers/plans/2026-06-14-card-detail-modal.md`

- [x] **Step 1: 更新代码走读**

补充：

```markdown
- `AssistantResultBlock.vue` 不再在推荐结果下方平铺食材和步骤，而是维护 `selectedCard` 并按需渲染单卡详情弹窗。
- `MealCard.vue` 和 `CocktailCard.vue` 只展示概要信息，通过“查看详情”按钮触发父组件弹窗。
```

- [x] **Step 2: 将计划和设计状态标记为完成**

把执行计划表对应任务更新为 `✅ 已完成`，并追加验证命令结果。

## 10. 自检

1. Spec 覆盖：按钮、弹窗、单卡详情、移除长列表、本地化步骤优先、滑块兼容均有任务覆盖。
2. 占位语扫描：无未完成占位、延期实现描述或模糊任务。
3. 类型一致性：`selectedCard` 使用现有 `Card` 联合类型；事件参数分别使用 `MealCard`、`CocktailCard`，父组件方法接收 `Card`。

✅ 计划已完成。
