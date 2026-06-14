# Tool 调用默认折叠展示设计

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.1 |
| 最近更新时间 | 2026-06-14 23:46:47 CST |
| 文档状态 | ✅ 已实现 |
| 关联需求 | `智能食谱助手需求分析.md` v0.36 |
| 关联设计 | `智能食谱助手技术设计.md` v0.43 |
| 确认方式 | 用户确认方案 A：在 `ToolTracePanel.vue` 内部统一默认折叠 |

## 1. 背景

当前前端把每个 Tool 调用渲染为独立大卡片，`search_meals`、`success`、结果数和耗时会在推荐结果下方直接平铺。截图显示该区域视觉重量过高，并夹在正文、步骤和画像 JSON 之间，影响用户阅读推荐结果。

用户希望参考 Codex 的工具状态设计：默认把所有工具调用缩略成一行小字，点击后再展示执行过的工具调用明细。

## 2. 目标

1. `ToolTracePanel.vue` 在 `items.length > 0` 时默认折叠。
2. 折叠态只展示一行轻量状态入口，文案为 `Loaded N tools`。
3. 折叠态入口使用终端图标和展开箭头，视觉上弱于正文和推荐卡片。
4. 点击入口后展开，展示每次 Tool 调用的名称、状态、结果数、耗时和错误信息。
5. 再次点击入口后收起，恢复一行小字。
6. `items.length === 0` 时保留现有“暂无 Tool 调用”空状态。
7. `AssistantResultBlock.vue` 和旧 `AssistantMessageTabs.vue` 继续复用同一个 `ToolTracePanel.vue`，不在调用方重复实现折叠逻辑。

## 3. 非目标

1. 不修改后端 SSE 事件契约。
2. 不修改 `ToolTraceItem` 类型字段。
3. 不新增 Tool 调用排序、合并、去重或状态流转规则。
4. 不改变 `ProfilePanel.vue` 的画像 JSON 展示方式。
5. 不引入新的 UI 组件库；继续使用现有 `lucide-vue-next` 图标。

## 4. 方案选择

推荐方案 A：在 `ToolTracePanel.vue` 内部统一默认折叠。

| 方案 | 说明 | 结论 |
|------|------|------|
| A | `ToolTracePanel.vue` 自己管理折叠状态，所有入口统一生效 | 采用 |
| B | 在 `AssistantResultBlock.vue` 外层包折叠逻辑 | 不采用，旧页签和结果区行为会不一致 |
| C | 后端新增 Tool 摘要字段 | 不采用，展示问题不应扩大到后端契约 |

方案 A 改动最小，职责也最清晰：Tool 轨迹如何展示由 Tool 轨迹组件自己负责；调用方只传入 `items`。

## 5. 组件设计

`ToolTracePanel.vue` 新增本地状态 `isExpanded=false`。

折叠态结构：

```text
button.tool-trace-toggle
  SquareTerminal icon
  Loaded N tools
  ChevronRight icon
```

展开态结构：

```text
button.tool-trace-toggle
  SquareTerminal icon
  Loaded N tools
  ChevronDown icon

div.trace-list.expanded
  article.trace-item x N
```

Tool 明细沿用现有信息，不展示完整 `arguments`，避免把 Tool 参数摘要区变成大段 JSON。

## 6. 样式设计

1. `.tool-trace-panel` 作为外层容器，宽度随父容器。
2. `.tool-trace-toggle` 使用透明背景、无边框、小字号、灰色文字，类似 Codex 的工具状态行。
3. 图标尺寸控制在 16px，和小字对齐。
4. `.trace-list.expanded` 在展开后增加轻微顶部间距。
5. `.trace-item` 保留 8px 圆角，但减少 padding 和边框视觉重量。

## 7. 测试方案

| 测试 | 断言 |
|------|------|
| 有 Tool 调用默认折叠 | 出现 `Loaded 2 tools`；不出现 `success`、`5 results`、`11829ms` 等明细 |
| 点击摘要展开 | 明细出现；按钮仍显示 `Loaded 2 tools`；展开态图标对应向下箭头 |
| 再次点击收起 | 明细隐藏；摘要仍存在 |
| 空 Tool 调用 | 继续展示“暂无 Tool 调用” |

## 8. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 更新需求、技术设计和本设计文档 | ✅ 已完成 | 已补充 Tool 调用默认折叠规则 |
| 2 | 编写 `ToolTracePanel` 失败测试 | ✅ 已完成 | 旧实现按预期失败：默认显示 Tool 明细且没有 `.tool-trace-toggle` |
| 3 | 实现 `ToolTracePanel.vue` 折叠/展开 | ✅ 已完成 | 组件内部状态，调用方不变 |
| 4 | 添加轻量摘要与展开明细样式 | ✅ 已完成 | 参考 Codex 小字状态行 |
| 5 | 运行前端聚焦测试与构建 | ✅ 已完成 | 前端全量 10 files / 36 tests passed；构建通过 |
| 6 | 更新代码走读文档 | ✅ 已完成 | 已同步 `智能食谱助手代码走读.md` v0.19 |

✅ 计划已完成。

## 9. 方案取舍

本次只解决 Tool 调用展示过重的问题，不顺手调整画像 JSON、推荐步骤或后端 Tool 数据。这样能把改动控制在前端展示组件和对应测试内，避免让一次 UI 收敛牵出后端契约变化。
