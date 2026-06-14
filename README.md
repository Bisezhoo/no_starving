# No Starving 智能食谱助手

| 项目 | 内容 |
|------|------|
| 文档版本 | v1.0 |
| 最近更新时间 | 2026-06-15 01:03:55 CST |
| 文档状态 | 初版整理 |
| 关联需求 | `智能食谱助手需求分析.md` v0.37 |
| 关联设计 | `智能食谱助手技术设计.md` v0.44 |
| 关联部署 | `智能食谱助手部署文档.md` v0.3 |

## 1. 项目简介

No Starving 是一个基于公开菜谱与饮品 API 的智能食谱助手。用户通过 Chat 对话描述想吃什么，后端 Agent 使用 OpenRouter 大模型自主选择 Tool，查询 TheMealDB / TheCocktailDB，并把结果清洗成前端可展示的结构化菜谱卡片和饮品卡片。

当前项目目标是演示版可用：

- 支持自然语言菜谱搜索、菜谱详情查看、饮品搜索和餐食搭配推荐。
- 支持多轮对话、SSE 流式输出、Tool 调用轨迹和最近聊天记录恢复。
- 后端负责意图识别、参数校验、英文查询词归一化、外部 API 清洗、推荐排序、画像维护和卡片本地化翻译校验。
- 前端只负责 Chat 交互、状态展示、结构化卡片展示和本地即时体验校验。

## 2. 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+、FastAPI、httpx、Pydantic、Uvicorn |
| 前端 | Vite、Vue 3、TypeScript、Vitest |
| AI | OpenRouter Tool Calling + Streaming，默认使用 DeepSeek 系列模型 |
| 外部数据 | TheMealDB、TheCocktailDB |
| 本地持久化 | `backend/data/*.json`，不引入数据库 |

## 3. 核心能力

| 能力 | 说明 |
|------|------|
| `search_meals` | 按关键词、食材、分类、地区或随机方式搜索菜谱 |
| `get_meal_detail` | 基于可信来源的 `idMeal` 获取菜谱详情 |
| `search_cocktails` | 按关键词、食材或随机方式搜索饮品 |
| 多轮上下文 | 使用本地 `agent-memory.json` 保存候选卡片引用和对话摘要 |
| 轻量口味画像 | 使用 `taste-profile.json` 保存当前唯一会话内偏好 |
| 推荐历史 | 使用 `recommendation-history.json` 做短期防重复和多样性轮换 |
| 完整聊天历史 | 使用 `chat-history.json` 恢复最近 24 小时、最多 60 条 UI 消息 |
| 卡片本地化 | 后端统一补充 `localized*` 字段，前端优先展示本地化内容 |

## 4. 目录结构

```text
.
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # Chat 与健康检查接口
│   │   ├── adapters/           # TheMealDB / TheCocktailDB HTTP 适配
│   │   ├── core/               # 配置、日志、错误、SSE、Prompt
│   │   ├── domain/             # 标准模型、语言、画像、推荐、参数校验
│   │   ├── services/           # Agent 编排、状态、存储、翻译服务
│   │   └── tools/              # Agent Tool 实现
│   ├── data/                   # 本地 JSON 持久化数据
│   ├── tests/                  # 后端单元测试与集成测试
│   └── pyproject.toml
├── frontend/                   # Vite Vue 前端
│   ├── src/
│   ├── tests/
│   ├── package.json
│   └── vite.config.ts
├── data_interface_testing/     # 外部 API 数据接口分析
├── docs/superpowers/           # 过程中的设计与计划文档
├── 智能食谱助手需求分析.md
├── 智能食谱助手技术设计.md
├── 智能食谱助手部署文档.md
├── 智能食谱助手代码走读.md
├── 任务完成度.md
└── README.md
```

## 5. 本地运行

### 5.1 后端

后端配置使用 `pydantic-settings` 读取当前工作目录下的 `.env`，因此本地启动和测试建议都在 `backend` 目录执行。

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
```

在 `backend/.env` 中配置：

```bash
OPENROUTER_API_KEY=sk-or-v1-replace-me
OPENROUTER_MODEL=deepseek/deepseek-chat
```

可选配置见 [智能食谱助手部署文档.md](智能食谱助手部署文档.md)。

启动后端：

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl -i http://127.0.0.1:8000/api/health
```

期望响应：

```json
{"code":200,"message":"success","data":{"status":"ok"}}
```

### 5.2 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务默认运行在：

```text
http://127.0.0.1:5173
```

`frontend/vite.config.ts` 已配置 `/api` 代理到 `http://127.0.0.1:8000`。

