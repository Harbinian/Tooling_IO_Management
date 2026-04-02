# MPL 模块 RBAC 权限重构

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00078
Goal: 重构 MPL 模块权限，实现最小权限原则
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
当前 MPL（工装可拆卸件清单）模块使用 `tool:view` 权限控制所有操作，导致所有能访问 `tool:view` 的角色（TEAM_LEADER, KEEPER, PLANNER, PRODUCTION_PREP, SYS_ADMIN）都能编写MPL。这违反了"只有工程技术部人员可以编写MPL"的业务要求。

### 目标用户
- 工程技术部人员：需要编写和管理 MPL
- 保管员：在确认申请时需要查看 MPL
- 其他角色：不能访问 MPL 管理功能

### 核心痛点
权限设计违反最小权限原则，MPL 编写权限没有正确隔离。

### 业务目标
1. 新增 `mpl:view` 和 `mpl:write` 专用权限
2. 新增 `engineering` 角色（工程技术部）
3. 限制 MPL 管理页面仅 engineering 和 sys_admin 可访问
4. keeper 通过 `order:keeper_confirm` 间接获得 MPL 查看能力

---

## Required References / 必需参考

- RBAC 设计规范: `docs/RBAC_DESIGN.md`
- RBAC 权限矩阵: `docs/RBAC_PERMISSION_MATRIX.md`
- RBAC 初始化数据: `docs/RBAC_INIT_DATA.md`
- MPL 路由: `backend/routes/mpl_routes.py`
- 前端路由: `frontend/src/router/index.js`
- 规则文件: `.claude/rules/00_core.md`, `.claude/rules/01_workflow.md`

---

## Core Task / 核心任务

按照 ADP 四阶段开发协议，实现 MPL 模块的 RBAC 权限重构：

### Phase 1: PRD - 业务需求分析
- 确认工程技术部角色是否已存在
- 确认 keeper 确认申请时的 MPL 查看调用链路

### Phase 2: Data - 数据审视
- 检查 `sys_permission` 和 `sys_role` 表结构
- 确认 RBAC_INIT_DATA.md 中的 SQL 语句

### Phase 3: Architecture - 架构设计
- 设计 `mpl:view` 和 `mpl:write` 权限
- 设计 engineering 角色的权限和数据范围
- 确认 keeper 间接访问 MPL 的实现方式

### Phase 4: Execution - 精确实施
1. 更新 RBAC_INIT_DATA.md（新增权限和角色定义）
2. 更新 RBAC_PERMISSION_MATRIX.md（同步权限矩阵）
3. 修改 backend/routes/mpl_routes.py（API权限注解）
4. 修改 frontend/src/router/index.js（前端路由守卫）
5. 执行语法检查
6. E2E 验证

---

## Required Work / 必需工作

### 1. 数据库初始化 (RBAC_INIT_DATA.md)
- [ ] 新增 `mpl:view` 权限定义
- [ ] 新增 `mpl:write` 权限定义
- [ ] 新增 `engineering` 角色（role_code: engineering, role_name: 工程技术部）
- [ ] engineering 角色分配: `mpl:view`, `mpl:write`
- [ ] engineering 角色的数据范围分配: ORG

### 2. API层 (backend/routes/mpl_routes.py)
| 端点 | 方法 | 新权限 |
|------|------|--------|
| `/api/mpl` | GET | `mpl:view` |
| `/api/mpl` | POST | `mpl:write` |
| `/api/mpl/<mpl_no>` | GET | `mpl:view` |
| `/api/mpl/<mpl_no>` | PUT | `mpl:write` |
| `/api/mpl/<mpl_no>` | DELETE | `mpl:write` |
| `/api/mpl/by-tool` | GET | `mpl:view` |

### 3. 前端路由 (frontend/src/router/index.js)
- [ ] `/mpl` 路由 meta.permission 改为 `mpl:write`
- [ ] 添加 engineering 角色检查到路由守卫
- [ ] 确保 keeper 角色不能访问 `/mpl` 页面

### 4. RBAC_PERMISSION_MATRIX.md
- [ ] 添加 mpl:view, mpl:write 权限定义到权限清单
- [ ] 添加 engineering 角色到角色-权限矩阵
- [ ] 更新工装路由 API 权限映射

### 5. 特殊处理: keeper 间接访问
- [ ] 确认 `tool_io_service.py` 中 keeper_confirm 调用 `/api/mpl/by-tool` 的逻辑
- [ ] 确保 keeper 通过 `order:keeper_confirm` 权限能间接调用 MPL 查看

---

## Constraints / 约束条件

1. **最小权限原则**: 用户仅获得其职责所需的权限
2. **文档权威性**: 代码不得偏离 `docs/RBAC_PERMISSION_MATRIX.md` 和 `docs/RBAC_INIT_DATA.md`
3. **零退化**: 不得破坏现有 UI 规范、核心业务逻辑
4. **编码规范**: 使用英文变量名，4空格缩进，UTF-8编码
5. **事务处理**: 关键操作必须使用数据库事务
6. **编码规范**: 使用 `column_names.py` 中的常量访问中文字段名

---

## Completion Criteria / 完成标准

### 功能验收
- [ ] engineering 角色可以正常访问 `/mpl` 页面（创建、编辑、删除MPL）
- [ ] sys_admin 角色可以正常访问 `/mpl` 页面
- [ ] keeper 角色访问 `/mpl` 页面时跳转到登录页（带 denied 参数）
- [ ] team_leader 角色访问 `/mpl` 页面时跳转到登录页（带 denied 参数）
- [ ] planner 角色访问 `/mpl` 页面时跳转到登录页（带 denied 参数）
- [ ] production_prep 角色访问 `/mpl` 页面时跳转到登录页（带 denied 参数）

### API 权限验收
- [ ] POST/PUT/DELETE `/api/mpl` 需要 `mpl:write` 权限
- [ ] GET `/api/mpl` 和 `/api/mpl/by-tool` 需要 `mpl:view` 权限
- [ ] keeper 通过 `order:keeper_confirm` 间接调用 `/api/mpl/by-tool` 正常工作

### 文档验收
- [ ] RBAC_INIT_DATA.md 包含新的权限和角色定义
- [ ] RBAC_PERMISSION_MATRIX.md 同步更新
- [ ] 语法检查通过: `python -m py_compile backend/routes/mpl_routes.py`

### E2E 验证
- [ ] tester 执行完整 E2E 验证通过
