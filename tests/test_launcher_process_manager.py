import os
from pathlib import Path
import shutil
import socket
import subprocess
import uuid

import pytest

from backend.launcher import process_manager


class DummyProcess:
    def __init__(self, pid: int = 4321, poll_results=None):
        self.pid = pid
        self._poll_results = list(poll_results or [None, None, 0])
        self.terminate_called = False
        self.kill_called = False

    def poll(self):
        if self._poll_results:
            return self._poll_results.pop(0)
        return 0

    def terminate(self):
        self.terminate_called = True

    def kill(self):
        self.kill_called = True

    def wait(self, timeout=None):
        raise subprocess.TimeoutExpired(cmd="dummy", timeout=timeout)


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific process tree handling")
def test_terminate_process_tree_uses_taskkill_for_remaining_children(monkeypatch: pytest.MonkeyPatch) -> None:
    process = DummyProcess()
    captured: dict[str, object] = {}

    class RunResult:
        returncode = 0

    def fake_run(*args, **kwargs):
        captured["args"] = args[0]
        captured["kwargs"] = kwargs
        return RunResult()

    monkeypatch.setattr(process_manager.subprocess, "run", fake_run)

    assert process_manager.terminate_process_tree(process) is True
    assert process.terminate_called is True
    assert captured["args"] == ["taskkill", "/PID", "4321", "/T", "/F"]
    assert captured["kwargs"]["creationflags"] == subprocess.CREATE_NO_WINDOW
    assert captured["kwargs"]["startupinfo"].wShowWindow == subprocess.SW_HIDE


def test_terminate_process_tree_returns_true_for_exited_process() -> None:
    class ExitedProcess:
        pid = 99

        @staticmethod
        def poll():
            return 0

    assert process_manager.terminate_process_tree(ExitedProcess()) is True


def test_build_backend_launch_env_disables_reloader() -> None:
    env = process_manager.build_backend_launch_env(8151)

    assert env["FLASK_HOST"] == "0.0.0.0"
    assert env["FLASK_PORT"] == "8151"
    assert env["FLASK_DEBUG"] == "false"
    assert env["FLASK_USE_RELOADER"] == "false"


def test_is_local_port_accepting_connections_returns_true(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_create_connection(address, timeout):
        assert address == ("127.0.0.1", 8150)
        assert timeout == 0.5
        return DummySocket()

    monkeypatch.setattr(process_manager.socket, "create_connection", fake_create_connection)

    assert process_manager.is_local_port_accepting_connections(8150) is True


def test_is_local_port_accepting_connections_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_create_connection(address, timeout):
        raise socket.error("connection refused")

    monkeypatch.setattr(process_manager.socket, "create_connection", fake_create_connection)

    assert process_manager.is_local_port_accepting_connections(8150) is False


def test_parse_windows_listening_pid_returns_pid_for_matching_port() -> None:
    netstat_output = """
  TCP    0.0.0.0:8150           0.0.0.0:0              LISTENING       23456
  TCP    127.0.0.1:8151         0.0.0.0:0              LISTENING       34567
"""

    assert process_manager.parse_windows_listening_pid(netstat_output, 8151) == 34567


def test_parse_windows_listening_pid_returns_none_when_port_missing() -> None:
    netstat_output = "  TCP    0.0.0.0:9000           0.0.0.0:0              LISTENING       99999"

    assert process_manager.parse_windows_listening_pid(netstat_output, 8151) is None


def test_parse_windows_process_name_returns_image_name_for_pid() -> None:
    tasklist_output = '"python.exe","34567","Console","1","25,000 K"\n"node.exe","45678","Console","1","30,000 K"'

    assert process_manager.parse_windows_process_name(tasklist_output, 45678) == "node.exe"


def test_parse_windows_process_name_returns_none_when_pid_missing() -> None:
    tasklist_output = '"python.exe","34567","Console","1","25,000 K"'

    assert process_manager.parse_windows_process_name(tasklist_output, 99999) is None


def test_parse_process_executable_output_returns_first_non_empty_line() -> None:
    output = "\n\nC:\\Python312\\python.exe\n"

    assert process_manager.parse_process_executable_output(output) == "C:\\Python312\\python.exe"


def test_parse_process_executable_output_returns_none_for_empty_output() -> None:
    assert process_manager.parse_process_executable_output(" \n\t\n") is None


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific pid tree termination")
def test_terminate_pid_tree_uses_taskkill(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class RunResult:
        returncode = 0

    def fake_run(*args, **kwargs):
        captured["args"] = args[0]
        captured["kwargs"] = kwargs
        return RunResult()

    monkeypatch.setattr(process_manager.subprocess, "run", fake_run)

    assert process_manager.terminate_pid_tree(5678) is True
    assert captured["args"] == ["taskkill", "/PID", "5678", "/T", "/F"]


def test_build_frontend_dev_command_uses_node_and_vite_script(monkeypatch: pytest.MonkeyPatch) -> None:
    temp_frontend_dir = Path("logs") / "pytest_tmp" / f"frontend_{uuid.uuid4().hex}"
    vite_bin = temp_frontend_dir / "node_modules" / "vite" / "bin"
    vite_bin.mkdir(parents=True, exist_ok=True)
    (vite_bin / "vite.js").write_text("console.log('vite')", encoding="utf-8")
    monkeypatch.setattr(process_manager, "FRONTEND_DIR", temp_frontend_dir)
    monkeypatch.setattr(process_manager, "NODE_CMD", "C:/node/node.exe")

    try:
        command = process_manager.build_frontend_dev_command(port=8150)
        assert command == [
            "C:/node/node.exe",
            str(vite_bin / "vite.js"),
            "--host",
            "0.0.0.0",
            "--port",
            "8150",
            "--strictPort",
        ]
    finally:
        shutil.rmtree(temp_frontend_dir.parent.parent, ignore_errors=True)
