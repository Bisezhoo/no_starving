# 智能食谱助手 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于 FastAPI + Vite Vue 3 的智能食谱助手，支持 OpenRouter DeepSeek Agent、多轮对话、3 个 Tool、结构化菜谱/饮品卡片、SSE 流式输出、本地 JSON 画像与 Agent Memory。

**Architecture:** 后端承载全部业务逻辑：请求校验、语言检测、Tool 参数英文归一化、OpenRouter ReAct 编排、外部 API 适配、标准化、推荐排序、持久化和错误降级。前端只负责 Chat 交互、SSE 解析、页签和卡片展示，不直接处理业务规则、密钥、外部 API 或画像合并。

**Tech Stack:** Python 3.11+、FastAPI、Pydantic、httpx、pytest、pytest-asyncio、respx；Vite、Vue 3、TypeScript、Vitest、@vue/test-utils、lucide-vue-next。

---

| 项目 | 内容 |
|------|------|
| 文档版本 | v0.13 |
| 最近更新时间 | 2026-06-14 22:13:12 CST |
| 文档状态 | ✅ 计划已完成 |
| 关联需求 | `智能食谱助手需求分析.md` v0.29 |
| 关联设计 | `智能食谱助手技术设计.md` v0.34 |

## 1. 执行边界

1. 首版只实现单用户、单 Agent、单活跃请求，不引入账号、多 `session`、数据库、Redis 或跨设备同步。
2. 首版唯一 Chat 接口是 `POST /api/chat/stream`，前端用 `fetch + ReadableStream` 解析 SSE，不实现非流式 Chat 接口。
3. OpenRouter 默认使用 DeepSeek 系列模型，具体模型 ID 通过 `OPENROUTER_MODEL` 配置；前端不接触 OpenRouter Key。
4. TheMealDB / TheCocktailDB 的 `limit` 只作为后端候选截取和补详情上限，不传递给外部 API。
5. 后端本地 JSON 文件是首版画像、推荐历史和 Agent Memory 的真实来源；并发控制只依赖 `conversation_lock`，`memory_store` 不加写锁。
6. 所有新增业务能力先写测试，再实现最小代码让测试通过。
7. 编码完成后必须新增代码走读文档，并交给 Claude 做代码审查。

## 2. 文件结构

### 2.1 后端新增文件

| 文件 | 职责 |
|------|------|
| `backend/pyproject.toml` | 后端依赖、pytest 配置和格式化配置 |
| `backend/app/main.py` | FastAPI 应用入口，注册路由和启动检查 |
| `backend/app/api/chat.py` | `POST /api/chat/stream`，只做参数接收、HTTP 错误和流式响应 |
| `backend/app/api/health.py` | 健康检查，暴露配置可用性但不泄露密钥 |
| `backend/app/core/config.py` | 环境变量、超时、模型、日志开关、Agent 步数预算 |
| `backend/app/core/errors.py` | 统一异常类型和 `{ code, message, data }` 响应模型 |
| `backend/app/core/logging.py` | 结构化日志、敏感字段脱敏、敏感日志开关 |
| `backend/app/core/sse.py` | SSE 事件序列化、JSON 转义、事件顺序辅助 |
| `backend/app/domain/models.py` | Pydantic 模型：卡片、画像、推荐历史、Tool、SSE、Agent Memory |
| `backend/app/domain/language.py` | 本轮消息语言检测 |
| `backend/app/domain/card_localization.py` | 按本轮语言为卡片生成本地化摘要和必要步骤展示字段 |
| `backend/app/domain/normalizers.py` | TheMealDB / TheCocktailDB 原始字段清洗与标准化 |
| `backend/app/domain/tool_args.py` | Tool 参数英文归一化、来源追踪、allowlist 校验、修正错误模型 |
| `backend/app/domain/taste_profile.py` | 画像合并、显式偏好覆盖、禁酒硬过滤信号提取 |
| `backend/app/domain/recommendation.py` | 推荐打分、硬过滤、同 ID 去重、主食材/分类/菜系软降权 |
| `backend/app/services/conversation_lock.py` | 单活跃请求锁和死锁防护 |
| `backend/app/services/conversation_state.py` | 单 Agent 内存状态与候选卡片引用 |
| `backend/app/services/memory_store.py` | 本地 JSON 读写、损坏恢复、原子替换 |
| `backend/app/services/openrouter_client.py` | OpenRouter Chat Completions 流式与 Tool Calling 封装 |
| `backend/app/services/tool_runner.py` | Tool Harness：校验、超时、重试、轨迹、错误包装 |
| `backend/app/services/agent_orchestrator.py` | ReAct 主循环、预算熔断、SSE 事件编排、持久化收尾 |
| `backend/app/adapters/mealdb_client.py` | TheMealDB HTTP 客户端 |
| `backend/app/adapters/cocktaildb_client.py` | TheCocktailDB HTTP 客户端 |
| `backend/app/tools/meal_tool.py` | `search_meals`、`get_meal_detail` |
| `backend/app/tools/cocktail_tool.py` | `search_cocktails` |
| `backend/data/.gitkeep` | 保留本地数据目录，JSON 文件运行时生成 |
| `backend/tests/unit/*.py` | 后端单元测试 |
| `backend/tests/integration/*.py` | 后端集成测试 |

### 2.2 前端新增文件

| 文件 | 职责 |
|------|------|
| `frontend/package.json` | 前端脚本和依赖 |
| `frontend/vite.config.ts` | Vite + Vue + Vitest 配置 |
| `frontend/src/main.ts` | Vue 应用入口 |
| `frontend/src/App.vue` | 应用壳 |
| `frontend/src/api/chat.ts` | Chat 请求封装和 HTTP 错误处理 |
| `frontend/src/api/sse.ts` | SSE 流解析 |
| `frontend/src/types/chat.ts` | 前端事件、卡片、画像类型 |
| `frontend/src/components/ChatPage.vue` | Chat 页面状态容器 |
| `frontend/src/components/MessageList.vue` | 消息列表 |
| `frontend/src/components/MessageComposer.vue` | 输入框、发送按钮、前端体验校验 |
| `frontend/src/components/AssistantMessage.vue` | 单条 Agent 消息展示；文本回复直出，按结构化数据决定是否渲染结果区块 |
| `frontend/src/components/MarkdownReply.vue` | 使用 `marked + DOMPurify` 渲染并清洗 Agent Markdown 文本回复 |
| `frontend/src/components/AssistantResultBlock.vue` | 结构化结果区块；仅在 `cards` 非空时展示卡片，并按需承载食材/步骤、Tool、画像变化辅助视图 |
| `frontend/src/components/AssistantMessageTabs.vue` | 旧页签组件，Task 10B 中改造或替换为结果区块，不能再包裹所有 Agent 回复 |
| `frontend/src/components/MealCard.vue` | 菜谱卡片 |
| `frontend/src/components/CocktailCard.vue` | 饮品卡片 |
| `frontend/src/components/ToolTracePanel.vue` | Tool 调用轨迹展示 |
| `frontend/src/components/ProfilePanel.vue` | 本轮画像变化展示 |
| `frontend/src/styles/app.css` | 页面布局、响应式、卡片和页签样式 |
| `frontend/tests/*.spec.ts` | 前端单元测试 |

### 2.3 文档新增文件

| 文件 | 职责 |
|------|------|
| `智能食谱助手代码走读.md` | 编码完成后的模块走读、关键流程、测试结果和审查关注点 |

