from types import SimpleNamespace

from backend.launcher import server_launcher


def test_stop_backend_terminates_tracked_backend_process(monkeypatch) -> None:
    terminated = []
    dummy_process = SimpleNamespace(poll=lambda: None)
    dummy = SimpleNamespace(
        backend_process=dummy_process,
        _expected_stops={"backend": False, "frontend": False},
        status_message="",
    )
    dummy._set_status = lambda message: setattr(dummy, "status_message", message)
    dummy._stop_service = lambda **kwargs: server_launcher.DevServerLauncher._stop_service(dummy, **kwargs)
    dummy._refresh_button_states = lambda backend_running, frontend_running: None
    dummy._check_backend_running = lambda: False
    dummy._is_frontend_process_running = lambda: False

    monkeypatch.setattr(
        server_launcher,
        "terminate_process_tree",
        lambda process: terminated.append(process) or True,
    )

    server_launcher.DevServerLauncher._stop_backend(dummy)

    assert terminated == [dummy_process]
    assert dummy._expected_stops["backend"] is True
    assert dummy.status_message


def test_stop_frontend_terminates_tracked_frontend_process(monkeypatch) -> None:
    terminated = []
    dummy_process = SimpleNamespace(poll=lambda: None)
    dummy = SimpleNamespace(
        frontend_process=dummy_process,
        _expected_stops={"backend": False, "frontend": False},
        status_message="",
    )
    dummy._set_status = lambda message: setattr(dummy, "status_message", message)
    dummy._is_frontend_process_running = lambda: True
    dummy._stop_service = lambda **kwargs: server_launcher.DevServerLauncher._stop_service(dummy, **kwargs)
    dummy._refresh_button_states = lambda backend_running, frontend_running: None
    dummy._check_backend_running = lambda: False

    monkeypatch.setattr(
        server_launcher,
        "terminate_process_tree",
        lambda process: terminated.append(process) or True,
    )

    server_launcher.DevServerLauncher._stop_frontend(dummy)

    assert terminated == [dummy_process]
    assert dummy._expected_stops["frontend"] is True
    assert dummy.status_message


def test_format_process_pid_returns_dash_for_stopped_process() -> None:
    dummy = SimpleNamespace()

    assert server_launcher.DevServerLauncher._format_process_pid(dummy, None, False) == "-"


def test_format_process_pid_returns_pid_for_running_process() -> None:
    dummy = SimpleNamespace()
    process = SimpleNamespace(pid=12345)

    assert server_launcher.DevServerLauncher._format_process_pid(dummy, process, True) == "12345"


def test_format_port_owner_pid_returns_dash_when_not_found(monkeypatch) -> None:
    dummy = SimpleNamespace()

    monkeypatch.setattr(server_launcher, "find_listening_pid_for_port", lambda port: None)

    assert server_launcher.DevServerLauncher._format_port_owner_pid(dummy, 8151) == "-"


def test_format_port_owner_pid_returns_listener_pid(monkeypatch) -> None:
    dummy = SimpleNamespace()

    monkeypatch.setattr(server_launcher, "find_listening_pid_for_port", lambda port: 45678)

    assert server_launcher.DevServerLauncher._format_port_owner_pid(dummy, 8151) == "45678"


def test_format_process_name_returns_dash_when_pid_missing() -> None:
    dummy = SimpleNamespace()

    assert server_launcher.DevServerLauncher._format_process_name(dummy, None) == "-"


def test_format_process_name_returns_process_name(monkeypatch) -> None:
    dummy = SimpleNamespace()

    monkeypatch.setattr(server_launcher, "find_process_name_by_pid", lambda pid: "python.exe")

    assert server_launcher.DevServerLauncher._format_process_name(dummy, 12345) == "python.exe"


def test_format_process_executable_returns_dash_when_pid_missing() -> None:
    dummy = SimpleNamespace()

    assert server_launcher.DevServerLauncher._format_process_executable(dummy, None) == "-"


def test_format_process_executable_returns_path(monkeypatch) -> None:
    dummy = SimpleNamespace()

    monkeypatch.setattr(server_launcher, "find_process_executable_by_pid", lambda pid: "C:\\Python312\\python.exe")

    assert server_launcher.DevServerLauncher._format_process_executable(dummy, 12345) == "C:\\Python312\\python.exe"


