# Prompt: 10178评审后续整改与确认

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P0
Stage: Prompt Number
Goal: 修复 10178 评审发现的遗漏与流程偏差，并完成待确认提示词的正确收口
Dependencies: 10178
Execution: RUNPROMPT

---

## Context

对 `10178_backend_p0_fixes` 的人工评审发现，本次修复尚未达到可确认状态，存在代码遗漏和流程偏差，不能直接视为完成。

当前评审结论摘要：

1. `backend/database/core/database_manager.py` 仍保留大量中文字段名字面量，未满足“无中文字段名字面量”的完成标准
2. `backend/database/repositories/order_repository.py` 中事务路径调用 `add_tool_io_log()` 时仍会吞异常，日志失败不会触发回滚，破坏可追溯性
3. `10178` 提示词文件当前位于 `promptsRec/active/🔶_00185_10178_10178_backend_p0_fixes_done.md`，但运行报告写的是“已归档”，流程状态不一致

本任务是 `10178` 的后续整改与确认任务，不是重新发散设计。必须基于真实现状做最小闭环修复。

---

## Required References

- `backend/database/core/database_manager.py`
- `backend/database/repositories/order_repository.py`
- `backend/database/schema/column_names.py`
- `logs/prompt_task_runs/run_20260401_193238_10178_backend_p0_fixes.md`
- `logs/codex_rectification/rectify_20260401_193238_10178_backend_p0_fixes.md`
- `promptsRec/active/🔶_00185_10178_10178_backend_p0_fixes_done.md`
- `promptsRec/.sequence`
- `.claude/rules/00_core.md`
- `.claude/rules/02_debug.md`
- `.claude/rules/05_task_convention.md`
- `docs/PROMPT_TASK_CONVENTION.md`
- `docs/AI_PIPELINE.md`

---

## Core Task

### 问题1: `database_manager.py` 外部表访问整改不完整

**现象**:
- `get_nonconforming_notices()`
- `get_inspection_records()`
- `get_repair_records()`
- `get_new_rework_applications()`
- `get_new_tooling_applications()`
- `_parse_application_results()`

上述路径仍存在中文字段名字面量、未统一别名、未完成常量收敛的情况。

**要求**:
- 对 `Tooling_ID_Main` 访问必须继续使用 `column_names.py` 常量
- 对其余查询，至少要消除返回映射阶段对原始中文列名的散落依赖，统一通过 SQL alias 收敛
- 若某些外部表暂无常量覆盖，必须在不破坏现有行为前提下最小化中文列名扩散范围，并在日志中明确说明边界

### 问题2: 事务内日志失败不会触发回滚

**现象**:
- `add_tool_io_log()` 捕获异常后直接返回 `False`
- `create_order` / `submit_order` / `keeper_confirm` / `final_confirm` 的事务回调未检查返回值

**要求**:
- 在事务路径中，日志失败必须抛出异常并触发事务回滚
- 不得用“记录失败但业务继续成功”的方式绕过可追溯性要求
- 保持非事务调用方行为可控，避免引入静默兼容问题

### 问题3: RUNPROMPT 归档状态不一致

**现象**:
- 运行报告记录 `10178` 已归档
- 实际文件仍在 `promptsRec/active/`

**要求**:
- 查清真实状态后按仓库规则修正
- 不得删除提示词文件
- 若仍需待确认，保留 `🔶` 前缀，但必须确保 active / archive 状态与报告一致
- 必要时补充运行报告或后续工作记录，明确这次 reviewer 确认后的最终状态

### 问题4: reviewer 确认闭环

**要求**:
- 本任务执行完成后，给出 D3 / D5 / D6 的 reviewer 结论
- 若满足确认条件，将 `10178` 从待确认状态推进到正确归档状态
- 若仍不满足，必须明确卡点，不允许模糊写“已完成”

---

## Required Work

1. 检查 `database_manager.py` 中所有仍使用中文字段名字面量的查询与结果映射，按最小改动原则继续收敛
2. 修复 `add_tool_io_log()` 在事务路径下的异常处理策略，确保日志失败会导致事务失败
3. 为上述修复补充必要的静态验证；如仓库已有测试条件，增加最小回归验证
4. 核对 `10178` 提示词、运行报告、归档状态三者的一致性，并修正流程资产
5. 输出 reviewer 结论，并按规则更新对应日志与归档文件

---

## Constraints

- 必须遵守 `.claude/rules/02_debug.md` 的 8D 协议
- 必须基于真实代码和真实文件状态修复，禁止假设“已经归档”
- 禁止删除 `promptsRec/active/` 或 `promptsRec/archive/` 中的提示词文件
- 所有文本文件必须保持 UTF-8 无 BOM
- 不得引入新的固定默认 `SECRET_KEY`
- 不得破坏 `10178` 已经完成的限流与事务主路径修复
- 禁止把中文字段名扩散到新的 SQL 或新的结果映射分支

---

## Completion Criteria

1. `database_manager.py` 中与本次评审相关的剩余中文字段依赖已被收敛，不再出现散落式结果映射
2. `create_order`、`submit_order`、`keeper_confirm`、`final_confirm` 在日志写入失败时会整体回滚
3. 至少完成以下校验且通过：
   - `python -m py_compile backend/database/core/database_manager.py backend/database/repositories/order_repository.py`
4. reviewer 结论明确给出：通过 / 有条件通过 / 拒绝
5. `10178` 的提示词文件位置、前缀状态、运行报告表述三者一致
6. 本次 RUNPROMPT 衍生的报告、纠正日志、归档动作符合仓库规则