## 3. 本次实现执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 后端脚手架、配置、统一错误和 SSE 基础 | ✅ 已完成 | `.venv/bin/python -m pytest tests/unit/test_config.py tests/unit/test_sse.py tests/integration/test_health.py -q` 通过，4 passed |
| 2 | 后端领域模型、语言检测和数据标准化 | ✅ 已完成 | `.venv/bin/python -m pytest tests/unit/test_config.py tests/unit/test_sse.py tests/integration/test_health.py tests/unit/test_language.py tests/unit/test_normalizers.py -q` 通过，7 passed |
| 3 | Tool 参数英文归一化、来源追踪和防幻觉校验 | ✅ 已完成 | `.venv/bin/python -m pytest -q` 通过，10 passed |
| 4 | 外部 API Adapter 与 3 个 Tool | ✅ 已完成 | `.venv/bin/python -m pytest -q` 通过，12 passed |
| 5 | 本地 JSON 持久化、画像、推荐历史和单活跃锁 | ✅ 已完成 | `.venv/bin/python -m pytest -q` 通过，19 passed |
| 6 | 推荐排序、防重复和硬过滤/软降权 | ✅ 已完成 | `.venv/bin/python -m pytest -q` 通过，21 passed |
| 7 | OpenRouter 客户端与 Agent ReAct 编排 | ✅ 已完成 | `.venv/bin/python -m pytest -q` 通过，25 passed |
| 8 | FastAPI Chat SSE 集成 | ✅ 已完成 | `.venv/bin/python -m pytest -q` 通过，27 passed |
| 9 | 前端 Vite Vue 基础、类型、API 和 SSE 解析 | ✅ 已完成 | `npm test -- --run` 通过，2 passed；npm 安装使用项目本地 `.npm-cache` |
| 10 | 前端 Chat UI、页签、卡片、Tool 轨迹和画像展示 | ✅ 已完成 | `npm test -- --run` 通过，6 passed；`npm run build` 通过 |
| 10A | 验收补洞：默认 Agent 装配、OpenRouter Step 适配、卡片事件和 memory 持久化闭环 | ✅ 已完成 | `.venv/bin/python -m pytest -q` 通过，32 passed |
| 10B | 前端回复卡片展示层级修正 | ✅ 已完成 | 新增 `chat-page.spec.ts` 覆盖流式回复渲染；前端组件 6 passed；前端全量 12 passed；`npm run build` 通过；已更新代码走读 |
| 10C | Agent 文本基础 Markdown 安全渲染 | ✅ 已完成 | 新增 `MarkdownReply.vue` 和 Markdown 渲染测试；前端组件 7 passed；前端全量 13 passed；`npm run build` 通过；已更新代码走读 |
| 10D | Markdown 渲染切换为 `marked + DOMPurify` | ✅ 已完成 | 已补链接/代码块/清洗测试；安装 `marked`、`dompurify`；前端组件 7 passed；前端全量 13 passed；`npm run build` 通过 |
| 10E | Tool 后语言闭环与卡片本地化 | ✅ 已完成 | 已补 `detectedLocale` 传入 LLM 上下文、Tool 结果语言约束、卡片 `localizedSummary/localizedLanguage/localizedInstructions` 和前端本地化步骤优先展示；后端相关回归 14 passed，前端相关回归 6 passed |
| 10F | 日志安全与结构化日志补齐 | ✅ 已完成 | 新增 `core/logging.py`，补启动、Agent、Tool、OpenRouter、MemoryStore、ChatHistoryStore 结构化日志；敏感字段默认摘要、API Key 始终脱敏；后端全量 57 passed |
| 11 | 全量验证、代码走读文档和审查准备 | ✅ 已完成 | 后端全量 57 passed；前端全量 22 passed；`npm run build` 通过；已更新代码走读 |

## 4. 实现任务

### Task 1: 后端脚手架、配置、统一错误和 SSE 基础

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/health.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/errors.py`
- Create: `backend/app/core/sse.py`
- Create: `backend/tests/unit/test_config.py`
- Create: `backend/tests/unit/test_sse.py`
- Create: `backend/tests/integration/test_health.py`

- [ ] **Step 1: 写配置和 SSE 失败测试**

```python
# backend/tests/unit/test_config.py
from app.core.config import Settings


def test_default_agent_budget_and_log_switches():
    settings = Settings(openrouter_api_key="sk-test", openrouter_model="deepseek/deepseek-chat")
    assert settings.agent_max_tool_calls == 6
    assert settings.agent_max_llm_steps == 4
    assert settings.log_full_user_message is False
    assert settings.log_sensitive_external_headers is False


def test_openrouter_key_is_required():
    try:
        Settings(openrouter_api_key="", openrouter_model="deepseek/deepseek-chat")
    except ValueError as exc:
        assert "OPENROUTER_API_KEY" in str(exc)
    else:
        raise AssertionError("empty OpenRouter key must fail")
```

```python
# backend/tests/unit/test_sse.py
from app.core.sse import format_sse


def test_format_sse_escapes_json_payload():
    event = format_sse("delta", {"text": "hello\nworld"})
    assert event.startswith("event: delta\n")
    assert 'data: {"text":"hello\\nworld"}' in event
    assert event.endswith("\n\n")
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/unit/test_config.py tests/unit/test_sse.py -q
```

Expected: FAIL，原因是 `app.core.config` 和 `app.core.sse` 尚不存在。

- [ ] **Step 3: 实现最小后端基础**

实现签名和行为：

```python
# backend/app/core/config.py
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(alias="OPENROUTER_MODEL")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    mealdb_base_url: str = Field("https://www.themealdb.com/api/json/v1/1", alias="MEALDB_BASE_URL")
    cocktaildb_base_url: str = Field("https://www.thecocktaildb.com/api/json/v1/1", alias="COCKTAILDB_BASE_URL")
    agent_max_tool_calls: int = Field(6, alias="AGENT_MAX_TOOL_CALLS")
    agent_max_llm_steps: int = Field(4, alias="AGENT_MAX_LLM_STEPS")
    log_full_system_prompt: bool = Field(False, alias="LOG_FULL_SYSTEM_PROMPT")
    log_full_user_message: bool = Field(False, alias="LOG_FULL_USER_MESSAGE")
    log_full_source_text: bool = Field(False, alias="LOG_FULL_SOURCE_TEXT")
    log_sensitive_external_headers: bool = Field(False, alias="LOG_SENSITIVE_EXTERNAL_HEADERS")
    log_stack_trace: bool = Field(False, alias="LOG_STACK_TRACE")

    @field_validator("openrouter_api_key", "openrouter_model")
    @classmethod
    def require_non_blank(cls, value: str, info):
        if not value or not value.strip():
            raise ValueError(f"{info.field_name.upper()} is required")
        return value.strip()
```

```python
# backend/app/core/sse.py
import json
from typing import Any


def format_sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event}\ndata: {payload}\n\n"
```

```python
# backend/app/core/errors.py
from fastapi.responses import JSONResponse


class BusinessException(Exception):
    def __init__(self, code: int, message: str, data: dict | None = None):
        self.code = code
        self.message = message
        self.data = data or {}


def error_response(code: int, message: str, data: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=code, content={"code": code, "message": message, "data": data or {}})
```

- [ ] **Step 4: 增加健康检查并运行测试**

```python
# backend/app/api/health.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health():
    return {"code": 200, "message": "success", "data": {"status": "ok"}}
```

```python
# backend/app/main.py
from fastapi import FastAPI

from app.api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="No Starving Recipe Assistant")
    app.include_router(health_router)
    return app


