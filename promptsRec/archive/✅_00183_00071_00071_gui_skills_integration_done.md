Primary Executor: Codex
Task Type: Feature Development
Priority: P2
Stage: 00071
Goal: 实现 GUI Launcher 与 Skills 的事件联动 - dev_server_launcher.py 修改
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

目前 `dev_server_launcher.py` 能实时检测前后端错误（进程崩溃、健康检查失败），但 Skills 系统（incident-monitor、incident-capture、self-healing-dev-loop）无法感知这些错误，需要手动触发。

目标：GUI 检测到错误时，自动通过事件文件触发 Skills 的事件捕获流程。

---

## Required References / 必需参考

- `dev_server_launcher.py` - GUI 启动器主文件
- `start-dev.ps1` - 启动脚本
- `.claude/rules/01_workflow.md` - ADP 开发协议

---

## Core Task / 核心任务

修改 `dev_server_launcher.py`，在以下三个检测点写入事件文件到 `incidents/gui_events/` 目录：

### 1. 新增 `_write_gui_event()` 方法

在 `DevServerLauncher` 类中新增方法：

```python
def _write_gui_event(self, event_data: dict) -> None:
    """Write GUI event to incidents/gui_events/ for Skills to pick up."""
    import json
    from datetime import datetime

    event_dir = BASE_DIR / "incidents" / "gui_events"
    event_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_id = f"GUI_EVENT_{timestamp}_{event_data['event_type']}"
    event_file = event_dir / f"{event_id}.json"

    event = {
        "event_id": event_id,
        "timestamp": datetime.now().isoformat(),
        "source": "dev_server_launcher",
        "session_id": self.instance_id,
        **event_data
    }

    try:
        with open(event_file, "w", encoding="utf-8") as f:
            json.dump(event, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # Non-blocking
```

### 2. 修改 `_watch_startup()` worker (line 649-676)

在检测到进程启动失败后，调用 `_write_gui_event()`：

```python
def worker() -> None:
    time.sleep(3)
    if process.poll() is not None:
        exit_code = process.returncode
        log_content = ""
        if log_file.exists():
            try:
                lines = open(log_file, encoding="utf-8").readlines()
                log_content = "".join(lines[-50:])
            except Exception:
                pass
        self._write_gui_event({
            "event_type": "startup_failure",
            "severity": "critical",
            "affected_service": service_name,
            "error_summary": f"{service_name} 进程启动后立即退出 (exit={exit_code})",
            "error_details": {
                "exit_code": exit_code,
                "log_file": str(log_file),
                "log_content": log_content
            }
        })
```

### 3. 修改 `_refresh_backend_health_async()` worker (line 578-605)

在健康检查失败时，调用 `_write_gui_event()`。在 `except requests.RequestException` 块中添加：

```python
except requests.RequestException as e:
    self._write_gui_event({
        "event_type": "health_check_failed",
        "severity": "high",
        "affected_service": "backend",
        "error_summary": f"后端健康检查失败: {str(e)}",
        "error_details": {
            "exception": str(e),
            "health_check_url": BACKEND_HEALTH_URL
        }
    })
```

### 4. 新增进程运行中崩溃检测

在 `_update_status_loop()` 方法中，新增进程崩溃检测逻辑。检测到进程之前在运行，现在不在了，则写入事件。

---

## Required Work / 必需工作

1. 在 `DevServerLauncher` 类中添加 `_write_gui_event()` 方法
2. 修改 `_watch_startup()` 中的 worker，在进程启动失败时写入事件
3. 修改 `_refresh_backend_health_async()` 中的 worker，在健康检查失败时写入事件
4. 在 `_update_status_loop()` 中添加进程运行中崩溃检测
5. 确保事件目录 `incidents/gui_events/` 存在（使用 `mkdir(parents=True, exist_ok=True)`）
6. 所有文件操作使用 `encoding="utf-8"`
7. 事件写入必须使用 try-except 保护，确保不会抛出异常

---

## Constraints / 约束条件

- 不能阻塞主线程，所有事件写入在 daemon 线程中执行
- 不能修改现有检测逻辑，只能在其基础上添加事件写入
- 必须使用 `encoding="utf-8"` 读写文件
- 事件 JSON 必须包含完整字段，不能省略

---

## Completion Criteria / 完成标准

1. `dev_server_launcher.py` 语法正确，能通过 `python -m py_compile dev_server_launcher.py` 检查
2. 三个检测点都能正确写入事件文件到 `incidents/gui_events/`
3. 事件文件格式符合规范，包含所有必需字段
4. 目录不存在时能自动创建
5. 事件写入失败不会影响 GUI 正常运行
