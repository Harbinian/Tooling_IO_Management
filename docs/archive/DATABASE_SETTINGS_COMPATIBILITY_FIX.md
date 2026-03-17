# 数据库配置兼容性修复 / Database Settings Compatibility Fix

---

## 问题摘要 / Problem Summary

仓库从 `config/settings.py` 导出了 `settings` 作为扁平配置类，包含以下属性: / The repository exported `settings` from `config/settings.py` as a flat configuration class with attributes such as:

- `DB_SERVER`
- `DB_DATABASE`
- `DB_USERNAME`
- `DB_PASSWORD`
- `DB_DRIVER`

然而，`database.py` 期望嵌套结构: / However, `database.py` expected a nested structure:

- `settings.db.server`
- `settings.db.database`
- `settings.db.username`
- `settings.db.password`
- `settings.db.driver`

由于此不匹配，导入 `database.py` 在 `DatabaseManager` 初始化时引发 `AttributeError`。 / Because of that mismatch, importing `database.py` raised an `AttributeError` during `DatabaseManager` initialization.

## 根本原因 / Root Cause

`database.py` 尝试在 `config.settings` 成功导入时使用统一配置: / `database.py` tried to use unified config when `config.settings` imported successfully:

- `_USE_UNIFIED_CONFIG = True`

但它仅检查模块导入是否成功。 / But it only checked whether the module import worked.

它没有验证 `settings.db` 是否实际存在。 / It did not validate whether `settings.db` actually existed.

因此失败发生在导入时: / So the failure happened at import time:

```python
settings.db.server
```

而实际的 `settings` 对象仅暴露扁平属性。 / while the actual `settings` object only exposed flat attributes.

## 所做的代码更改 / Code Changes Made

### 1. 将 `config/settings.py` 重建为兼容的设置对象 / 1. Rebuilt `config/settings.py` into a compatible settings object

配置模块现在暴露: / The configuration module now exposes:

- 一个具体的 `settings` 对象 / a concrete `settings` object
- 一个嵌套的 `settings.db` 对象用于数据库访问 / a nested `settings.db` object for database access
- 向后兼容的扁平访问器，如 `settings.DB_SERVER` / backward-compatible flat accessors such as `settings.DB_SERVER`

这使两种样式都能工作: / This keeps both styles working:

- `settings.db.server`
- `settings.DB_SERVER`

### 2. 在 `database.py` 中添加防御性配置加载 / 2. Added defensive config loading in `database.py`

`DatabaseManager.__init__()` 现在: / `DatabaseManager.__init__()` now:

- 仅在 `settings.db` 存在时使用统一配置 / uses unified config only when `settings.db` exists
- 当嵌套 db 配置不可用时回退到环境变量 / falls back to environment variables when the nested db config is unavailable
- 保持真实的 SQL Server 运行时错误可见 / keeps real SQL Server runtime errors visible
- 仅防止配置结构不匹配 / only protects against configuration shape mismatch

## 引入的回退逻辑 / Fallback Logic Introduced

当统一配置可用时: / When unified config is available:

- 从 `settings.db` 读取 / read from `settings.db`
- 如果单个键缺失，回退到环境变量值 / if individual keys are missing, fall back to environment values

当统一配置不可用或格式错误时: / When unified config is unavailable or malformed:

- 直接使用 `CESOFT_DB_*` 环境变量 / use `CESOFT_DB_*` environment variables directly

这意味着配置加载不再导致模块导入崩溃。 / This means configuration loading no longer crashes module import.

## 执行的验证 / Validation Performed

- `import database` 成功 / `import database` succeeds
- `import web_server` 成功 / `import web_server` succeeds
- Flask `test_client()` 调用 `/api/tools/search` 成功 / Flask `test_client()` call to `/api/tools/search` succeeds
- `python -m py_compile config\settings.py database.py backend\services\tool_io_service.py web_server.py` 成功 / `python -m py_compile config\settings.py database.py backend\services\tool_io_service.py web_server.py` succeeds

验证了来自真实 SQL Server 后端搜索的 API 响应包含: / Verified API response from real SQL Server-backed search includes:

- `tool_code` / 工装编码
- `tool_name` / 工装名称
- `drawing_no` / 图号
- `spec_model` / 规格型号
- `current_version` / 当前版次
- `current_location_text` / 当前位置文本
- `status_text` / 状态文本

## 限制和假设 / Limitations And Assumptions

- 此修复不重新设计数据库层 / This fix does not redesign the database layer
- SQL Server 仍是主要数据源 / SQL Server remains the primary data source
- 此修复仅解决配置兼容性和导入时健壮性问题 / The fix only addresses configuration compatibility and import-time robustness
- 真实的数据库连接问题仍将正常显现，这是预期行为 / Real database connectivity problems will still surface normally, which is the intended behavior
