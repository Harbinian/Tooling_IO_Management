---
name: 20116_refactor_unify_response_format
executor: Codex
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/01_workflow.md
  - .claude/rules/00_core.md
version: 1.0.0
---

# 20116: 重构 - 统一 API 响应格式

## Header / 头部信息

Primary Executor: Codex
Task Type: Refactoring
Priority: P1
Stage: 20116
Goal: 统一所有 API 路由的响应格式，消除 {success, data} 与直接返回数据的混用
Dependencies: "00096 (全局错误处理与CORS)"
Execution: RUNPROMPT

---

## Context / 上下文

架构评审发现路由层响应格式不统一：

**问题类型 A**：
```json
{"success": true, "data": {...}}
```

**问题类型 B**：
```json
{...}  // 直接返回业务数据
```

这种混用导致前端 API 封装层难以统一处理。

---

## Phase 1 - PRD / 业务需求分析

**业务背景**：
- 前端 `frontend/src/api/` 封装了统一的 unwrap 逻辑
- 后端响应格式不一致导致前端处理复杂

**目标**：
- 所有成功响应：`{"success": true, "data": <result>}`
- 所有错误响应：`{"success": false, "error": <error_message>}`

**成功标准**：
- 100% 路由使用统一格式
- 前端 API 封装可简化

---

## Phase 2 - Data / 数据流转审视

**需要检查的路由文件**：

| 文件 | 当前格式 |
|------|----------|
| `backend/routes/order_routes.py` | 混用 |
| `backend/routes/tool_routes.py` | 混用 |
| `backend/routes/mpl_routes.py` | 混用 |
| `backend/routes/system_config_routes.py` | 混用 |
| `backend/routes/auth_routes.py` | 混用 |

**统一后的目标格式**：

成功：
```json
{
    "success": true,
    "data": <result>
}
```

错误：
```json
{
    "success": false,
    "error": {
        "code": "ORDER_NOT_FOUND",
        "message": "订单不存在"
    }
}
```

---

## Phase 3 - Architecture / 架构设计

### 实现方案

**方案：在 web_server.py 或独立模块定义响应辅助函数**

```python
# backend/utils/response.py
from flask import jsonify

def success_response(data, code=200):
    return jsonify({
        "success": True,
        "data": data
    }), code

def error_response(code, message, http_code=400):
    return jsonify({
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }), http_code
```

**重构策略**：
1. 创建 `backend/utils/response.py` 统一响应模块
2. 逐步迁移各路由文件
3. 保留原有 HTTP 状态码语义

### 风险识别
- 大量文件需要修改
- 需要确保不改变业务逻辑

---

## Phase 4 - Execution / 精确执行

### 执行步骤

**Step 1**: 创建响应工具模块
```
- 创建 backend/utils/response.py
- 定义 success_response / error_response 函数
- 语法检查
```

**Step 2**: 迁移 order_routes.py
```
- 替换所有 return jsonify({...}) 为 success_response
- 替换所有错误返回为 error_response
- 语法检查
```

**Step 3**: 迁移其他路由文件
```
- tool_routes.py
- mpl_routes.py
- system_config_routes.py
- auth_routes.py
- admin_user_routes.py
- org_routes.py
- feedback_routes.py
- dashboard_routes.py
```

**Step 4**: 验证
```
- 语法检查所有路由文件
- 运行 api_e2e.py 确认功能正常
```

---

## Required References / 必需参考

| 文件 | 路径 | 用途 |
|------|------|------|
| 路由 | `backend/routes/order_routes.py` | 主要修改目标 |
| 响应封装 | `frontend/src/api/client.js` | 了解前端期望格式 |
| API规范 | `docs/API_SPEC.md` | 确认响应格式规范 |
| 错误码 | `backend/services/tool_io_service.py` | 参考现有错误码 |

---

## Constraints / 约束条件

1. **不改变业务逻辑**：只修改响应格式
2. **向后兼容**：前端 unwrap 仍能正常工作
3. **HTTP 状态码不变**：保持语义（如 404 表示资源不存在）
4. **UTF-8 编码**：所有文件 UTF-8 无 BOM

---

## Phase 4 - Execution / 精确执行

### 执行步骤

**Step 1**: 创建响应工具模块
```
- 创建 backend/utils/response.py
- 定义 success_response / error_response 函数
- 语法检查
```

**Step 2**: 迁移 order_routes.py
```
- 替换所有 return jsonify({...}) 为 success_response
- 替换所有错误返回为 error_response
- 语法检查
```

**Step 3**: 迁移其他路由文件
```
- tool_routes.py
- mpl_routes.py
- system_config_routes.py
- auth_routes.py
- admin_user_routes.py
- org_routes.py
- feedback_routes.py
- dashboard_routes.py
```

**Step 4**: 验证
```
- 语法检查所有路由文件
- 运行 api_e2e.py 确认功能正常
```

**Step 5**: 文档同步
```
- 更新 docs/API_SPEC.md（统一响应格式规范）
- 更新 docs/ARCHITECTURE.md（如有架构变更说明）
```

---

## Required References / 必需参考

| 文件 | 路径 | 用途 |
|------|------|------|
| 路由 | `backend/routes/order_routes.py` | 主要修改目标 |
| 响应封装 | `frontend/src/api/client.js` | 了解前端期望格式 |
| API规范 | `docs/API_SPEC.md` | 确认响应格式规范 |
| 错误码 | `backend/services/tool_io_service.py` | 参考现有错误码 |

---

## Constraints / 约束条件

1. **不改变业务逻辑**：只修改响应格式
2. **向后兼容**：前端 unwrap 仍能正常工作
3. **HTTP 状态码不变**：保持语义（如 404 表示资源不存在）
4. **UTF-8 编码**：所有文件 UTF-8 无 BOM

---

## Completion Criteria / 完成标准

- [ ] `backend/utils/response.py` 已创建
- [ ] 所有路由文件使用统一响应格式
- [ ] 语法检查通过
- [ ] api_e2e.py 测试通过
- [ ] docs/API_SPEC.md 已更新
- [ ] docs/ARCHITECTURE.md 已更新（如需要）
- [ ] tester E2E 验证通过
