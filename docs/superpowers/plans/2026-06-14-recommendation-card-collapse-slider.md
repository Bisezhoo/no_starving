# 推荐结果默认收起与横向滑块实现计划

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.2 |
| 最近更新时间 | 2026-06-14 21:33:56 CST |
| 文档状态 | ✅ 已完成 |
| 关联设计 | `docs/superpowers/specs/2026-06-14-recommendation-card-collapse-slider-design.md` v0.2 |

## 1. 目标

让 `AssistantResultBlock.vue` 在推荐结果超过 3 个时默认只展示前 3 个，点击“查看更多”后以横向滑块展示全部卡片，并通过同一个按钮“收起”恢复默认态。

## 2. 文件职责

| 文件 | 职责 |
|------|------|
| `frontend/tests/cards.spec.ts` | 覆盖默认 3 个、无溢出不显示按钮、展开全部、横向模式和收起 |
| `frontend/src/components/AssistantResultBlock.vue` | 管理 `isExpanded`、`visibleCards`、按钮和按类型分发卡片组件 |
| `frontend/src/styles/app.css` | 提供默认网格与展开横向滑块样式 |
| `智能食谱助手需求分析.md` | 同步成功标准与前端需求 |
| `智能食谱助手技术设计.md` | 同步前端职责、展示规则和测试重点 |
| `智能食谱助手代码走读.md` | 记录最终实现和验证结果 |

## 3. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 编写 `cards.spec.ts` 失败测试 | ✅ 已完成 | 旧实现失败原因：第 4 张卡片和步骤仍出现，且不存在 `.result-toggle` |
| 2 | 实现 `AssistantResultBlock.vue` 的 `visibleCards` 和切换按钮 | ✅ 已完成 | 默认 3 个，展开全部，收起恢复 |
| 3 | 将步骤区绑定到 `visibleCards` | ✅ 已完成 | 隐藏卡片步骤不会提前露出 |
| 4 | 添加 `.card-slider` 横向滚动样式 | ✅ 已完成 | `display:flex` + `overflow-x:auto` + `scroll-snap-type` |
| 5 | 运行聚焦测试 | ✅ 已完成 | `cd frontend && npm test -- cards.spec.ts assistant-message.spec.ts --run`，9 tests passed |
| 6 | 运行前端全量测试 | ✅ 已完成 | `cd frontend && npm test -- --run`，7 files / 19 tests passed |
| 7 | 运行前端构建 | ✅ 已完成 | `cd frontend && npm run build` 通过 |
| 8 | 更新代码走读文档 | ✅ 已完成 | `智能食谱助手代码走读.md` v0.12 |

✅ 计划已完成。

## 4. TDD 记录

1. 先新增超过 3 个推荐时默认隐藏第 4 个推荐和步骤的测试，旧实现按预期失败。
2. 先新增点击“查看更多/收起”的测试，旧实现按预期失败，因为按钮和横向模式不存在。
3. 再实现 `visibleCards`、按钮和横向 class，使测试转绿。

## 5. 验证命令

```bash
cd frontend && npm test -- cards.spec.ts --run
cd frontend && npm test -- cards.spec.ts assistant-message.spec.ts --run
cd frontend && npm test -- --run
cd frontend && npm run build
```