## 6. 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 后端健康检查 |
| `GET` | `/api/chat/history` | 读取最近聊天历史 |
| `POST` | `/api/chat/stream` | Chat 流式接口，返回 SSE 事件 |

`POST /api/chat/stream` 请求体：

```json
{
  "message": "我想吃鸡肉，配一杯清爽饮品"
}
```

SSE 事件包括 `meta`、`delta`、`tool_call`、`card`、`profile_update`、`done`、`error`。前端以 `done.cards` 和 `card` 事件中的标准化卡片作为结构化展示来源。

## 7. 测试与构建

后端测试：

```bash
cd backend
.venv/bin/python -m pytest
```

前端测试：

```bash
cd frontend
npm test -- --run
```

前端构建：

```bash
cd frontend
npm run build
```

最近一次文档记录的验证结果见 [任务完成度.md](任务完成度.md)：后端 63 passed，前端 39 passed，前端构建通过。真实 OpenRouter / TheMealDB / TheCocktailDB 在线冒烟仍建议在交付前单独执行。

## 8. 配置与安全

| 配置 | 默认值 | 说明 |
|------|--------|------|
| `OPENROUTER_API_KEY` | 无 | 必填，OpenRouter API Key |
| `OPENROUTER_MODEL` | 无 | 必填，OpenRouter 模型 ID |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter API 地址 |
| `MEALDB_BASE_URL` | `https://www.themealdb.com/api/json/v1/1` | TheMealDB API 地址 |
| `COCKTAILDB_BASE_URL` | `https://www.thecocktaildb.com/api/json/v1/1` | TheCocktailDB API 地址 |
| `OUTBOUND_HTTP_PROXY` | 空 | 显式出站代理 |
| `OUTBOUND_HTTP_TRUST_ENV` | `true` | 是否读取环境代理配置 |
| `AGENT_MAX_TOOL_CALLS` | `6` | 单轮最大 Tool 调用数 |
| `AGENT_MAX_LLM_STEPS` | `4` | 单轮最大 LLM 推理步数 |

注意事项：

1. 不要把真实 `OPENROUTER_API_KEY` 提交到 Git。
2. 敏感日志开关默认保持关闭，包括完整用户消息、完整 Prompt、完整 Tool 原文和敏感 Header。
3. 前端不得接触 OpenRouter Key、模型配置或外部 API 业务校验逻辑。
4. `backend/data/*.json` 是首版本地状态来源，部署时需要可写权限并纳入备份。

## 9. 设计边界

首版明确不支持：

- 多用户账号体系。
- 多 `session` 或跨设备同步。
- 数据库、Redis 或分布式状态存储。
- 非流式 Chat 降级接口。
- 医疗、营养或过敏风险的专业判断。

这些边界来自当前需求与技术设计，后续如需扩展，应先更新设计文档，再修改代码。

## 10. 文档索引

| 文档 | 用途 |
|------|------|
| [任务.md](任务.md) | 原始任务说明 |
| [智能食谱助手需求分析.md](智能食谱助手需求分析.md) | 业务需求、成功标准和字段规则 |
| [智能食谱助手技术设计.md](智能食谱助手技术设计.md) | 架构设计、模块职责、接口与数据流 |
| [智能食谱助手部署文档.md](智能食谱助手部署文档.md) | 生产部署、环境变量、Nginx 与 systemd 示例 |
| [智能食谱助手代码走读.md](智能食谱助手代码走读.md) | 当前实现走读和审查入口 |
| [任务完成度.md](任务完成度.md) | 完成度、已知缺口和验证结果 |
| [LLM测试计划.md](LLM测试计划.md) | LLM 与 Agent 场景测试计划 |
| [Claude代码审查输入.md](Claude代码审查输入.md) | 提供给 Claude 的代码审查上下文 |

## 11. 已知后续事项

| 优先级 | 事项 | 说明 |
|--------|------|------|
| P0 | 真实在线冒烟 | 使用真实 OpenRouter Key 验证中文菜谱搜索、详情追问、配饮、空结果和翻译 patch |
| P1 | 外部 API 有限重试 | 对 TheMealDB / TheCocktailDB 的 5xx 或网络错误补一次有限重试 |
| P1 | 本地 JSON 可靠写入 | 为状态文件写入补充 `fsync` 策略，或在设计中降低可靠性承诺 |
| P1 | 确定性引用解析 | 为“第一个”“刚才那个”增加不完全依赖 LLM 的兜底解析 |
| P2 | 画像提取增强 | 扩展素食、纯素、地区菜系和口味偏好的规则覆盖 |
