# 10176_fix_order_routes_transport_permission_comments

## Context

在审查 `backend/routes/order_routes.py` 时发现多处 API 端点的注释与实际 `@require_permission` 装饰器不一致。

**问题详情**：

`order_routes.py` 中有 4 个 API 端点使用了 `@require_permission("order:transport_execute")`，但注释声称需要 `KEEPER` 权限：

| 行号 | API 端点 | 注释声称 | 实际 `@require_permission` | KEEPER 是否有此权限 |
|------|----------|---------|---------------------------|-------------------|
| 213 | `POST /api/tool-io-orders/<order_no>/transport-start` | `# KEEPER` | `order:transport_execute` | **否** |
| 236 | `POST /api/tool-io-orders/<order_no>/transport-complete` | `# KEEPER` | `order:transport_execute` | **否** |
| 259 | `POST /api/tool-io-orders/<order_no>/report-transport-issue` | `# PRODUCTION_PREP/KEEPER` | `order:transport_execute` | **否** |
| 499 | `GET /api/tool-io-orders/pre-transport` | `# PRODUCTION_PREP/KEEPER` | `order:transport_execute` | **否** |

根据 `docs/RBAC_PERMISSION_MATRIX.md`：
- `order:transport_execute` 权限仅分配给 `PRODUCTION_PREP` 和 `SYS_ADMIN`
- `KEEPER` **没有**此权限

这些错误的注释会误导开发者，认为 KEEPER 可以访问这些端点。

---

## Required References

- `backend/routes/order_routes.py` - 需要修正注释的文件
- `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵（权威来源）
- `docs/RBAC_DESIGN.md` - RBAC 设计规范

---

## Core Task

修正 `backend/routes/order_routes.py` 中 4 处误导性注释，使其与实际的 `@require_permission` 装饰器一致。

**修改原则**：
- 只修改注释，不修改代码逻辑
- 注释必须反映实际有权限访问该端点的角色

---

## Required Work

1. **读取** `backend/routes/order_routes.py` 文件
2. **定位**以下 4 处错误的注释（行号可能有偏差，以实际搜索为准）：
   - `transport-start` 端点（约第 213 行）
   - `transport-complete` 端点（约第 236 行）
   - `report-transport-issue` 端点（约第 259 行）
   - `pre-transport` 端点（约第 499 行）
3. **修正注释**，将错误的 `# KEEPER` 或 `# PRODUCTION_PREP/KEEPER` 改为：
   - `# PRODUCTION_PREP, SYS_ADMIN` （对于 transport-start, transport-complete）
   - `# PRODUCTION_PREP, KEEPER, SYS_ADMIN` （对于 report-transport-issue）
   - `# PRODUCTION_PREP, KEEPER, SYS_ADMIN` （对于 pre-transport）
4. **验证**：运行 `python -m py_compile backend/routes/order_routes.py` 确认语法正确

---

## Constraints

- **只修改注释**，不修改任何 `@require_permission` 装饰器
- **不修改**任何业务逻辑代码
- 使用 `grep -n "require_permission.*transport_execute"` 确认端点位置

---

## Completion Criteria

1. 4 处误导性注释已被修正
2. 注释与 `@require_permission` 装饰器一致
3. Python 语法检查通过
4. 不存在因注释修改导致的任何其他文件变更
