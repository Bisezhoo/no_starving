# 本地 JSON 可靠写入 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将用户画像、推荐历史和 Agent Memory 的本地 JSON 更新方式统一改为“同目录临时文件 + 文件 `fsync` + 原子 `rename` + 目录 `fsync`”，降低进程崩溃或断电造成半写、空文件或目录项未落盘的风险。

**Architecture:** `MemoryStore` 继续作为唯一持久化边界，不新增依赖、不引入额外锁，仍依赖外层 `conversation_lock` 保证单进程内写入串行。`save_all()` 保持现有降级语义：单个 JSON 写入失败时收集 warning，主回复流程不被阻断。可靠写入逻辑集中在 `_atomic_write()`，三份 JSON 共享同一写入路径。

**Tech Stack:** Python 3、FastAPI 后端、pytest、pytest-asyncio、标准库 `json` / `os` / `pathlib`。

---

| 项目 | 内容 |
|------|------|
| 计划版本 | v0.1 |
| 最近更新时间 | 2026-06-14 19:11:15 CST |
| 关联设计 | `智能食谱助手技术设计.md` v0.24 |
| 状态 | 待执行 |

## 1. 成功标准

1. `taste-profile.json`、`recommendation-history.json` 和 `agent-memory.json` 均通过同一个 `_atomic_write()` 可靠写入路径。
2. 写入顺序为：写临时文件内容、`flush`、文件 `fsync`、原子覆盖目标文件、父目录 `fsync`。
3. 临时文件位于目标文件同目录，失败残留不会被读取，后续写入可覆盖同名临时文件。
4. `save_all()` 的 warning 行为保持不变：任一文件写入失败时返回可读 warning，其他文件继续尝试写入。
5. 不执行文件删除命令，不调用任何文件删除 API。
6. 后端相关单元测试通过，代码走读文档同步描述本次可靠写入逻辑。

## 2. 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `backend/tests/unit/test_memory_store.py` | 修改 | 先补充失败测试，验证文件 `fsync`、原子覆盖、目录 `fsync`、失败 warning 和历史裁剪不变 |
| `backend/app/services/memory_store.py` | 修改 | 实现可靠写入路径，保持读取、模型校验和 `save_all()` 外部契约不变 |
| `智能食谱助手代码走读.md` | 修改 | 写完代码后补充本地 JSON 持久化走读说明，便于后续 Claude 审查 |
| `docs/superpowers/plans/2026-06-14-atomic-json-persistence.md` | 修改 | 实施过程中按进度规则更新任务状态 |

## 3. 执行计划表

| 序号 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 1 | 为 `MemoryStore` 可靠写入补充失败测试 | ⏳ 待执行 | 先验证当前实现缺少 `fsync` 和 `os.replace` 路径 |
| 2 | 实现同目录临时文件、文件 `fsync`、原子 `rename` 和目录 `fsync` | ⏳ 待执行 | 最小改动集中在 `_atomic_write()` |
| 3 | 更新代码走读文档 | ⏳ 待执行 | 说明三份 JSON 共用可靠写入路径 |
| 4 | 运行后端验证命令 | ⏳ 待执行 | 先跑 memory_store 单测，再按可用环境跑后端单测集合 |

## 4. 任务拆解

### Task 1: 为 `MemoryStore` 可靠写入补充失败测试

**Files:**
- Modify: `backend/tests/unit/test_memory_store.py`
- Test: `backend/tests/unit/test_memory_store.py`

- [ ] **Step 1: 写入失败测试**

在 `backend/tests/unit/test_memory_store.py` 顶部补充导入：

```python
import json
import os
from pathlib import Path
```

保留现有 `pytest`、领域模型和 `MemoryStore` 导入不变。新增测试函数：

```python
def test_atomic_write_fsyncs_file_before_replace_and_parent_after(tmp_path, monkeypatch):
    store = MemoryStore(tmp_path)
    target = tmp_path / "taste-profile.json"
    calls = []

    real_replace = os.replace

    def track_fsync(fd):
        calls.append(("fsync", fd))

    def track_replace(source, destination):
        calls.append(("replace", Path(source).name, Path(destination).name))
        real_replace(source, destination)

    def track_open(path, flags):
        calls.append(("open_dir", Path(path)))
        return 9876

    def track_close(fd):
        calls.append(("close", fd))

    monkeypatch.setattr(os, "fsync", track_fsync)
    monkeypatch.setattr(os, "replace", track_replace)
    monkeypatch.setattr(os, "open", track_open)
    monkeypatch.setattr(os, "close", track_close)

    store._atomic_write(target, {"likedIngredients": ["chicken"]})

    assert json.loads(target.read_text(encoding="utf-8")) == {"likedIngredients": ["chicken"]}
    assert calls[0][0] == "fsync"
    assert calls[1] == ("replace", "taste-profile.json.tmp", "taste-profile.json")
    assert calls[2] == ("open_dir", tmp_path)
    assert calls[3] == ("fsync", 9876)
    assert calls[4] == ("close", 9876)
```

更新现有失败 warning 测试，让它拦截新的 `os.replace` 路径：

