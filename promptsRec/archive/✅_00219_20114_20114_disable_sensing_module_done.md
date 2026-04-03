# Prompt 20114: 禁用 E2E 感知模块

Primary Executor: Claude Code
Task Type: Refactoring
Priority: P2
Stage: 1
Goal: 禁用 Playwright E2E 中的感知模块，避免 SQLite 数据库锁定
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述

`test_runner/playwright_e2e.py` 导入感知模块 `sensing/`，在并发运行时导致 SQLite 数据库锁定：

```
sqlite3.OperationalError: database is locked
```

### 影响

- 感知模块不适合并发测试环境
- 对于内部工具，感知模块属于过度设计
- 需要禁用以提高测试稳定性

---

## Phase 1: PRD - 业务需求分析

- **业务场景**: E2E 测试在 CI/CD 中并发运行时，感知模块导致数据库锁定
- **目标用户**: CI/CD 系统、执行 E2E 测试的开发者
- **核心痛点**: 测试不稳定，频繁因数据库锁定失败
- **业务目标**: 禁用感知模块，恢复测试稳定性

---

## Phase 2: Data - 数据流转

- **受影响文件**: `test_runner/playwright_e2e.py`
- **变更方式**:
  - 注释掉感知模块导入
  - 设置 `SENSING_AVAILABLE = False`
  - 移除对 `sensing.storage` 和 `sensing.orchestrator` 的依赖

---

## Phase 3: Architecture - 架构设计

### 当前架构

```
playwright_e2e.py → sensing.storage (SQLite) → e2e_sensing.db
                → sensing.orchestrator
```

### 目标架构

```
playwright_e2e.py → (sensing disabled)
                 → 直接使用 Playwright + requests
```

### 风险识别

- 禁用感知模块后，相关测试报告功能可能受影响
- 已有数据不丢失（数据库文件保留）

---

## Phase 4: Execution - 精确执行

### 修改 `test_runner/playwright_e2e.py`

```python
# 注释掉感知模块导入
# SENSING_PACKAGE_ROOT = REPO_ROOT / ".skills" / "human-e2e-tester"
# if str(SENSING_PACKAGE_ROOT) not in sys.path:
#     sys.path.insert(0, str(SENSING_PACKAGE_ROOT))

# 强制禁用感知
SENSING_AVAILABLE = False

# 注释掉感知相关代码块
# try:
#     from sensing.storage import SQLiteStorage
#     from sensing.orchestrator import SensingOrchestrator
#     SENSING_AVAILABLE = True
# except ImportError:
#     SENSING_AVAILABLE = False
#     print("[WARN] Sensing module not available, running without sensing")
```

---

## Required Work / 必需工作

- [ ] 注释 `test_runner/playwright_e2e.py` 中的感知模块导入
- [ ] 设置 `SENSING_AVAILABLE = False`（强制禁用）
- [ ] 注释感知初始化代码块
- [ ] 添加注释说明此文件已降级为手动测试
- [ ] 运行 quick_smoke 测试验证

---

## Constraints / 约束条件

- **最小改动**: 只禁用感知模块，不改变测试逻辑
- **不删除文件**: 数据库文件和感知模块文件保留
- **向后兼容**: 仍可通过手动还原启用感知模块

---

## Completion Criteria / 完成标准

1. **感知模块禁用**: `SENSING_AVAILABLE = False`
2. **无导入错误**: 运行 `python -c "import test_runner.playwright_e2e"` 无错误
3. **测试仍可运行**: `python test_runner/playwright_e2e.py --mode quick_smoke` 能启动（可能有 warning 但不 crash）
4. **无数据库锁定错误**: 连续运行两次测试无锁定错误

---

## Verification / 验证

```bash
# 1. 语法检查
python -m py_compile test_runner/playwright_e2e.py

# 2. 运行冒烟测试
python test_runner/playwright_e2e.py --mode quick_smoke

# 预期: 无 "database is locked" 错误
```