def test_copy_label_value_copies_pid_text() -> None:
    clipboard: list[str] = []
    statuses: list[str] = []

    class FakeRoot:
        def clipboard_clear(self):
            clipboard.clear()

        def clipboard_append(self, value):
            clipboard.append(value)

        def update(self):
            return None

    class FakeLabel:
        @staticmethod
        def cget(key):
            assert key == "text"
            return "12345"

    dummy = SimpleNamespace(root=FakeRoot())
    dummy._set_status = lambda message: statuses.append(message)

    server_launcher.DevServerLauncher._copy_label_value(dummy, FakeLabel(), "后端 PID")

    assert clipboard == ["12345"]
    assert statuses[-1] == "已复制 后端 PID: 12345；可在任务管理器“详细信息”页按 PID 列查找"


def test_copy_label_value_handles_empty_pid() -> None:
    statuses: list[str] = []

    class FakeLabel:
        @staticmethod
        def cget(key):
            assert key == "text"
            return "-"

    dummy = SimpleNamespace()
    dummy._set_status = lambda message: statuses.append(message)

    server_launcher.DevServerLauncher._copy_label_value(dummy, FakeLabel(), "后端 PID")

    assert statuses[-1] == "后端 PID 当前无可复制值"


def test_manual_refresh_status_triggers_single_refresh() -> None:
    calls: list[bool] = []
    statuses: list[str] = []
    dummy = SimpleNamespace(instance_dir="E:/logs/dev_server_launcher")
    dummy._set_status = lambda message: statuses.append(message)
    dummy._refresh_status_snapshot = lambda *, refresh_health: calls.append(refresh_health)

    server_launcher.DevServerLauncher._manual_refresh_status(dummy)

    assert calls == [True]
    assert statuses[-1] == "正在手动刷新状态... | 日志目录: E:/logs/dev_server_launcher"


def test_matches_repo_frontend_process_returns_true_for_repo_vite(monkeypatch) -> None:
    dummy = SimpleNamespace()
    command_line = '"D:\\Program Files\\nodejs\\node.exe" E:\\CA001\\Tooling_IO_Management\\frontend\\node_modules\\vite\\bin\\vite.js --host 0.0.0.0 --port 8150 --strictPort'

    monkeypatch.setattr(server_launcher, "find_process_command_line_by_pid", lambda pid: command_line)

    assert server_launcher.DevServerLauncher._matches_repo_frontend_process(dummy, 4300) is True


def test_matches_repo_frontend_process_returns_false_for_unrelated_command(monkeypatch) -> None:
    dummy = SimpleNamespace()

    monkeypatch.setattr(server_launcher, "find_process_command_line_by_pid", lambda pid: '"node.exe" D:\\other\\app.js')

    assert server_launcher.DevServerLauncher._matches_repo_frontend_process(dummy, 4300) is False


def test_stop_frontend_kills_repo_port_owner_when_process_not_tracked(monkeypatch) -> None:
    terminated: list[int] = []
    refreshes: list[bool] = []
    statuses: list[str] = []
    dummy = SimpleNamespace(
        frontend_process=None,
        _expected_stops={"backend": False, "frontend": False},
    )
    dummy._is_frontend_process_running = lambda: False
    dummy._check_backend_running = lambda: False
    dummy._refresh_button_states = lambda backend_running, frontend_running: None
    dummy._schedule_status_refresh = lambda *, refresh_health: refreshes.append(refresh_health)
    dummy._set_status = lambda message: statuses.append(message)
    dummy._matches_repo_frontend_process = lambda pid: True
    dummy._stop_frontend_port_owner_if_safe = lambda: server_launcher.DevServerLauncher._stop_frontend_port_owner_if_safe(dummy)

    monkeypatch.setattr(server_launcher, "find_listening_pid_for_port", lambda port: 4300)
    monkeypatch.setattr(server_launcher, "terminate_pid_tree", lambda pid: terminated.append(pid) or True)

    server_launcher.DevServerLauncher._stop_frontend(dummy)

    assert terminated == [4300]
    assert refreshes == [False]
    assert dummy._expected_stops["frontend"] is True
    assert statuses[-1] == "前端端口占用进程已停止"


def test_stop_frontend_does_not_kill_unrelated_port_owner(monkeypatch) -> None:
    terminated: list[int] = []
    statuses: list[str] = []
    dummy = SimpleNamespace(frontend_process=None)
    dummy._is_frontend_process_running = lambda: False
    dummy._stop_frontend_port_owner_if_safe = lambda: False
    dummy._set_status = lambda message: statuses.append(message)

    monkeypatch.setattr(server_launcher, "terminate_pid_tree", lambda pid: terminated.append(pid) or True)

    server_launcher.DevServerLauncher._stop_frontend(dummy)

    assert terminated == []
    assert statuses[-1] == "前端未运行"
