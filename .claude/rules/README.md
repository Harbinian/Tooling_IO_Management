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
| `07_ci_gates.md` | CI 自动化门禁规范（替代人工评分/检查） |
| `08_skill_convention.md` | 技能文件约定规范（结构、体积、触发命令） |

---

## 流程选择决策树 / Workflow Decision Tree

收到任务时，按以下顺序判断应使用哪个协议：

```
收到任务
 │
 ├─ 生产环境紧急故障？
 │   └─ YES → 🚑 HOTFIX SOP (03_hotfix.md)
 │
 ├─ 已有功能出现 Bug / 回归问题？
 │   └─ YES → 🐛 8D 协议 (02_debug.md)
 │
 ├─ 新功能 / 重构 / UI 迁移？
 │   └─ YES → 🔄 ADP 四阶段 (01_workflow.md)
 │
 └─ 纯测试任务？
     └─ YES → 🧪 测试规范 (06_testing.md)
```

> ⚠️ 若任务横跨多个类型（如修 Bug 时发现需重构），**以最高优先级流程为主**，
> 子任务拆分为独立编号单独执行。

---

## 技能与规则映射 / Skills & Rules Mapping

以下 Skills 自动化规则执行：

| 规则文件 | 对应技能 |
|----------|----------|
| `01_workflow.md` | `prompt-task-runner` - 四阶段流程执行 |
| `02_debug.md` | `self-healing-dev-loop` - 8D 问题解决 |
| `03_hotfix.md` | `self-healing-dev-loop` - 热修复流程 |
| `04_frontend.md` | 手动执行 / Manual |
| `05_task_convention.md` | `auto-task-generator` - 任务生成与编号 |
| `06_testing.md` | 手动执行 / Manual |
| `07_ci_gates.md` | 手动执行 / Manual（CI 配置由人工维护） |

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

### CI 门禁 (07_ci_gates.md)

```
L1: pre-commit → L2: 静态分析 → L3: 测试覆盖 → L4: 结构检查 → L5: 归档守卫
```
- G1/G2: 替代人工 Code Review
- G3: 替代 tester 测试确认
- G4: 替代 reviewer D3/D5/D6 评分
- G5: 替代人工归档检查
- H1-H5: 保留人工节点（业务语义无法自动化）

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
