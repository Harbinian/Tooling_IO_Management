Primary Executor: Claude Code
Task Type: Refactoring
Priority: P1
Stage: 205
Goal: Fix outdated documentation - correct framework names and state machine definitions
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

docs/ 文件夹下的多个核心文档存在过时信息，需要修正以反映实际的系统架构。

**发现的主要问题：**

1. **PRD.md** (第 274 行)：描述后端使用 "FastAPI"，实际是 **Flask**
2. **ARCHITECTURE.md** (多处)：描述 "FastAPI" 和 "SQLAlchemy"，实际是 **Flask + pyodbc**
3. **PRD.md** (5.2 节)：状态机不完整，缺少 `partially_confirmed`, `transport_notified`, `final_confirmation_pending` 等状态
4. **ARCHITECTURE.md** (3.1 节)：只显示 7 个状态，实际有 **9 个状态**
5. **RBAC_DESIGN.md** (章节 103-114, 129-138)：表名错误 (`users` → `sys_user`, `organizations` → `sys_org`)
6. **DB_SCHEMA.md** (章节 82-90 与 272-281)：自相矛盾的状态描述
7. **PROJECT_DEVELOPMENT_SUMMARY.md** (第 180 行)：使用旧表名 "工装位置表" 应改为 "工装出入库单_位置"

---

## Required References / 必需参考

- `docs/PRD.md` - 产品需求文档（需修正第 274 行和技术栈描述）
- `docs/ARCHITECTURE.md` - 架构文档（需修正技术栈和状态机）
- `docs/RBAC_DESIGN.md` - RBAC 设计文档（需修正表名）
- `docs/DB_SCHEMA.md` - 数据库 Schema（已更新，需确保一致性）
- `docs/API_SPEC.md` - API 规格文档（检查状态定义一致性）
- `web_server.py` - 确认使用 Flask 框架
- `backend/database/schema/schema_manager.py` - 确认实际的表结构
- `backend/services/rbac_service.py` - 确认 RBAC 表名

**实际系统状态定义**（以 DB_SCHEMA.md 和 API_SPEC.md 为准）：

| 状态值 | 中文 | 说明 |
|--------|------|------|
| draft | 草稿 | 订单刚创建 |
| submitted | 已提交 | 已提交给保管员 |
| partially_confirmed | 部分确认 | 部分明细已确认 |
| keeper_confirmed | 保管员已确认 | 保管员已确认 |
| transport_notified | 已通知运输 | 已发送运输通知 |
| transport_in_progress | 运输中 | 运输进行中 |
| final_confirmation_pending | 待最终确认 | 等待最终确认 |
| completed | 已完成 | 订单完成 |
| rejected | 已拒绝 | 订单被拒绝 |
| cancelled | 已取消 | 订单已取消 |

---

## Core Task / 核心任务

修正 docs/ 文件夹下过时文档中的以下问题：

### 1. PRD.md 修正
- 第 274 行附近：将 "FastAPI" 改为 "Flask"
- 5.2 节：补充完整的状态流转规则，包含所有 10 个状态

### 2. ARCHITECTURE.md 修正
- 第 15, 21, 32, 33, 240 行附近：将 "FastAPI" 改为 "Flask"，"SQLAlchemy" 改为 "pyodbc"
- 3.1 节：更新订单状态图和表格，包含所有 10 个状态
- 确保状态定义与 PRD.md, DB_SCHEMA.md, API_SPEC.md 一致

### 3. RBAC_DESIGN.md 修正
- 章节 103-114, 129-138：将 `users` 改为 `sys_user`，将 `organizations` 改为 `sys_org`
- 确保所有表名与实际 RBAC 系统一致

### 4. DB_SCHEMA.md 清理
- 移除或更新第 43, 86-89, 99, 132-133, 243, 259 行的过时 line references（指向 database.py 的行号已不准确）
- 确保章节 82-90 与 272-281 的描述一致（已修复的字段统一标记为 ✅）

### 5. PROJECT_DEVELOPMENT_SUMMARY.md 修正
- 第 180 行：将 "工装位置表" 更新为 "工装出入库单_位置"
- 更新技术栈描述部分

### 6. ARCHITECTURE_INDEX.md 修正
- 第 82 行：移除对不存在的 `TOOL_MASTER_FIELD_MAPPING.md` 的引用

---

## Required Work / 必需工作

### PRD.md
```
1. 搜索 "FastAPI" 出现的位置，全部替换为 "Flask"
2. 在 5.2 节状态流转规则表格中补充：
   - partially_confirmed (部分确认)
   - transport_notified (运输已通知)
   - transport_in_progress (运输中)
   - final_confirmation_pending (待最终确认)
3. 确保状态流转关系正确
```

### ARCHITECTURE.md
```
1. 搜索 "FastAPI" 出现的位置（图表和文字），全部替换为 "Flask"
2. 搜索 "SQLAlchemy" 出现的位置，全部替换为 "pyodbc"
3. 在 3.1 节补充完整的状态定义表格
4. 更新状态流转图
```

### RBAC_DESIGN.md
```
1. 搜索 "users" 表引用，确认并改为 "sys_user"
2. 搜索 "organizations" 表引用，确认并改为 "sys_org"
3. 检查其他可能的旧表名引用
```

### DB_SCHEMA.md
```
1. 在文件开头或适当位置添加注释：
   "注意：本文件中引用的 line numbers 已过时，请参考实际的 backend/database/schema/schema_manager.py"
2. 或者移除不再准确的 line references
3. 统一标记"缺失字段"章节的描述
```

### PROJECT_DEVELOPMENT_SUMMARY.md
```
1. 将 "工装位置表" 替换为 "工装出入库单_位置"
2. 检查并统一技术栈描述
```

### ARCHITECTURE_INDEX.md
```
1. 移除对 docs/TOOL_MASTER_FIELD_MAPPING.md 的引用
2. 或创建该文档（如果确实需要）
```

---

## Constraints / 约束条件

1. **只修改文档**：不修改任何代码文件
2. **保持一致性**：修正后的文档之间、文档与代码之间应保持一致
3. **保留历史痕迹**：使用删除线或注释标记旧信息，不要完全删除
4. **英文优先**：代码、变量名、API 路径使用英文；注释可以使用中英双语
5. **验证修改**：修改后使用 grep 确认没有遗留的 "FastAPI" 或 "SQLAlchemy" 等过时词汇

---

## Completion Criteria / 完成标准

1. **语法检查**：无（纯文档修改）

2. **关键词检查**（使用 grep 验证）：
   ```powershell
   # 确保 PRD.md 中没有 FastAPI
   Select-String -Path "docs/PRD.md" -Pattern "FastAPI"
   # 确保 ARCHITECTURE.md 中没有 FastAPI 和 SQLAlchemy
   Select-String -Path "docs/ARCHITECTURE.md" -Pattern "FastAPI|SQLAlchemy"
   # 确保 RBAC_DESIGN.md 中没有 "表: users" 或 "表: organizations"
   Select-String -Path "docs/RBAC_DESIGN.md" -Pattern "表: users|表: organizations"
   ```

3. **一致性检查**：
   - PRD.md、ARCHITECTURE.md、DB_SCHEMA.md、API_SPEC.md 中的状态定义一致
   - RBAC_DESIGN.md 中的表名与实际一致（sys_user, sys_org 等）

4. **可读性检查**：
   - 修正后的文档仍然易于阅读
   - 没有破坏文档的整体结构