app = create_app()
```

```bash
cd backend
python -m pytest tests/unit/test_config.py tests/unit/test_sse.py tests/integration/test_health.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/pyproject.toml backend/app backend/tests
git commit -m "chore: scaffold FastAPI backend"
```

### Task 2: 后端领域模型、语言检测和数据标准化

**Files:**
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/models.py`
- Create: `backend/app/domain/language.py`
- Create: `backend/app/domain/normalizers.py`
- Create: `backend/tests/unit/test_language.py`
- Create: `backend/tests/unit/test_normalizers.py`

- [ ] **Step 1: 写语言检测和标准化失败测试**

```python
# backend/tests/unit/test_language.py
from app.domain.language import detect_locale


def test_detect_chinese_and_mixed_language():
    assert detect_locale("我想吃 chicken，配什么 drink") == "zh-CN"
    assert detect_locale("I want a light chicken dinner") == "en-US"
```

```python
# backend/tests/unit/test_normalizers.py
from app.domain.normalizers import normalize_meal, normalize_cocktail, is_empty_result


def test_meal_normalizer_pairs_ingredients_and_trims_fields():
    raw = {
        "idMeal": "52795",
        "strMeal": " Chicken Handi ",
        "strMealThumb": "https://img.example/meal.jpg",
        "strCategory": "Chicken",
        "strCountry": "India",
        "strArea": None,
        "strIngredient1": " Chicken ",
        "strMeasure1": " 1 kg ",
        "strIngredient2": "",
        "strMeasure2": "ignored",
        "strIngredient3": "Tomato",
        "strMeasure3": "",
        "strInstructions": "Step one.\\r\\nStep two.",
        "strTags": "Spicy, Meat",
        "strSource": "https://source.example",
        "strYoutube": "",
    }
    card = normalize_meal(raw, detail_level="detail")
    assert card.title == "Chicken Handi"
    assert card.country == "India"
    assert card.ingredients[0].name == "Chicken"
    assert card.ingredients[0].measure == "1 kg"
    assert card.ingredients[1].name == "Tomato"
    assert card.instructions == ["Step one.", "Step two."]
    assert card.tags == ["Spicy", "Meat"]


def test_cocktail_no_data_found_is_only_top_level_empty():
    assert is_empty_result({"drinks": "no data found"}, "drinks") is True
    card = normalize_cocktail({
        "idDrink": "11007",
        "strDrink": "Margarita",
        "strDrinkThumb": "https://img.example/drink.jpg",
        "strCategory": "Ordinary Drink",
        "strAlcoholic": "Alcoholic",
        "strGlass": "Cocktail glass",
        "strInstructions": "no data found",
        "strIngredient1": "Tequila",
        "strMeasure1": "1 1/2 oz",
    }, detail_level="detail")
    assert card.instructions == ["no data found"]
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/unit/test_language.py tests/unit/test_normalizers.py -q
```

Expected: FAIL，原因是领域模型和标准化函数尚不存在。

- [ ] **Step 3: 实现模型和标准化函数**

必须定义这些模型和函数：

```python
# backend/app/domain/models.py
from pydantic import BaseModel, Field
from typing import Any


class IngredientItem(BaseModel):
    name: str
    measure: str | None = None


class MealCard(BaseModel):
    type: str = "meal"
    id: str
    detailLevel: str
    title: str
    localizedTitle: str | None = None
    localizedLanguage: str | None = None
    imageUrl: str
    category: str | None = None
    country: str | None = None
    tags: list[str] = Field(default_factory=list)
    ingredients: list[IngredientItem] = Field(default_factory=list)
    instructions: list[str] | None = None
    localizedSummary: str | None = None
    localizedInstructions: list[str] | None = None
    matchReasons: list[str] | None = None
    sourceUrl: str | None = None
    youtubeUrl: str | None = None


class CocktailCard(BaseModel):
    type: str = "cocktail"
    id: str
    detailLevel: str
    title: str
    localizedTitle: str | None = None
    localizedLanguage: str | None = None
    imageUrl: str
    category: str | None = None
    alcoholic: str | None = None
    glass: str | None = None
    tags: list[str] = Field(default_factory=list)
    ingredients: list[IngredientItem] = Field(default_factory=list)
    instructions: list[str] | None = None
    localizedSummary: str | None = None
    localizedInstructions: list[str] | None = None
    matchReasons: list[str] | None = None


Card = MealCard | CocktailCard


class TasteProfile(BaseModel):
    dietaryRestrictions: list[str] = Field(default_factory=list)
    likedIngredients: list[str] = Field(default_factory=list)
    dislikedIngredients: list[str] = Field(default_factory=list)
    preferredCuisines: list[str] = Field(default_factory=list)
    flavorPreferences: list[str] = Field(default_factory=list)
    allowAlcohol: bool | None = None


class RecommendationRecord(BaseModel):
    itemType: str
    itemId: str
    title: str
    recommendedAt: str
    mainIngredients: list[str] = Field(default_factory=list)
    category: str | None = None
    cuisine: str | None = None
    matchReasons: list[str] = Field(default_factory=list)


class ToolCallSummary(BaseModel):
    id: str
    name: str
    status: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    durationMs: int | None = None
    resultCount: int | None = None
    error: str | None = None


class AgentMemoryCandidate(BaseModel):
    type: str
    id: str
    title: str
    rank: int
    detailLevel: str
    mainIngredients: list[str] = Field(default_factory=list)
    category: str | None = None
    cuisine: str | None = None


class AgentMemory(BaseModel):
    updatedAt: str | None = None
    conversationSummary: str = ""
    recentTurns: list[dict[str, str]] = Field(default_factory=list)
    activeCandidates: list[AgentMemoryCandidate] = Field(default_factory=list)
    lastToolCalls: list[ToolCallSummary] = Field(default_factory=list)
    lastIntent: str | None = None


class SseEvent(BaseModel):
    event: str
    data: dict[str, Any]
```

```python
# backend/app/domain/language.py
def detect_locale(message: str) -> str:
    has_cjk = any("\\u4e00" <= ch <= "\\u9fff" for ch in message)
    return "zh-CN" if has_cjk else "en-US"
```

`normalizers.py` 必须实现：

```python
def clean_text(value: object) -> str | None: ...
def split_tags(value: object) -> list[str]: ...
def split_instructions(value: object) -> list[str] | None: ...
def extract_ingredients(raw: dict, max_items: int) -> list[IngredientItem]: ...
def is_empty_result(payload: dict, root_key: str) -> bool: ...
def normalize_meal(raw: dict, detail_level: str) -> MealCard: ...
def normalize_cocktail(raw: dict, detail_level: str) -> CocktailCard: ...
```

关键规则：

1. `clean_text` 将 `None`、`""`、纯空格、字符串 `"null"` 转为空。
2. 顶层 `drinks: "no data found"` 才算空结果，普通文本不全局清洗该值。
3. 食材为空跳过整行；食材有值且用量为空时保留食材并省略用量；用量有值但食材为空时跳过。
4. 步骤只按换行和明显步骤标记保守拆分，不改写原文。

- [ ] **Step 4: 运行测试**

```bash
cd backend
python -m pytest tests/unit/test_language.py tests/unit/test_normalizers.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/app/domain backend/tests/unit/test_language.py backend/tests/unit/test_normalizers.py
git commit -m "feat: add domain models and normalizers"
```

### Task 3: Tool 参数英文归一化、来源追踪和防幻觉校验

**Files:**
- Create: `backend/app/domain/tool_args.py`
- Create: `backend/tests/unit/test_tool_args.py`

- [ ] **Step 1: 写失败测试**

