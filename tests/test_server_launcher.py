from types import SimpleNamespace

from backend.launcher import server_launcher


def test_start_backend_refreshes_status_after_success(monkeypatch) -> None:
    scheduled: list[bool] = []
    watched: list[tuple[object, str, str]] = []
    dummy_process = SimpleNamespace(pid=24680, poll=lambda: None)

    class ImmediateThread:
        def __init__(self, target=None, daemon=None):
            self._target = target

        def start(self):
            if self._target:
                self._target()

    dummy = SimpleNamespace(
        backend_process=None,
        backend_log_path="backend.log",
        frontend_process=None,
        _expected_stops={"backend": False, "frontend": False},
        status_message="",
    )
    dummy._set_status = lambda message: setattr(dummy, "status_message", message)
    dummy._reset_log_file = lambda path: None
    dummy._run_command = lambda *args, **kwargs: dummy_process
    dummy._write_startup_info = lambda service, pid: None
    dummy._refresh_button_states = lambda backend_running, frontend_running: None
    dummy._is_frontend_process_running = lambda: False
    dummy._schedule_status_refresh = lambda *, refresh_health: scheduled.append(refresh_health)
    dummy._watch_startup = lambda process, service_name, log_path: watched.append((process, service_name, log_path))

    monkeypatch.setattr(server_launcher, "PYTHON_CMD", "python")
    monkeypatch.setattr(server_launcher, "BACKEND_SCRIPT", SimpleNamespace(exists=lambda: True))
    monkeypatch.setattr(server_launcher.threading, "Thread", ImmediateThread)

    server_launcher.DevServerLauncher._start_backend(dummy)

    assert scheduled == [False]
    assert watched == [(dummy_process, "后端", "backend.log")]
    assert "后端启动命令已发送" in dummy.status_message


def test_start_frontend_warns_when_port_is_already_in_use(monkeypatch) -> None:
    errors: list[tuple[str, str]] = []
    gui_events: list[dict] = []

    monkeypatch.setattr(
        server_launcher.messagebox,
        "showerror",
        lambda title, message: errors.append((title, message)),
    )

    dummy = SimpleNamespace(
        frontend_process=None,
        status_message="",
        frontend_log_path="frontend.log",
    )
    dummy._is_frontend_process_running = lambda: False
    dummy._is_frontend_port_occupied = lambda: True
    dummy._set_status = lambda message: setattr(dummy, "status_message", message)
    dummy._write_gui_event = lambda payload: gui_events.append(payload)

    server_launcher.DevServerLauncher._start_frontend(dummy)

    assert errors == [
        (
            "启动失败",
            "前端固定端口 8150 已被占用，启动器不会切换端口。\n\n"
            "请先释放该端口后再重试。",
        )
    ]
    assert gui_events == [
        {
            "event_type": "startup_failure",
            "severity": "high",
            "affected_service": "frontend",
            "error_summary": "前端启动失败: 端口 8150 已被占用",
            "error_details": {
                "port": 8150,
                "log_file": "frontend.log",
            },
        }
    ]
    assert dummy.status_message == "前端启动失败: 端口 8150 已被占用"


def test_start_frontend_refreshes_status_after_success(monkeypatch) -> None:
    scheduled: list[bool] = []
    watched: list[tuple[object, str, str]] = []
    dummy_process = SimpleNamespace(pid=13579, poll=lambda: None)

    class ImmediateThread:
        def __init__(self, target=None, daemon=None):
            self._target = target

        def start(self):
            if self._target:
                self._target()

    dummy = SimpleNamespace(
        frontend_process=None,
        frontend_log_path="frontend.log",
        status_message="",
        _expected_stops={"backend": False, "frontend": False},
    )
    dummy._is_frontend_process_running = lambda: False
    dummy._is_frontend_port_occupied = lambda: False
    dummy._set_status = lambda message: setattr(dummy, "status_message", message)
    dummy._reset_log_file = lambda path: None
    dummy._run_command = lambda *args, **kwargs: dummy_process
    dummy._refresh_button_states = lambda backend_running, frontend_running: None
    dummy._check_backend_running = lambda: False
    dummy._schedule_status_refresh = lambda *, refresh_health: scheduled.append(refresh_health)
    dummy._watch_startup = lambda process, service_name, log_path: watched.append((process, service_name, log_path))

    monkeypatch.setattr(server_launcher, "NODE_CMD", "node")
    monkeypatch.setattr(server_launcher, "build_frontend_dev_command", lambda *args, **kwargs: ["node", "vite.js"])
    monkeypatch.setattr(server_launcher, "FRONTEND_DIR", SimpleNamespace(is_dir=lambda: True))
    monkeypatch.setattr(server_launcher.threading, "Thread", ImmediateThread)

    server_launcher.DevServerLauncher._start_frontend(dummy)

    assert scheduled == [False]
    assert watched == [(dummy_process, "前端", "frontend.log")]
    assert "前端启动命令已发送" in dummy.status_message
