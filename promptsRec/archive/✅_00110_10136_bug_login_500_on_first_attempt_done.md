Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 111
Goal: Fix first login attempt returns 500 error due to Werkzeug reloader
Dependencies: None
Execution: RUNPROMPT

---

## Context

**问题描述**：用户第一次登录时报 500 错误，再次点击时正常登录。

**根本原因分析（D4）**：
1. Werkzeug 开发服务器的 `debug=True` 模式启用了文件监控自动重载（watchdog）
2. 当 Werkzeug 检测到文件变化时，会触发服务重启（`Restarting with watchdog`）
3. 服务重启期间（1-2秒），如果客户端发送请求，会返回 500 或连接失败
4. 第一次登录失败后，第二次成功，是因为服务已完成重启

**证据**：
- 日志显示 Werkzeug 多次检测到文件变化并触发重启：
  ```
  * Detected change in '...', reloading
  * Restarting with watchdog (windowsapi)
  ```
- 重启期间收到请求时返回错误

---

## Required References

- `web_server.py` - Flask 应用启动配置
- `config/settings.py` - 配置管理

---

## Core Task

修复 Werkzeug 自动重载导致的首次请求失败问题。

---

## Required Work

1. 修改 `web_server.py` 启动配置：

   **问题代码**：
   ```python
   app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
   ```

   **修复方案**：
   ```python
   # 使用 threaded=True 处理并发请求
   # 使用 use_reloader=False 禁用自动重载，或
   # 配置 reloader_type 为 "stat"（更稳定）
   app.run(
       host=FLASK_HOST,
       port=FLASK_PORT,
       debug=FLASK_DEBUG,
       threaded=True,
       use_reloader=False  # 禁用自动重载避免重启期间500错误
   )
   ```

2. 或者保留自动重载但增加稳定性：
   ```python
   import os
   os.environ['WERKZEUG_RUN_MAIN'] = 'true'
   app.run(
       host=FLASK_HOST,
       port=FLASK_PORT,
       debug=FLASK_DEBUG,
       threaded=True
   )
   ```

3. 如果需要自动重载功能，考虑：
   - 使用 `reloader_type="stat"` 替代默认的 " watchdog"
   - 配置 `extra_files` 指定特定文件而非整个目录

---

## Constraints

- 开发环境下保持代码变更检测能力
- 确保并发请求处理正常
- 不影响生产环境的 WSGI 服务器部署

---

## Completion Criteria

1. 后端语法检查通过：
   ```powershell
   python -m py_compile web_server.py config/settings.py
   ```

2. 功能测试：
   - 重启服务后立即发送登录请求
   - 验证登录请求不再返回 500 错误
   - 多次快速连续登录测试，确认稳定性

3. 确认代码修改后 Werkzeug watchdog 重启不会导致 500 错误