```python
# backend/tests/unit/test_tool_args.py
from app.domain.tool_args import (
    NormalizedToolArg,
    ToolValidationError,
    normalize_user_terms,
    validate_search_meals_args,
    validate_get_meal_detail_args,
)


def test_chinese_ingredient_normalizes_to_english_with_source():
    args = normalize_user_terms({"ingredient": "鸡肉"}, source="user_message")
    assert args["ingredient"].value == "chicken"
    assert args["ingredient"].sourceText == "鸡肉"
    assert args["ingredient"].source == "user_message"


def test_non_english_query_is_rejected_before_external_api():
    try:
        validate_search_meals_args({"query": NormalizedToolArg(value="鸡肉", sourceText="鸡肉", source="user_message", confidence="high")})
    except ToolValidationError as exc:
        assert exc.field == "query"
        assert exc.retryable is True
    else:
        raise AssertionError("Chinese query must not pass Tool validation")


def test_id_must_come_from_candidate_or_tool_result():
    try:
        validate_get_meal_detail_args({"idMeal": "52795", "source": "user_message"})
    except ToolValidationError as exc:
        assert exc.field == "idMeal"
        assert "candidate" in exc.reason
    else:
        raise AssertionError("LLM generated ID must be rejected")
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/unit/test_tool_args.py -q
```

Expected: FAIL，原因是 `tool_args.py` 尚不存在。

- [ ] **Step 3: 实现最小可测归一化与校验**

必须实现这些类型和函数：

```python
from pydantic import BaseModel


class NormalizedToolArg(BaseModel):
    value: str
    sourceText: str
    source: str
    confidence: str


class ToolValidationError(Exception):
    def __init__(self, field: str, reason: str, retryable: bool, allowed_values: list[str] | None = None):
        self.field = field
        self.reason = reason
        self.retryable = retryable
        self.allowed_values = allowed_values or []


def normalize_user_terms(raw_args: dict[str, str], source: str) -> dict[str, NormalizedToolArg]: ...
def validate_search_meals_args(args: dict) -> dict: ...
def validate_get_meal_detail_args(args: dict) -> dict: ...
def validate_search_cocktails_args(args: dict) -> dict: ...
```

首版内置映射必须至少覆盖测试和核心验收词：

```python
TERM_MAP = {
    "鸡肉": "chicken",
    "牛肉": "beef",
    "猪肉": "pork",
    "鸡蛋": "egg",
    "番茄": "tomato",
    "意大利面": "pasta",
    "素食": "Vegetarian",
    "纯素": "Vegan",
    "日本": "Japanese",
    "日式": "Japanese",
    "印度": "Indian",
}
```

校验规则：

1. `ingredient` / `query` 不得包含中文字符。
2. `limit` 范围是 `1..10`，默认 `5`。
3. `category` / `area` 必须来自 allowlist。
4. `idMeal` / `idDrink` 的来源只能是 `candidate_card`、`tool_result` 或 `external_api`。
5. “随便推荐”不生成假 `ingredient` / `query`。

- [ ] **Step 4: 运行测试**

```bash
cd backend
python -m pytest tests/unit/test_tool_args.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/app/domain/tool_args.py backend/tests/unit/test_tool_args.py
git commit -m "feat: validate and normalize tool arguments"
```

### Task 4: 外部 API Adapter 与 3 个 Tool

**Files:**
- Create: `backend/app/adapters/__init__.py`
- Create: `backend/app/adapters/mealdb_client.py`
- Create: `backend/app/adapters/cocktaildb_client.py`
- Create: `backend/app/tools/__init__.py`
- Create: `backend/app/tools/meal_tool.py`
- Create: `backend/app/tools/cocktail_tool.py`
- Create: `backend/tests/unit/test_meal_tool.py`
- Create: `backend/tests/unit/test_cocktail_tool.py`

- [ ] **Step 1: 写 Tool 失败测试**

```python
# backend/tests/unit/test_meal_tool.py
import pytest
import respx
from httpx import Response

from app.adapters.mealdb_client import MealDbClient
from app.tools.meal_tool import search_meals


@pytest.mark.asyncio
@respx.mock
async def test_search_meals_filter_limits_lookup_count():
    respx.get("https://www.themealdb.com/api/json/v1/1/filter.php").respond(
        200,
        json={"meals": [
            {"idMeal": "1", "strMeal": "A", "strMealThumb": "https://img/a.jpg", "strCountry": "US"},
            {"idMeal": "2", "strMeal": "B", "strMealThumb": "https://img/b.jpg", "strCountry": "US"},
        ]},
    )
    respx.get("https://www.themealdb.com/api/json/v1/1/lookup.php").mock(
        side_effect=[
            Response(200, json={"meals": [{"idMeal": "1", "strMeal": "A", "strMealThumb": "https://img/a.jpg", "strIngredient1": "Chicken", "strMeasure1": "1 kg", "strInstructions": "Cook."}]}),
        ]
    )
    client = MealDbClient(base_url="https://www.themealdb.com/api/json/v1/1", timeout_seconds=8)
    result = await search_meals(client, {"ingredient": "chicken", "limit": 1})
    assert len(result.cards) == 1
    assert result.lookupCount == 1
    assert result.cards[0].id == "1"
```

```python
# backend/tests/unit/test_cocktail_tool.py
import pytest
import respx

from app.adapters.cocktaildb_client import CocktailDbClient
from app.tools.cocktail_tool import search_cocktails


@pytest.mark.asyncio
@respx.mock
async def test_search_cocktails_filters_alcohol_when_user_says_no():
    respx.get("https://www.thecocktaildb.com/api/json/v1/1/search.php").respond(
        200,
        json={"drinks": [
            {"idDrink": "11007", "strDrink": "Margarita", "strDrinkThumb": "https://img/m.jpg", "strAlcoholic": "Alcoholic"},
            {"idDrink": "12720", "strDrink": "Lemonade", "strDrinkThumb": "https://img/l.jpg", "strAlcoholic": "Non alcoholic"},
        ]},
    )
    client = CocktailDbClient(base_url="https://www.thecocktaildb.com/api/json/v1/1", timeout_seconds=8)
    result = await search_cocktails(client, {"query": "lemon", "allowAlcohol": False, "limit": 5})
    assert [card.title for card in result.cards] == ["Lemonade"]
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/unit/test_meal_tool.py tests/unit/test_cocktail_tool.py -q
```

Expected: FAIL，原因是 Adapter 和 Tool 尚不存在。

- [ ] **Step 3: 实现 Adapter 与 Tool 结果模型**

必须提供：

```python
class ToolDataResult(BaseModel):
    status: str
    cards: list[MealCard | CocktailCard]
    resultCount: int
    lookupCount: int = 0
    error: str | None = None
```

Adapter 方法：

```python
class MealDbClient:
    async def search(self, query: str) -> dict: ...
    async def filter_by_ingredient(self, ingredient: str) -> dict: ...
    async def filter_by_category(self, category: str) -> dict: ...
    async def filter_by_area(self, area: str) -> dict: ...
    async def lookup(self, meal_id: str) -> dict: ...
    async def random(self) -> dict: ...


class CocktailDbClient:
    async def search(self, query: str) -> dict: ...
    async def filter_by_ingredient(self, ingredient: str) -> dict: ...
    async def lookup(self, drink_id: str) -> dict: ...
    async def random(self) -> dict: ...
```

Tool 规则：

1. `search_meals` 端点优先级：`ingredient > category > area > query > random`。
2. `search_cocktails` 端点优先级：`ingredient > query > random`。
3. `filter` 后只对截取后的最多 `limit` 条调用 `lookup`。
4. TheMealDB 空搜索只在默认推荐场景使用；TheCocktailDB 默认推荐使用 `random.php`。
5. 同一轮按 ID 去重。

