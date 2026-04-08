---
name: 00096_feature_add_global_error_handler_cors
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/01_workflow.md
  - .claude/rules/00_core.md
version: 1.0.0
---

# 00096: 功能开发 - 添加全局错误处理与 CORS 支持

## Header / 头部信息

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00096
Goal: 为 Flask 后端添加全局错误处理中间件和 CORS 支持
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

架构评审发现接入层存在以下缺失：

1. **无全局错误处理**：所有路由需单独 try/catch，代码重复
2. **CORS 未配置**：跨域请求会被阻止
3. **限流粒度粗糙**：所有端点共享同一限流配置

**业务价值**：
- 减少路由层代码重复
- 支持前端跨域开发
- 提高系统健壮性

**独立性说明**：本任务可独立执行，不依赖 10203/20115。

---

## Phase 1 - PRD / 业务需求分析

**业务背景**：
- 当前每个路由都有相同的错误处理模式
- 前端 Vite 开发服务器 (localhost:8150) 调用后端 (localhost:8151) 存在跨域问题

**目标用户**：
- 后端开发者（减少重复代码）
- 前端开发者（跨域调用）
- 运维（统一的错误日志）

**核心功能**：
1. 全局 `@app.errorhandler` 捕获所有未处理异常
2. 统一错误响应格式
3. flask-cors 配置允许前端域名

**成功标准**：
- 路由层无需重复 try/catch
- 前端能正常跨域调用 API

---

## Phase 2 - Data / 数据流转审视

**现有代码分析**：

| 文件 | 当前错误处理 | 问题 |
|------|-------------|------|
| `web_server.py` | 无全局处理 | 每个路由单独 try/catch |
| `backend/routes/*.py` | 重复模式 | `except Exception as exc: return jsonify({"success": False, "error": str(exc)}), 500` |

**影响范围**：
- 所有 Blueprint 注册的路由
- 所有 HTTP 方法 (GET/POST/PUT/DELETE)

---

## Phase 3 - Architecture / 架构设计

### 方案设计

**全局错误处理**：
```python
@app.errorhandler(Exception)
def handle_exception(e):
    # 记录日志
    app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    # 返回统一格式
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "code": "INTERNAL_ERROR"
    }), 500
```

**CORS 配置**：
```python
from flask_cors import CORS

# 开发环境：允许所有来源
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 生产环境：在 settings.py 中配置具体域名
# CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})
```

### 环境区分策略
| 环境 | origins | 配置来源 |
|------|---------|---------|
| 开发 | `*` | 硬编码 |
| 生产 | 来自 `config/settings.py` | 配置文件 |

### 风险识别
- 全局错误处理可能吞掉预期内的业务异常 → 保留自定义异常特殊处理
- CORS 开放可能导致安全风险 → 生产环境必须配置具体域名

---

## Phase 4 - Execution / 精确执行

### 执行步骤

**Step 1**: 添加依赖
```
- 确认 requirements.txt 包含 flask-cors
- 如未包含，添加 flask-cors==5.0.0（精确版本）
```

**Step 2**: 修改 web_server.py
```
- 导入 flask_cors
- 注册 CORS(app)
- 添加全局错误处理函数
- 保留自定义异常（如 AuthenticationRequiredError）特殊处理
```

**Step 3**: 验证
```
- 语法检查：python -m py_compile web_server.py
- 跨域测试：curl -X OPTIONS -H "Origin: http://localhost:8150" http://localhost:8151/api/tool-io-orders
- 错误处理测试：触发一个故意抛出的异常，确认全局处理
```

**Step 4**: 文档同步
```
- 更新 docs/ARCHITECTURE.md（接入层架构变更）
- 更新 docs/API_SPEC.md（如有响应格式变更）
```

---

## Required References / 必需参考

| 文件 | 路径 | 用途 |
|------|------|------|
| 接入层 | `web_server.py` | 修改目标 |
| 路由示例 | `backend/routes/order_routes.py` | 了解当前错误模式 |
| 现有依赖 | `requirements.txt` | 检查 flask-cors 是否存在 |
| 配置 | `config/settings.py` | CORS 生产域名配置位置 |
| 错误码规范 | `backend/services/tool_io_service.py` | 了解现有异常类型 |

---

## Constraints / 约束条件

1. **不修改业务逻辑**：只添加基础设施，不改变现有函数行为
2. **向后兼容**：现有路由的错误处理仍正常工作
3. **CORS 安全**：开发环境允许 `*`，生产环境必须使用具体域名
4. **UTF-8 编码**：所有文件 UTF-8 无 BOM

---

## Completion Criteria / 完成标准

- [ ] `flask-cors` 已添加到 requirements.txt
- [ ] `web_server.py` 包含 `@app.errorhandler(Exception)`
- [ ] CORS 已配置（开发环境 `*`，生产环境读取配置）
- [ ] 自定义异常（如 `AuthenticationRequiredError`）被正确处理
- [ ] 语法检查通过
- [ ] 跨域请求测试通过
- [ ] docs/ARCHITECTURE.md 已更新
- [ ] tester E2E 验证通过（API 调用流程）
