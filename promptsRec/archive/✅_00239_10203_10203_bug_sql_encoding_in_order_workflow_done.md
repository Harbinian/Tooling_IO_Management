---
name: 10203_bug_sql_encoding_in_order_workflow
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/02_debug.md
  - .claude/rules/00_core.md
version: 1.0.0
---

# 10203: Bug修复 - SQL 编码错误导致数据完整性风险

## Header / 头部信息

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P0
Stage: 10203
Goal: 修复 order_workflow_service.py assign_transport 中 SQL 乱码问题，防止数据写入错误列
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

架构评审代码审查发现 `backend/services/order_workflow_service.py` 第 209-215 行存在 SQL 编码错误。

**乱码示例**（终端输出编码问题导致显示为乱码，实际文件中也是乱码）：
```python
update_sql = """
    UPDATE tool_io_order
    SET ææ­·æµæ¯'D = ?,
        ææ­·æµæå"˜éš? = ?,
        æ·‡æ¿ˆî…¸é›æ¨¼'ç'‡ã††æ¤‚é—‚? = ?,
        æ·‡î†½æ•¼éƒƒå ã¤æ£¿ = SYSDATETIME()
    WHERE é"'å"„å†…æ'¬æ'³å´Ÿé™? = ?
"""
```

这些乱码字符本应是中文字段名，但直接写在 SQL 中违反了 `column_names.py` 字段名常量规范。

**影响**：
- 运行时 SQL 执行失败
- 或数据写入错误列，导致数据完整性风险

---

## D1 - 团队分工 / Team Assignment

| 角色 | 负责人 |
|------|--------|
| Coder | Claude Code |
| Reviewer | 待指定 |
| Architect | Claude Code |

---

## D2 - 问题描述 / Problem Description

**已观测证据**（来自架构评审代码审查）：

| 证据类型 | 内容 |
|----------|------|
| 代码审查 | `backend/services/order_workflow_service.py` 第 209-215 行存在 ææ­·æµæ¯'D 等乱码字符 |
| 违规类型 | SQL 语句直接使用中文字符串，未通过 `ORDER_COLUMNS` 常量引用 |
| 影响范围 | `assign_transport` 函数（line 186），涉及订单运输状态更新 |

**实际文件位置**：
- 问题函数：`backend/services/order_workflow_service.py` line 186 `def assign_transport(...)`
- 乱码 SQL：`backend/services/order_workflow_service.py` line 209-215

**D2 禁止内容**：根因分析留待 D4。

---

## D3 - 临时遏制措施 / Containment

**爆炸半径评估**：
- 影响文件：`backend/services/order_workflow_service.py`
- 影响函数：`assign_transport`（唯一使用乱码 SQL 的函数）
- 影响 API：POST `/api/tool-io-orders/<order_no>/assign-transport`
- 风险等级：P0 - 数据完整性风险

**临时措施**：
1. 在修复完成前，**禁止执行** `assign_transport` 相关功能
2. 如生产环境需要紧急使用，手动禁用该 API 端点

---

## D4 - 根因分析 / Root Cause Analysis

使用 5 Whys 分析：

**Why 1**: 为什么存在乱码字符？
→ 开发者将中文字符串直接写入 SQL，未使用字段名常量

**Why 2**: 为什么未使用字段名常量？
→ 可能是不熟悉 `column_names.py` 规范，或在复制粘贴过程中编码丢失

**Why 3**: 为什么编码会丢失？
→ 文件在传输或编辑过程中可能经历了多次编码转换

**系统级根因**：
- 缺少 G1-2 pre-commit hook 检测中文字段名
- 建议添加 static analysis 检测

---

## D5 - 永久对策 / Permanent Countermeasures

**修改文件**：
- `backend/services/order_workflow_service.py`

**修复方案**：
1. 将乱码字符替换为正确的 `ORDER_COLUMNS` 常量引用
2. 使用 `from backend.database.schema.column_names import ORDER_COLUMNS`
3. 确保所有中文字段名通过常量访问

**具体常量名需执行时从 `column_names.py` 确认，以下为推断**：
- 运输状态字段 → `ORDER_COLUMNS['transport_status']` 或类似
- 运输员字段 → `ORDER_COLUMNS['transport_operator']` 或类似
- 运输员姓名 → `ORDER_COLUMNS['transport_operator_name']` 或类似
- 运输联系方式 → `ORDER_COLUMNS['transport_contact']` 或类似
- 订单号 → `ORDER_COLUMNS['order_no']`

**防退化宣誓**：
- 未来所有 SQL 中的中文字段名必须通过 `column_names.py` 访问
- 添加 G1-2 pre-commit hook 检测（见 D7）

---

## D6 - 实施验证 / Implementation

**执行步骤**：

1. 读取 `backend/services/order_workflow_service.py`，定位乱码 SQL 位置
2. 读取 `backend/database/schema/column_names.py`，获取正确的常量名称
3. 将乱码 SQL 改写为使用 `ORDER_COLUMNS` 常量：
   ```python
   update_sql = f"""
       UPDATE tool_io_order
       SET {ORDER_COLUMNS['transport_status']} = ?,
           {ORDER_COLUMNS['transport_operator']} = ?,
           {ORDER_COLUMNS['transport_operator_name']} = ?,
           {ORDER_COLUMNS['transport_time']} = SYSDATETIME()
       WHERE {ORDER_COLUMNS['order_no']} = ?
   """
   ```
4. 运行语法检查：`python -m py_compile backend/services/order_workflow_service.py`
5. 检查是否还有其他 SQL 存在类似乱码问题（grep 搜索中文字符）

**验证标准**：
- [ ] 语法检查通过
- [ ] 无中文字段名字面量出现在 SQL 语句中

---

## D7 - 预防复发 / Prevention

**短期措施**：
- 在 `.pre-commit-config.yaml` 中添加 G1-2 中文字段名检测规则（详见 `07_ci_gates.md` G1-2）

**长期措施**：
- 考虑引入静态分析工具（如 Ruff）增强检测能力

---

## D8 - 归档复盘 / Documentation

待修复完成后填写。

---

## Required References / 必需参考

| 文件 | 路径 | 用途 |
|------|------|------|
| 问题代码 | `backend/services/order_workflow_service.py` | 修复目标（line 186-234） |
| 字段名常量 | `backend/database/schema/column_names.py` | 获取正确常量 |
| 编码规范 | `.claude/rules/00_core.md` | 字段名使用规范 |
| Bug修复规则 | `.claude/rules/02_debug.md` | 8D流程参考 |
| API规范 | `docs/API_SPEC.md` | 确认 assign-transport API 规范 |

---

## Constraints / 约束条件

1. **禁止破坏现有业务逻辑**：只修复乱码问题，不改变 SQL 语义
2. **必须使用字段名常量**：`ORDER_COLUMNS` 中定义的常量
3. **Zero-Assumption Policy**：先读取 `column_names.py` 确认常量名，不假设

---

## Completion Criteria / 完成标准

- [ ] `assign_transport` 函数中的乱码字符已替换为 `ORDER_COLUMNS` 常量
- [ ] 语法检查通过：`python -m py_compile backend/services/order_workflow_service.py`
- [ ] 全局搜索确认无其他文件中存在类似乱码问题
- [ ] reviewer 评分审核通过（D3/D5/D6 节点）