- [ ] **Step 4: 运行测试**

```bash
cd backend
python -m pytest tests/unit/test_meal_tool.py tests/unit/test_cocktail_tool.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/app/adapters backend/app/tools backend/tests/unit/test_meal_tool.py backend/tests/unit/test_cocktail_tool.py
git commit -m "feat: add meal and cocktail tools"
```

### Task 5: 本地 JSON 持久化、画像、推荐历史和单活跃锁

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/memory_store.py`
- Create: `backend/app/services/conversation_lock.py`
- Create: `backend/app/services/conversation_state.py`
- Create: `backend/app/domain/taste_profile.py`
- Create: `backend/data/.gitkeep`
- Create: `backend/tests/unit/test_memory_store.py`
- Create: `backend/tests/unit/test_conversation_lock.py`
- Create: `backend/tests/unit/test_taste_profile.py`

- [ ] **Step 1: 写失败测试**

```python
# backend/tests/unit/test_taste_profile.py
from app.domain.taste_profile import empty_profile, merge_profile_from_message


def test_no_alcohol_message_sets_hard_filter():
    profile, patch = merge_profile_from_message(empty_profile(), "今天不要酒精，推荐一杯清爽的")
    assert profile.allowAlcohol is False
    assert patch["allowAlcohol"] is False


def test_liked_and_disliked_ingredients_are_deduplicated():
    profile, _ = merge_profile_from_message(empty_profile(), "我不吃牛肉，喜欢鸡肉")
    assert profile.dislikedIngredients == ["beef"]
    assert profile.likedIngredients == ["chicken"]
```

```python
# backend/tests/unit/test_conversation_lock.py
import pytest

from app.services.conversation_lock import ConversationLock


@pytest.mark.asyncio
async def test_lock_releases_after_exception():
    lock = ConversationLock()
    try:
        async with lock.acquire("req_1"):
            assert lock.is_locked is True
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert lock.is_locked is False
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/unit/test_taste_profile.py tests/unit/test_conversation_lock.py tests/unit/test_memory_store.py -q
```

Expected: FAIL，原因是持久化、锁和画像模块尚不存在。

- [ ] **Step 3: 实现持久化与锁**

必须实现：

```python
class MemoryStore:
    def __init__(self, data_dir: Path): ...
    async def load_profile(self) -> TasteProfile: ...
    async def load_history(self) -> list[RecommendationRecord]: ...
    async def load_agent_memory(self) -> AgentMemory: ...
    async def save_all(self, profile: TasteProfile, history: list[RecommendationRecord], memory: AgentMemory) -> list[str]: ...
```

```python
class ConversationLock:
    @property
    def is_locked(self) -> bool: ...
    async def acquire(self, request_id: str): ...
```

实现规则：

1. 文件不存在返回空画像、空历史、空 memory。
2. JSON 损坏时返回空数据并记录日志。
3. 写入先写同目录临时文件，再 `replace` 原文件，防止半写。
4. `MemoryStore` 不获取 `conversation_lock`。
5. `ConversationLock` 用 `asynccontextmanager` + `try/finally`，异常和取消都释放。
6. 推荐历史最多保留 20 条，Agent Memory 最近轮次最多 10 条。

- [ ] **Step 4: 运行测试**

```bash
cd backend
python -m pytest tests/unit/test_memory_store.py tests/unit/test_conversation_lock.py tests/unit/test_taste_profile.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/app/services backend/app/domain/taste_profile.py backend/data/.gitkeep backend/tests/unit/test_memory_store.py backend/tests/unit/test_conversation_lock.py backend/tests/unit/test_taste_profile.py
git commit -m "feat: persist single-user memory"
```

### Task 6: 推荐排序、防重复和硬过滤/软降权

**Files:**
- Create: `backend/app/domain/recommendation.py`
- Create: `backend/tests/unit/test_recommendation.py`

- [ ] **Step 1: 写失败测试**

```python
# backend/tests/unit/test_recommendation.py
from app.domain.models import MealCard, RecommendationRecord, TasteProfile
from app.domain.recommendation import rank_recommendations


def meal(item_id: str, title: str, ingredients: list[str], category: str = "Beef") -> MealCard:
    return MealCard(
        id=item_id,
        detailLevel="detail",
        title=title,
        imageUrl="https://img.example/x.jpg",
        category=category,
        country="US",
        tags=[],
        ingredients=[{"name": name} for name in ingredients],
    )


def test_disliked_ingredient_is_hard_filter():
    profile = TasteProfile(dislikedIngredients=["beef"])
    cards, explanation = rank_recommendations([meal("1", "Beef Pie", ["beef"])], profile, [])
    assert cards == []
    assert "hard_filter" in explanation.reasons


def test_recent_main_ingredient_is_soft_downranked():
    profile = TasteProfile()
    history = [
        RecommendationRecord(itemType="meal", itemId="old1", title="A", recommendedAt="2026-06-10T00:00:00Z", mainIngredients=["beef"], matchReasons=[]),
        RecommendationRecord(itemType="meal", itemId="old2", title="B", recommendedAt="2026-06-11T00:00:00Z", mainIngredients=["beef"], matchReasons=[]),
    ]
    cards, explanation = rank_recommendations(
        [meal("1", "Beef Pie", ["beef"]), meal("2", "Chicken Rice", ["chicken"], "Chicken")],
        profile,
        history,
    )
    assert cards[0].id == "2"
    assert "recent_main_ingredient_downrank" in explanation.reasons
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/unit/test_recommendation.py -q
```

Expected: FAIL，原因是推荐模块尚不存在或行为未实现。

- [ ] **Step 3: 实现推荐规则**

必须实现：

```python
def rank_recommendations(cards: list[Card], profile: TasteProfile, history: list[RecommendationRecord]) -> tuple[list[Card], RecommendationExplanation]: ...
def append_history(history: list[RecommendationRecord], displayed_cards: list[Card]) -> list[RecommendationRecord]: ...
```

规则：

1. `dislikedIngredients`、明确饮食限制、`allowAlcohol=false` 是硬过滤。
2. 泛化推荐中最近 10 条同 `itemId` 硬去重。
3. 最近 3 条同主食材出现 2 次以上软降权。
4. 同分类或菜系近期高频软降权。
5. 软降权可回退，硬过滤不可突破。
6. 只把实际展示的卡片追加到推荐历史。

- [ ] **Step 4: 运行测试**

```bash
cd backend
python -m pytest tests/unit/test_recommendation.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/app/domain/recommendation.py backend/tests/unit/test_recommendation.py
git commit -m "feat: rank recommendations with profile history"
```

### Task 7: OpenRouter 客户端与 Agent ReAct 编排

**Files:**
- Create: `backend/app/services/openrouter_client.py`
- Create: `backend/app/services/tool_runner.py`
- Create: `backend/app/services/agent_orchestrator.py`
- Create: `backend/tests/unit/test_tool_runner.py`
- Create: `backend/tests/unit/test_agent_orchestrator.py`

- [ ] **Step 1: 写 ToolRunner 和 Agent 失败测试**

```python
# backend/tests/unit/test_agent_orchestrator.py
import pytest

from app.services.agent_orchestrator import AgentOrchestrator


@pytest.mark.asyncio
async def test_max_tool_calls_stops_loop_and_returns_warning(fake_llm_repeating_tool, fake_tool_runner):
    agent = AgentOrchestrator(
        llm=fake_llm_repeating_tool,
        tool_runner=fake_tool_runner,
        max_tool_calls=1,
        max_llm_steps=4,
    )
    events = [event async for event in agent.run("我想吃鸡肉")]
    done = [event for event in events if event.event == "done"][-1]
    assert "已达 Tool 调用上限" in done.data["warnings"][0]
    assert fake_tool_runner.call_count == 1


