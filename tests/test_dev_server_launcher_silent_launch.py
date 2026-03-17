import os
import subprocess

import pytest

import dev_server_launcher as launcher


@pytest.mark.skipif(os.name != "nt", reason="Windows-only process window flags")
def test_windows_hidden_process_kwargs_are_set() -> None:
    kwargs = launcher._windows_hidden_process_kwargs()

    assert kwargs["creationflags"] == subprocess.CREATE_NO_WINDOW
    startupinfo = kwargs["startupinfo"]
    assert startupinfo.dwFlags & subprocess.STARTF_USESHOWWINDOW
    assert startupinfo.wShowWindow == subprocess.SW_HIDE


@pytest.mark.skipif(os.name != "nt", reason="Windows-only process window flags")
def test_is_python_runnable_uses_hidden_process_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class Result:
        returncode = 0

    def fake_run(*args, **kwargs):
        captured.update(kwargs)
        return Result()

    monkeypatch.setattr(launcher.subprocess, "run", fake_run)

    assert launcher._is_python_runnable("python") is True
    assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW
    assert captured["startupinfo"].wShowWindow == subprocess.SW_HIDE


@pytest.mark.skipif(os.name != "nt", reason="Windows-only process window flags")
def test_run_command_uses_hidden_process_kwargs(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class DummyProc:
        stdout = None

        def poll(self):
            return None

    def fake_popen(*args, **kwargs):
        captured.update(kwargs)
        return DummyProc()

    monkeypatch.setattr(launcher.subprocess, "Popen", fake_popen)

    class DummyLauncher:
        def _set_status(self, message: str) -> None:
            self.message = message

        def _append_log(self, log_file, msg: str) -> None:
            pass

    dummy = DummyLauncher()
    proc = launcher.DevServerLauncher._run_command(
        dummy,
        ["python", "--version"],
        cwd=tmp_path,
        env={"UNIT_TEST_FLAG": "1"},
        log_file=tmp_path / "launcher.log",
    )

    assert proc is not None
    assert captured["creationflags"] == subprocess.CREATE_NO_WINDOW
    assert captured["startupinfo"].wShowWindow == subprocess.SW_HIDE
