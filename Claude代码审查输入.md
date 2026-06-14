# Claude 代码审查输入

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.1 |
| 最近更新时间 | 2026-06-15 00:44:36 CST |
| 文档状态 | ✅ 审查输入已准备 |
| 审查范围 | 当前 working tree 中 Tool 结果统一翻译与前端本地化展示相关改动 |
| 基准提交 | `53e962b81be2267f5bb9e14482a3b65ab6f3247b` |
| 关联需求 | `智能食谱助手需求分析.md` v0.37 |
| 关联设计 | `智能食谱助手技术设计.md` v0.44 |

## 1. 审查目标

请重点审查本次新增的 Tool 结果统一翻译链路是否满足以下要求：

1. Tool 仍只负责查询、清洗和标准化，不直接翻译返回值。
2. 卡片进入 SSE `card` / `done.cards` 前，由后端统一补充 `localized*` 字段。
3. LLM 翻译只能返回本地化 patch，不能覆盖原始 `title`、`ingredients`、`instructions`、ID 或推荐事实字段。
4. patch 必须通过结构校验；非法 patch 或翻译异常不能阻断主回复、卡片展示、画像更新或推荐历史写入。
5. 源语言与目标语言一致时跳过 LLM 翻译。
6. 前端只按 `localized* ?? 原字段` 展示，不自行生成翻译。

## 2. 主要变更文件

| 文件 | 审查重点 |
|------|----------|
| `backend/app/services/card_translation_service.py` | `CardTranslationService`、`OpenRouterCardTranslator`、patch schema、校验与回退 |
| `backend/app/domain/models.py` | `MealCard` / `CocktailCard` 新增本地化字段是否合理 |
| `backend/app/services/agent_orchestrator.py` | 翻译服务调用位置、warning 合并、是否影响推荐排序和持久化 |
| `backend/app/services/default_agent.py` | 默认 Agent 是否正确复用 OpenRouter client 装配翻译器 |
| `frontend/src/types/chat.ts` | 前端 Card 类型是否与后端契约一致 |
| `frontend/src/components/MealCard.vue` | 菜谱卡片本地化标题和 meta 展示优先级 |
| `frontend/src/components/CocktailCard.vue` | 饮品卡片本地化标题和 meta 展示优先级 |
| `frontend/src/components/AssistantResultBlock.vue` | 详情弹窗本地化标题、食材、meta、步骤回退规则 |
| `backend/tests/unit/test_card_translation_service.py` | 翻译服务 TDD 覆盖是否足够 |
| `backend/tests/unit/test_agent_orchestrator.py` | Agent 接入翻译服务的行为覆盖 |
| `frontend/tests/cards.spec.ts` | 前端本地化展示优先级覆盖 |

## 3. 已验证命令

| 命令 | 结果 |
|------|------|
| `cd backend && .venv/bin/python -m pytest` | ✅ 63 passed |
| `cd frontend && npm test -- --run` | ✅ 10 files / 39 tests passed |
| `cd frontend && npm run build` | ✅ 通过 |

注意：后端全量测试需要在 `backend` 目录执行。若从仓库根目录直接运行，`Settings()` 可能读取不到 `backend/.env`，导致配置相关测试失败。

## 4. 重点风险问题

请优先关注这些潜在问题：

1. `CardTranslationPatch` 是否仍可能允许 LLM 改写事实字段或通过嵌套结构绕过校验。
2. `localizedIngredients` / `localizedInstructions` 的长度校验是否足以保证结构不被破坏。
3. `OpenRouterCardTranslator` 复用 OpenRouter streaming client 时，是否会和主 Agent 推理共享超时、日志、安全策略产生问题。
4. `AgentOrchestrator` 在同一轮多次 Tool 查询时，翻译 warning 是否会重复或遮蔽其他 warning。
5. 英文输出跳过翻译的判断是否过于粗糙，是否会影响中英混合场景。
6. 前端使用 `localizedTitle` 后，是否仍需要在 UI 中保留英文原名作为辅助信息。
7. 当前实现未做翻译缓存，是否会导致同一轮重复候选或历史候选重复消耗 LLM。

## 5. 非本次范围

以下问题已记录为后续增强，不要求在本次审查中阻塞：

1. 真实 OpenRouter / TheMealDB / TheCocktailDB 在线冒烟。
2. 外部 API adapter 的 5xx / 网络错误重试一次。
3. 本地 JSON 写入的文件 `fsync` 和目录 `fsync`。
4. 多轮“第一个/刚才那个”的后端确定性引用解析。
5. 更完整的素食、纯素、地区菜系画像提取。

## 6. 审查输出格式建议

请按严重程度输出：

1. Critical：会导致数据损坏、事实篡改、安全泄露、主链路不可用的问题。
2. Important：会导致需求不满足、边界错误、测试缺口或明显维护风险的问题。
3. Minor：命名、局部结构、可读性或后续优化建议。

每条问题请包含：

- 文件路径和具体位置。
- 问题描述。
- 影响。
- 建议修复方向。

## 7. 审查准备执行计划

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 汇总本次实现范围 | ✅ 已完成 | 已限定为 Tool 结果翻译和前端本地化展示 |
| 2 | 汇总主要变更文件 | ✅ 已完成 | 已列出后端、前端和测试文件 |
| 3 | 汇总验证命令 | ✅ 已完成 | 后端全量、前端全量、前端构建均已记录 |
| 4 | 标注重点审查风险 | ✅ 已完成 | 已列出 patch 校验、OpenRouter 复用、warning 合并等关注点 |