@pytest.mark.asyncio
async def test_same_tool_same_args_returns_cached_result(fake_llm_same_tool_twice, fake_tool_runner):
    agent = AgentOrchestrator(
        llm=fake_llm_same_tool_twice,
        tool_runner=fake_tool_runner,
        max_tool_calls=6,
        max_llm_steps=4,
    )
    events = [event async for event in agent.run("我想吃鸡肉")]
    cached = [event for event in events if event.event == "tool_result" and event.data["status"] == "cached"]
    assert len(cached) == 1
    assert fake_tool_runner.external_call_count == 1
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/unit/test_tool_runner.py tests/unit/test_agent_orchestrator.py -q
```

Expected: FAIL，原因是 ToolRunner 和 Agent 尚不存在。

- [ ] **Step 3: 实现 OpenRouter 和 Agent 接口**

必须实现：

```python
class OpenRouterClient:
    async def stream_chat(self, messages: list[dict], tools: list[dict]) -> AsyncIterator[OpenRouterChunk]: ...
```

```python
class ToolRunner:
    async def run(self, tool_name: str, raw_args: dict, request_id: str, retry_of: str | None = None) -> ToolRunResult: ...
```

```python
class AgentOrchestrator:
    async def run(self, message: str) -> AsyncIterator[SseEvent]: ...
```

Agent 规则：

1. `maxToolCalls` 默认 6，`maxLlmSteps` 默认 4。
2. `retryOf` 参数修正整轮 Chat 共享最多 1 次，不是每个 Tool 一次。
3. 同 Tool + 相同归一化参数熔断，第二次返回 `tool_result.status="cached"`。
4. 多个 `tool_calls` 首版串行执行。
5. `delta` 与 `tool_call` 不在同一次 LLM 调用窗口内交错。
6. 不编造 Tool 结果；必要 Tool 全失败时按用户语言说明失败。
7. 收尾必须发送 `done`，并带最终快照和 `warnings`。

- [ ] **Step 4: 运行测试**

```bash
cd backend
python -m pytest tests/unit/test_tool_runner.py tests/unit/test_agent_orchestrator.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/openrouter_client.py backend/app/services/tool_runner.py backend/app/services/agent_orchestrator.py backend/tests/unit/test_tool_runner.py backend/tests/unit/test_agent_orchestrator.py
git commit -m "feat: orchestrate agent tool loop"
```

### Task 8: FastAPI Chat SSE 集成

**Files:**
- Create: `backend/app/api/chat.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/integration/test_chat_stream.py`

- [ ] **Step 1: 写接口失败测试**

```python
# backend/tests/integration/test_chat_stream.py
import pytest
from httpx import AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_chat_rejects_empty_message():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"message": "   "})
    assert response.status_code == 400
    assert response.json()["message"] == "message 不能为空"


@pytest.mark.asyncio
async def test_chat_stream_returns_sse_events(fake_agent_dependency):
    app = create_app(agent=fake_agent_dependency)
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"message": "我想吃鸡肉"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: meta" in response.text
    assert "event: done" in response.text
```

- [ ] **Step 2: 运行失败测试**

```bash
cd backend
python -m pytest tests/integration/test_chat_stream.py -q
```

Expected: FAIL，原因是 Chat 路由尚不存在。

- [ ] **Step 3: 实现 Chat 路由**

实现要求：

1. `POST /api/chat/stream` 请求体只接受 `message`。
2. `message.trim()` 长度必须为 `1..1000`。
3. 空消息和超长消息返回 HTTP JSON，不建立 SSE。
4. `conversation_lock` 已占用时返回 HTTP `409` JSON，不建立 SSE。
5. 请求通过后返回 `StreamingResponse(media_type="text/event-stream")`。
6. SSE 已建立后的运行期错误使用 `error` 事件。
7. 客户端断开、异常、超时都释放 `conversation_lock`。

- [ ] **Step 4: 运行集成测试**

```bash
cd backend
python -m pytest tests/integration/test_chat_stream.py -q
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/chat.py backend/app/main.py backend/tests/integration/test_chat_stream.py
git commit -m "feat: expose streaming chat endpoint"
```

### Task 9: 前端 Vite Vue 基础、类型、API 和 SSE 解析

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/types/chat.ts`
- Create: `frontend/src/api/sse.ts`
- Create: `frontend/src/api/chat.ts`
- Create: `frontend/tests/sse.spec.ts`
- Create: `frontend/tests/chat-api.spec.ts`

- [ ] **Step 1: 写 SSE 解析失败测试**

```ts
// frontend/tests/sse.spec.ts
import { describe, expect, it } from "vitest";
import { parseSseChunk } from "../src/api/sse";

describe("parseSseChunk", () => {
  it("parses done warnings without dropping cards", () => {
    const events = parseSseChunk(
      'event: done\\ndata: {"reply":"ok","cards":[{"type":"meal","id":"1","title":"A"}],"warnings":["本次偏好可能未保存"]}\\n\\n'
    );
    expect(events[0].event).toBe("done");
    expect(events[0].data.cards).toHaveLength(1);
    expect(events[0].data.warnings).toEqual(["本次偏好可能未保存"]);
  });
});
```

- [ ] **Step 2: 运行失败测试**

```bash
cd frontend
npm test -- sse.spec.ts
```

Expected: FAIL，原因是前端项目和 `parseSseChunk` 尚不存在。

- [ ] **Step 3: 实现前端类型、SSE 和 Chat API**

必须定义：

```ts
export type SseEventName =
  | "meta"
  | "delta"
  | "tool_call"
  | "tool_result"
  | "card"
  | "profile_update"
  | "error"
  | "done";

export type ParsedSseEvent = {
  event: SseEventName;
  data: Record<string, unknown>;
};

export function parseSseChunk(chunk: string): ParsedSseEvent[];

export async function streamChat(
  message: string,
  handlers: Record<SseEventName, (data: Record<string, unknown>) => void>,
  signal?: AbortSignal
): Promise<void>;
```

API 规则：

1. 非 2xx HTTP 先读取 JSON 错误并抛出。
2. SSE 中途断开且没有 `done` 时抛出“生成中断，请重试”。
3. 前端不发送 `locale`、`languagePreference`、`tasteProfile`。

- [ ] **Step 4: 运行测试**

```bash
cd frontend
npm test -- sse.spec.ts chat-api.spec.ts
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add frontend/package.json frontend/vite.config.ts frontend/index.html frontend/src frontend/tests
git commit -m "feat: scaffold Vue chat client"
```

### Task 10: 前端 Chat UI、页签、卡片、Tool 轨迹和画像展示

**Files:**
- Create: `frontend/src/components/ChatPage.vue`
- Create: `frontend/src/components/MessageList.vue`
- Create: `frontend/src/components/MessageComposer.vue`
- Create: `frontend/src/components/AssistantMessageTabs.vue`
- Create: `frontend/src/components/MealCard.vue`
- Create: `frontend/src/components/CocktailCard.vue`
- Create: `frontend/src/components/ToolTracePanel.vue`
- Create: `frontend/src/components/ProfilePanel.vue`
- Create: `frontend/src/styles/app.css`
- Create: `frontend/tests/message-composer.spec.ts`
- Create: `frontend/tests/assistant-message-tabs.spec.ts`
- Create: `frontend/tests/cards.spec.ts`

- [ ] **Step 1: 写组件失败测试**

