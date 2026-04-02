# Rules 文件夹索引 / Rules Index

本目录包含工装出入库管理系统的开发规则。

---

## 文件结构 / File Structure

| 文件 | 用途 |
|------|------|
| `README.md` | 本索引文件 |
| `00_core.md` | 核心开发规则（编码、字段名常量、命名、Git、数据库表范围等） |
| `01_workflow.md` | ADP 四阶段开发流程（PRD → Data → Architecture → Execution） |
| `02_debug.md` | 8D 问题解决协议（调试/回归问题） |
| `03_hotfix.md` | 热修复 SOP |
| `04_frontend.md` | 前端开发规范（页面、搜索、主题、RBAC） |
| `05_task_convention.md` | 提示词任务编号约定 + 归档前置条件 |
| `06_testing.md` | 测试任务规范（30101-39999） |

---

## 技能与规则映射 / Skills & Rules Mapping

以下 Skills 自动化规则执行：

| 规则文件 | 对应技能 |
|----------|----------|
| `01_workflow.md` | `prompt-task-runner` - 四阶段流程执行 |
| `02_debug.md` | `self-healing-dev-loop` - 8D 问题解决 |
| `03_hotfix.md` | `self-healing-dev-loop` - 热修复流程 |
| `05_task_convention.md` | `auto-task-generator` - 任务生成与编号 |

---

## 快速参考 / Quick Reference

### 核心规则 (00_core.md)

- UTF-8 编码
- 字段名常量使用 (`column_names.py`)
- 外部系统表只读
- 代码完整性（禁止占位符）
- 文档权威性

### 开发流程 (01_workflow.md)

```
Phase 1: PRD → Phase 2: Data → Phase 3: Architecture → Phase 4: Execution
```

### 调试/热修复 (02_debug.md / 03_hotfix.md)

- 8D: D1-D8 问题解决
- 热修复: 识别 → RFC → 分步执行 → 回滚预案 → 归档

### 任务编号 (05_task_convention.md)

- 功能: `00001-09999`
- Bug修复: `10101-19999`
- 重构: `20101-29999`
- 测试: `30101-39999`

---

## 文档权威性

代码实现必须遵循 `docs/` 目录下的权威文档：

- `PRD.md` - 产品需求
- `ARCHITECTURE.md` - 架构
- `API_SPEC.md` - API 规范
- `DB_SCHEMA.md` - 数据库 Schema
- `RBAC_PERMISSION_MATRIX.md` - 权限矩阵
