# Agent 回复结果卡片层级设计

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.1 |
| 最近更新时间 | 2026-06-14 20:02:55 CST |
| 文档状态 | ✅ 已实现 |
| 关联需求 | `智能食谱助手需求分析.md` v0.26 |
| 关联设计 | `智能食谱助手技术设计.md` v0.26 |
| 确认方式 | 用户已确认可视化原型 B |

## 1. 背景

当前前端把所有 Agent 回复都交给 `AssistantMessageTabs.vue` 渲染，导致普通问候、说明、追问类文本也被放进“回复 / 推荐 / 食材/步骤 / Tool 调用 / 画像变化”的页签容器。这个层级过重，也会让没有结构化结果的数据看起来像推荐卡片。

用户确认的目标是：普通回复继续作为文本消息输出；只有后端返回结构化卡片数据时，才把结果转换为卡片展示。

## 2. 目标

1. `delta` 和 `done.reply` 始终进入 Agent 文本区。
2. 只有 `card` 事件或 `done.cards.length > 0` 时，才渲染结构化结果区块。
3. 无卡片时不显示“推荐”“食材/步骤”“暂无推荐”等结果容器。
4. 有卡片时保留文本回复，并在文本下方展示菜谱/饮品卡片。
5. `warnings`、`toolCalls`、`profileUpdates` 不清空文本或卡片；它们只能作为辅助信息展示，不能把普通回复提升为页签容器。

## 3. 非目标

1. 不修改后端 SSE 事件契约。
2. 不修改 `Card` 数据模型。
3. 不新增前端业务判断、推荐排序或字段清洗逻辑。
4. 不引入新的 UI 框架或状态管理库。

## 4. 设计方案

采用前端展示层最小改造：

1. 新增 `AssistantMessage.vue` 作为单条 Agent 消息入口。
2. 新增 `AssistantResultBlock.vue` 作为结构化结果区块。
3. `MessageList.vue` 根据消息角色分发：用户消息仍直接展示气泡，Agent 消息渲染 `AssistantMessage.vue`。
4. `AssistantMessage.vue` 始终渲染文本回复；当 `message.cards.length > 0` 时才渲染 `AssistantResultBlock.vue`。
5. `AssistantResultBlock.vue` 复用 `MealCard.vue` 和 `CocktailCard.vue`，并按需承载 Tool 轨迹和画像变化辅助视图。

## 5. 数据流

```text
SSE delta/done.reply
  -> ChatPage 合并到 AssistantMessage.reply
  -> AssistantMessage 文本区展示

SSE card/done.cards
  -> ChatPage 合并到 AssistantMessage.cards
  -> cards.length > 0 时展示 AssistantResultBlock
  -> MealCard / CocktailCard 按 type 分发
```

## 6. 错误与空状态

1. 外部 API 空结果时，后端用 `reply` 说明原因；前端不额外展示“暂无推荐”卡片容器。
2. `message.error` 在文本区附近展示，不触发结果区块。
3. `warnings` 作为非阻塞提示展示，不能替换或清空 `reply`、`cards`。
4. Tool 失败轨迹可在辅助区展示；如果没有卡片，普通回复仍然保持文本形态。

## 7. 测试方案

| 测试 | 断言 |
|------|------|
| 无卡片 Agent 回复 | 文本出现；不出现“推荐”“暂无推荐”；`.assistant-result-block` 不存在 |
| 有卡片 Agent 回复 | 文本出现；卡片标题出现；`.assistant-result-block` 存在 |
| 有 `warnings` | 警告出现；文本和卡片不被清空 |
| 旧卡片组件 | `MealCard` / `CocktailCard` 缺失字段仍不崩溃 |

## 8. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 更新需求、技术设计和计划文档 | ✅ 已完成 | 已同步 v0.26 / v0.5 |
| 2 | 编写前端无卡片/有卡片测试 | ✅ 已完成 | 新增 `frontend/tests/assistant-message.spec.ts` |
| 3 | 实现 `AssistantMessage` 与 `AssistantResultBlock` | ✅ 已完成 | 最小展示层改造完成 |
| 4 | 运行前端测试与构建 | ✅ 已完成 | `npm test -- --run` 11 passed；`npm run build` 通过 |
| 5 | 更新代码走读文档 | ✅ 已完成 | 已更新 `智能食谱助手代码走读.md` v0.3 |

## 9. 方案取舍

推荐方案是不改后端契约，只调整前端展示层。原因是 `card` 事件与 `done.cards` 已经能表达结构化结果是否存在，错误发生在前端把整条 Agent 消息无条件页签化。改后端会扩大影响面，继续隐藏/显示旧页签组件则容易保留错误职责边界。