```ts
// frontend/tests/message-composer.spec.ts
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import MessageComposer from "../src/components/MessageComposer.vue";

describe("MessageComposer", () => {
  it("does not submit blank messages", async () => {
    const wrapper = mount(MessageComposer, { props: { disabled: false } });
    await wrapper.find("textarea").setValue("   ");
    await wrapper.find("form").trigger("submit.prevent");
    expect(wrapper.emitted("send")).toBeUndefined();
  });
});
```

```ts
// frontend/tests/assistant-message-tabs.spec.ts
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AssistantMessageTabs from "../src/components/AssistantMessageTabs.vue";

describe("AssistantMessageTabs", () => {
  it("shows non-blocking warnings without hiding cards", () => {
    const wrapper = mount(AssistantMessageTabs, {
      props: {
        message: {
          reply: "ok",
          cards: [{ type: "meal", id: "1", title: "Chicken Handi", imageUrl: "https://img.example/x.jpg", tags: [], ingredients: [] }],
          toolCalls: [],
          warnings: ["本次偏好可能未保存"],
        },
      },
    });
    expect(wrapper.text()).toContain("本次偏好可能未保存");
    expect(wrapper.text()).toContain("Chicken Handi");
  });
});
```

- [ ] **Step 2: 运行失败测试**

```bash
cd frontend
npm test -- message-composer.spec.ts assistant-message-tabs.spec.ts cards.spec.ts
```

Expected: FAIL，原因是组件尚不存在。

- [ ] **Step 3: 实现组件**

组件职责：

1. `ChatPage.vue` 维护消息数组、发送状态和事件归并。
2. `MessageComposer.vue` 做空输入、1000 字符长度、发送中禁用。
3. `AssistantMessageTabs.vue` 提供“回复 / 推荐 / 食材/步骤 / 配饮 / Tool 调用 / 画像变化”页签。
4. `MealCard.vue` 和 `CocktailCard.vue` 只渲染标准化字段，不读取外部原始字段。
5. `ToolTracePanel.vue` 展示 Tool 名称、参数摘要、状态、耗时、结果数、`cached` 和 `validation_failed`。
6. `ProfilePanel.vue` 展示本轮画像变化，不提供复杂编辑。
7. `app.css` 使用克制的工作台风格，保证常见手机宽度和桌面宽度下文本不重叠。

- [ ] **Step 4: 运行组件测试**

```bash
cd frontend
npm test -- message-composer.spec.ts assistant-message-tabs.spec.ts cards.spec.ts
```

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components frontend/src/styles frontend/tests/message-composer.spec.ts frontend/tests/assistant-message-tabs.spec.ts frontend/tests/cards.spec.ts
git commit -m "feat: build chat interface"
```

### Task 10B: 前端回复卡片展示层级修正

**Files:**
- Create: `frontend/src/components/AssistantMessage.vue`
- Create: `frontend/src/components/AssistantResultBlock.vue`
- Modify: `frontend/src/components/MessageList.vue`
- Modify: `frontend/src/components/AssistantMessageTabs.vue`
- Modify: `frontend/src/styles/app.css`
- Create: `frontend/tests/assistant-message.spec.ts`
- Modify: `frontend/tests/assistant-message-tabs.spec.ts`
- Modify: `智能食谱助手代码走读.md`

- [x] **Step 1: 写无卡片场景失败测试**

```ts
// frontend/tests/assistant-message.spec.ts
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AssistantMessage from "../src/components/AssistantMessage.vue";