```python
@pytest.mark.asyncio
async def test_save_all_returns_warning_when_atomic_write_fails(tmp_path, monkeypatch):
    store = MemoryStore(tmp_path)

    def fail_replace(source, destination):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", fail_replace)
    warnings = await store.save_all(TasteProfile(), [], AgentMemory())

    assert warnings
    assert "持久化失败" in warnings[0]
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/unit/test_memory_store.py -q
```

Expected: FAIL。至少出现以下两类失败之一：

```text
AssertionError: assert 'fsync' ...
```

或：

```text
assert warnings
```

失败原因应是当前 `_atomic_write()` 使用 `Path.write_text()` 和 `Path.replace()`，没有执行文件 `fsync`、目录 `fsync`，也没有走 `os.replace`。

### Task 2: 实现同目录临时文件、文件 `fsync`、原子 `rename` 和目录 `fsync`

**Files:**
- Modify: `backend/app/services/memory_store.py`
- Test: `backend/tests/unit/test_memory_store.py`

- [ ] **Step 1: 写最小实现**

在 `backend/app/services/memory_store.py` 顶部加入标准库导入：

```python
import json
import os
from pathlib import Path
from typing import Any
```

将 `_atomic_write()` 替换为以下实现，并新增 `_fsync_directory()`：

```python
    def _atomic_write(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.tmp")
        content = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        with temp_path.open("w", encoding="utf-8") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, path)
        self._fsync_directory(path.parent)

    def _fsync_directory(self, directory: Path) -> None:
        dir_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
```

该实现保持固定临时文件名，不删除失败残留文件；失败时异常继续抛给 `save_all()`，由现有 warning 逻辑处理。

- [ ] **Step 2: 运行 memory_store 单测并确认通过**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/unit/test_memory_store.py -q
```

Expected: PASS，输出类似：

```text
5 passed
```

- [ ] **Step 3: 检查实现没有引入额外抽象**

人工检查 `backend/app/services/memory_store.py`，确认只新增 `os` 导入、可靠写入逻辑和目录 `fsync` 小 helper，没有改动读取逻辑、模型校验、历史裁剪上限或 `save_all()` 返回格式。

### Task 3: 更新代码走读文档

**Files:**
- Modify: `智能食谱助手代码走读.md`

- [ ] **Step 1: 更新 `MemoryStore` 走读说明**

在 `智能食谱助手代码走读.md` 的 `backend/app/services/memory_store.py` 相关段落中，将原有本地 JSON 写入描述补充为：

```markdown
- 使用本地 JSON 保存 `taste-profile.json`、`recommendation-history.json`、`agent-memory.json`。
- 三份 JSON 共用同一个可靠写入路径：先写入目标同目录临时文件，刷新缓冲区后对临时文件执行 `fsync`，再通过原子 `rename` 覆盖目标文件，最后对父目录执行 `fsync`，降低崩溃或断电导致半写、空文件或目录项未落盘的风险。
- 写入失败时不阻断主回复流程，由 `save_all()` 返回可读 warning，并通过 SSE `done.warnings` 暴露给前端。
```

- [ ] **Step 2: 检查代码走读文档与设计文档一致**

人工检查 `智能食谱助手技术设计.md` v0.24 与 `智能食谱助手代码走读.md` 的持久化描述，确认二者都表达：

```text
同目录临时文件 -> 文件 fsync -> 原子 rename -> 目录 fsync
```

### Task 4: 运行后端验证命令

**Files:**
- Verify: `backend/tests/unit/test_memory_store.py`
- Verify: `backend/tests/unit`

- [ ] **Step 1: 运行定向单测**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/unit/test_memory_store.py -q
```

Expected: PASS。

- [ ] **Step 2: 运行后端单元测试集合**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/unit -q
```

Expected: PASS。若本地环境缺少 `.venv` 或依赖，改用项目可用 Python 解释器运行等价命令：

```bash
cd backend
python -m pytest tests/unit -q
```

并在最终结果中说明实际使用的命令和输出。

- [ ] **Step 3: 更新本计划执行表**

将本计划第 3 节的任务状态更新为：

```markdown
| 1 | 为 `MemoryStore` 可靠写入补充失败测试 | ✅ 已完成 | 已确认旧实现缺少 `fsync`/`os.replace` 路径 |
| 2 | 实现同目录临时文件、文件 `fsync`、原子 `rename` 和目录 `fsync` | ✅ 已完成 | `_atomic_write()` 已统一三份 JSON 写入路径 |
| 3 | 更新代码走读文档 | ✅ 已完成 | 已同步可靠写入说明 |
| 4 | 运行后端验证命令 | ✅ 已完成 | 记录实际测试命令与结果 |
```

并在执行计划表下方追加：

```markdown
✅ 计划已完成。
```

## 5. 自审记录

1. Spec 覆盖：本计划覆盖 `智能食谱助手技术设计.md` v0.24 中本地 JSON 可靠写入、失败 warning、三份 JSON 共用写入路径、禁止后端删除临时文件的要求。
2. 完整性扫描：本文未留下需要执行者自行补全的空洞内容。
3. 类型一致性：测试和实现均使用现有 `MemoryStore._atomic_write(path: Path, payload: Any) -> None` 签名，`save_all()` 外部返回 `list[str]` 不变。