describe("AssistantMessage", () => {
  it("renders plain assistant reply without result tabs when there are no cards", () => {
    const wrapper = mount(AssistantMessage, {
      props: {
        message: {
          role: "assistant",
          reply: "你好！我是你的食谱助手。",
          cards: [],
          toolCalls: [],
          warnings: [],
          profileUpdates: [],
        },
      },
    });

    expect(wrapper.text()).toContain("你好！我是你的食谱助手。");
    expect(wrapper.text()).not.toContain("推荐");
    expect(wrapper.text()).not.toContain("暂无推荐");
    expect(wrapper.find(".assistant-result-block").exists()).toBe(false);
  });
});
```

- [x] **Step 2: 运行失败测试**

```bash
cd frontend
npm test -- assistant-message.spec.ts
```

Expected: FAIL，原因是 `AssistantMessage.vue` 尚不存在。

- [x] **Step 3: 写有卡片场景失败测试**

```ts
// frontend/tests/assistant-message.spec.ts
it("keeps text reply and renders result block when cards exist", () => {
  const wrapper = mount(AssistantMessage, {
    props: {
      message: {
        role: "assistant",
        reply: "好的，我给你 3 个中餐选择。",
        cards: [
          {
            type: "meal",
            id: "1",
            title: "Chicken Handi",
            localizedSummary: "适合配米饭。",
            imageUrl: "https://img.example/x.jpg",
            tags: [],
            ingredients: [{ name: "Chicken", measure: "500g" }],
          },
        ],
        toolCalls: [],
        warnings: ["本次偏好可能未保存"],
        profileUpdates: [],
      },
    },
  });

  expect(wrapper.text()).toContain("好的，我给你 3 个中餐选择。");
  expect(wrapper.text()).toContain("Chicken Handi");
  expect(wrapper.text()).toContain("本次偏好可能未保存");
  expect(wrapper.find(".assistant-result-block").exists()).toBe(true);
});
```

- [x] **Step 4: 实现最小展示组件**

实现要点：

1. `MessageList.vue` 对 `assistant` 消息渲染 `AssistantMessage.vue`，不再直接渲染 `AssistantMessageTabs.vue`。
2. `AssistantMessage.vue` 始终展示 `message.reply` 和 `message.error`；`message.cards.length > 0` 时才渲染 `AssistantResultBlock.vue`。
3. `AssistantResultBlock.vue` 复用 `MealCard.vue`、`CocktailCard.vue`、`ToolTracePanel.vue`、`ProfilePanel.vue`，结果区内部可以保留轻量视图切换，但不能包裹普通文本回复。
4. `AssistantMessageTabs.vue` 若继续保留，只作为兼容包装或被 `AssistantResultBlock.vue` 替代，不再承担整条 Agent 消息容器职责。

- [x] **Step 5: 运行组件测试**

```bash
cd frontend
npm test -- assistant-message.spec.ts assistant-message-tabs.spec.ts cards.spec.ts
```

Expected: PASS。

- [x] **Step 6: 运行前端全量验证**

```bash
cd frontend
npm test -- --run
npm run build
```

Expected: PASS。

- [x] **Step 7: 更新代码走读文档**

在 `智能食谱助手代码走读.md` 中补充前端展示层级变更：

1. `AssistantMessage.vue` 是 Agent 文本消息入口。
2. `AssistantResultBlock.vue` 只在 `cards` 非空时展示。
3. 无卡片普通回复不会出现推荐空容器。

- [x] **Step 8: 记录本次不提交**

本次不执行 `git commit`：当前工作区已有多项既有未提交改动，且用户未要求提交。需要提交时，可在审查后按实际文件范围手动执行：

```bash
git add frontend/src/components frontend/src/styles/app.css frontend/tests/assistant-message.spec.ts frontend/tests/assistant-message-tabs.spec.ts 智能食谱助手代码走读.md 智能食谱助手需求分析.md 智能食谱助手技术设计.md docs/superpowers/plans/2026-06-14-smart-recipe-assistant.md
git commit -m "fix: adjust assistant result card hierarchy"
```

### Task 10E: Tool 后语言闭环与卡片本地化

**Files:**
- Create: `backend/app/domain/card_localization.py`
- Modify: `backend/app/services/agent_orchestrator.py`
- Modify: `backend/app/services/openrouter_client.py`
- Modify: `backend/app/core/prompts.json`
- Modify: `backend/tests/unit/test_agent_orchestrator.py`
- Modify: `backend/tests/unit/test_openrouter_client.py`
- Create: `backend/tests/unit/test_card_localization.py`
- Modify: `frontend/src/components/AssistantResultBlock.vue`
- Modify: `frontend/tests/cards.spec.ts`
- Modify: `智能食谱助手代码走读.md`

- [x] **Step 1: 写后端失败测试**

验证点：

1. `AgentOrchestrator` 传给 LLM 的上下文包含 `detectedLocale`。
2. Tool 返回卡片后，`card` 事件和 `done.cards` 都包含 `localizedLanguage` 与 `localizedSummary`。
3. 用户询问做法、步骤或详情时，详情卡片包含 `localizedInstructions`。
4. `OpenRouterStepLlm` 组装 Tool 结果消息时，明确要求最终回复使用 `detectedLocale`。

- [x] **Step 2: 运行后端失败测试**

```bash
cd backend
.venv/bin/python -m pytest tests/unit/test_agent_orchestrator.py tests/unit/test_openrouter_client.py tests/unit/test_card_localization.py -q
```

Actual: FAIL，原因是当前上下文没有 `detectedLocale`，Prompt 没有输出语言约束，卡片没有本地化合并层。

- [x] **Step 3: 实现后端最小修复**

实现要点：

1. `AgentOrchestrator` 在 context 中写入 `detectedLocale`。
2. 新增 `card_localization.py`，对返回前卡片生成 `localizedLanguage`、`localizedSummary`，必要时生成 `localizedInstructions`。
3. `OpenRouterStepLlm` 在 system prompt 和 Tool 结果回填消息中显式加入输出语言约束。
4. 不改变 Tool 原始标准化字段，不覆盖 `title`、`instructions`、`ingredients`。

- [x] **Step 4: 写并运行前端失败测试**

验证 `AssistantResultBlock.vue` 在 `localizedInstructions` 存在时优先展示本地化步骤，不再把原始英文步骤作为首选展示。

```bash
cd frontend
npm test -- cards.spec.ts --run
```

Actual: FAIL，原因是 `AssistantResultBlock.vue` 仍直接展示原始 `instructions`。

- [x] **Step 5: 运行回归验证**

```bash
cd backend
.venv/bin/python -m pytest tests/unit/test_language.py tests/unit/test_tool_args.py tests/unit/test_agent_orchestrator.py tests/unit/test_openrouter_client.py tests/unit/test_card_localization.py -q
```

```bash
cd frontend
npm test -- cards.spec.ts assistant-message.spec.ts --run
```

Actual: PASS，后端 14 passed，前端 2 files / 6 tests passed。

- [x] **Step 6: 更新代码走读文档**

补充 Tool 后语言闭环：

1. `detectedLocale` 从 Agent 进入 LLM 上下文。
2. Tool 结果回填时附带输出语言约束。
3. 卡片在发送前合并本地化摘要和必要步骤。
4. 前端步骤展示优先使用 `localizedInstructions`。

Actual: 已更新 `智能食谱助手代码走读.md`。

### Task 11: 全量验证、代码走读文档和审查准备

**Files:**
- Create: `智能食谱助手代码走读.md`
- Modify: `README.md`

- [ ] **Step 1: 运行后端测试**

```bash
cd backend
python -m pytest -q
```

Expected: PASS。

- [ ] **Step 2: 运行前端测试**

```bash
cd frontend
npm test -- --run
```

Expected: PASS。

- [ ] **Step 3: 启动本地服务手工验收**

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

手工验收输入：

1. `我想吃鸡肉，不要太辣`
2. `第一个怎么做`
3. `给我推荐一顿晚餐，不喝酒`
4. `再推荐一个，别总是牛肉`

Expected:

1. 中文回复，Tool 参数为英文，返回菜谱卡片。
2. 复用上一轮候选 ID 获取详情。
3. 有主菜；饮品不包含 `Alcoholic`。
4. 推荐理由说明已尽量换口味。

- [ ] **Step 4: 编写代码走读文档**

`智能食谱助手代码走读.md` 必须包含：

1. 文档版本和最近更新时间。
2. 后端模块走读：API、Agent、ToolRunner、Tool、Adapter、Domain、Memory。
3. 前端模块走读：ChatPage、SSE、页签、卡片、Tool 轨迹、画像展示。
4. 关键流程：中文输入到英文 Tool 参数、`filter -> lookup`、SSE 事件、JSON 持久化、锁释放。
5. 风险点：OpenRouter 模型能力、外部 API 稳定性、JSON 单进程限制、SSE 网关缓冲。
6. 测试结果：后端命令、前端命令、手工验收结果。
7. Claude 审查关注点：并发锁、敏感日志、Tool 参数防幻觉、推荐硬过滤。

- [ ] **Step 5: Commit**

```bash
git add README.md 智能食谱助手代码走读.md
git commit -m "docs: add implementation walkthrough"
```

## 5. 最终验收命令

```bash
cd backend
python -m pytest -q
```

```bash
cd frontend
npm test -- --run
```

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

## 6. 实现期风险与处理

| 风险 | 处理 |
|------|------|
| OpenRouter 当前 DeepSeek 模型不支持 Tool Calling 或 Streaming | 更换 `OPENROUTER_MODEL` 为 OpenRouter 上支持两者的 DeepSeek 模型，不改业务代码 |
| 外部 API 返回字段为空或结构变化 | 标准化层兜底为空数组或缺省字段，前端只消费标准模型 |
| 两个页面同时聊天 | 第二个请求 HTTP `409`，不进入 Agent，不修改 memory |
| JSON 写入失败 | 主回复和卡片照常返回，`done.warnings` 提示本次偏好或历史可能未保存 |
| Agent 重复调用同 Tool 同参数 | ReAct 熔断返回 `cached`，不重复请求外部 API |
| LLM 生成中文 Tool 参数或假 ID | ToolRunner `validation_failed`，Agent 最多修正 1 次，失败后追问或说明 |
| 用户明确不喝酒但候选都是含酒精 | 硬过滤后返回无合适饮品，不主动鼓励饮酒 |

## 7. 自查结果

| 检查项 | 结果 |
|--------|------|
| Spec 覆盖 | 覆盖需求 v0.29 的 Agent、3 个 Tool、多轮、结构化展示、语言转换、轻量画像、推荐历史、本地 JSON、单活跃锁、SSE、日志安全、错误降级、前端回复层级和最近一天聊天记录加载 |
| 技术设计覆盖 | 覆盖技术设计 v0.34 的后端分层、Vue 前端、ToolRunner、ReAct 预算熔断、SSE 事件顺序、`done.warnings`、DeepSeek 配置、禁酒硬过滤、按需结构化结果区和 Tool 后语言闭环 |
| 待定内容扫描 | 未使用待定标记或未定义的实现语句 |
| 类型一致性 | 计划中的 `TasteProfile`、`RecommendationRecord`、`MealCard`、`CocktailCard`、`Card`、`SseEvent` 与技术设计命名保持一致 |
| 简单性检查 | 首版不引入数据库、账号、多 session、WebSocket 或非流式 Chat 接口 |

## 8. 交接说明

执行本计划时，每完成一个 Task 立即更新本文件第 3 节执行计划表状态，并在备注中记录测试结果。全部 Task 完成后，将本文件状态改为“✅ 计划已完成”，再进入代码审查。
