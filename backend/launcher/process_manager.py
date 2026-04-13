# -*- coding: utf-8 -*-
"""Process management utilities for dev server launcher."""

from __future__ import annotations

import ctypes
import csv
import os
import shutil
import socket
import subprocess
import sys
import re
import threading
from pathlib import Path
from typing import Optional

HTTP_200_LINE_PATTERN = re.compile(r'"\w+\s+[^"]+\s+HTTP/\d(?:\.\d+)?"\s+200\b')
REQUIRED_PYTHON_IMPORTS = (
    "requests",
    "flask_limiter",
)


def get_base_dir() -> Path:
    """Return project root directory.

    When running as a PyInstaller frozen exe, sys.argv[0] may be a relative
    path or just the filename if launched from Explorer. We resolve it against
    the CWD, then walk up to find the directory that contains both the backend
    script and the frontend subdirectory.
    """
    from backend.launcher.config import SINGLE_INSTANCE_MUTEX_NAME

    if getattr(sys, "frozen", False):
        argv_path = Path(sys.argv[0])
        if argv_path.is_absolute():
            exe_dir = argv_path.parent.resolve()
        else:
            exe_dir = (Path.cwd() / argv_path).parent.resolve()

        candidate = exe_dir
        for _ in range(5):
            if (candidate / "web_server.py").exists() and (candidate / "frontend").is_dir():
                return candidate
            parent = candidate.parent
            if parent == candidate:
                break
            candidate = parent

        if exe_dir.name.lower() == "dist":
            return exe_dir.parent.resolve()
        return exe_dir
    return Path(__file__).parent.parent.parent.resolve()


BASE_DIR = get_base_dir()
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_SCRIPT = BASE_DIR / "web_server.py"


def acquire_single_instance_lock() -> bool:
    """Return True if current process is the first launcher instance."""
    from backend.launcher.config import SINGLE_INSTANCE_MUTEX_NAME

    if os.name != "nt":
        return True
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, SINGLE_INSTANCE_MUTEX_NAME)
    if not mutex:
        return True
    # ERROR_ALREADY_EXISTS = 183
    return ctypes.windll.kernel32.GetLastError() != 183


def release_single_instance_lock() -> None:
    """Release the single instance lock."""
    from backend.launcher.config import SINGLE_INSTANCE_MUTEX_NAME

    if os.name != "nt":
        return
    # Note: mutex handle is stored in module globals by the caller
    # This function is kept for API compatibility


_MUTEX_HANDLE: Optional[ctypes.windll.HANDLE] = None


def set_mutex_handle(handle: ctypes.windll.HANDLE) -> None:
    """Store the mutex handle for later release."""
    global _MUTEX_HANDLE
    _MUTEX_HANDLE = handle


def release_mutex() -> None:
    """Release the stored mutex handle."""
    global _MUTEX_HANDLE
    if os.name != "nt" or not _MUTEX_HANDLE:
        return
    ctypes.windll.kernel32.CloseHandle(_MUTEX_HANDLE)
    _MUTEX_HANDLE = None


def python_candidates() -> list[str]:
    """Return safe python interpreter candidates for launcher subprocesses."""
    candidates: list[str] = [str(BASE_DIR / ".venv" / "Scripts" / "python.exe")]

    if not getattr(sys, "frozen", False):
        candidates.append(sys.executable)

    candidates.append("python")
    return candidates


def has_required_modules(python_cmd: str) -> bool:
    """Return whether the interpreter can import launcher/backend prerequisites."""
    try:
        result = subprocess.run(
            [python_cmd, "-c", f"import {', '.join(REQUIRED_PYTHON_IMPORTS)}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
            **windows_hidden_process_kwargs(),
        )
        return result.returncode == 0
    except Exception:
        return False


def validate_installation() -> list[str]:
    """Validate that all required files and interpreters exist."""
    errors = []
    backend_script = BASE_DIR / "web_server.py"
    frontend_dir = BASE_DIR / "frontend"
    frontend_package = frontend_dir / "package.json"

    if not backend_script.exists():
        errors.append(f"Backend script not found: {backend_script}")
    if not frontend_dir.is_dir():
        errors.append(f"Frontend directory not found: {frontend_dir}")
    elif not frontend_package.exists():
        errors.append(f"Frontend package.json not found: {frontend_package}")

    py_candidates = python_candidates()
    python_ok = False
    for candidate in py_candidates:
        if candidate and is_python_runnable(candidate):
            if has_required_modules(candidate):
                python_ok = True
                break
    if not python_ok:
        errors.append(
            f"Python interpreter with required modules {list(REQUIRED_PYTHON_IMPORTS)!r} not found. "
            f"Checked: {py_candidates}. "
            f"Ensure .venv is activated and dependencies are installed."
        )

    return errors


def windows_hidden_process_kwargs() -> dict:
    """Force subprocess to run without visible console windows on Windows."""
    if os.name != "nt":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return {
        "creationflags": subprocess.CREATE_NO_WINDOW,
        "startupinfo": startupinfo,
    }


def is_python_runnable(python_cmd: str) -> bool:
    try:
        result = subprocess.run(
            [python_cmd, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=3,
            **windows_hidden_process_kwargs(),
        )
        return result.returncode == 0
    except Exception:
        return False


def resolve_python() -> str:
    """Find a Python interpreter that can run backend/launcher prerequisites."""
    candidates = python_candidates()
    for candidate in candidates:
        if candidate and is_python_runnable(candidate):
            if has_required_modules(candidate):
                return candidate
    return ""


def resolve_node() -> str:
    """Find a usable Node.js executable for the frontend dev server."""
    return shutil.which("node.exe") or shutil.which("node") or ""


def build_backend_launch_env(port: int) -> dict[str, str]:
    """Build a launcher-safe backend environment.

    The GUI launcher should hold the real Flask server process instead of a
    Werkzeug reloader parent/child pair, otherwise stopping the tracked process
    can still leave the child listener alive on the port.
    """
    return {
        "FLASK_HOST": "0.0.0.0",
        "FLASK_PORT": str(port),
        "FLASK_DEBUG": "false",
        "FLASK_USE_RELOADER": "false",
    }


def is_local_port_accepting_connections(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Return whether a local TCP port is already accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _extract_port_from_endpoint(endpoint: str) -> str | None:
    """Extract the trailing TCP port from a netstat/lsof endpoint token."""
    token = endpoint.strip()
    if not token:
        return None
    if token.startswith("[") and "]:" in token:
        return token.rsplit("]:", 1)[-1]
    if ":" not in token:
        return None
    return token.rsplit(":", 1)[-1]


def parse_windows_listening_pid(netstat_output: str, port: int) -> int | None:
    """Parse `netstat -ano -p tcp` output and return the listening PID for a port."""
    port_text = str(port)
    for raw_line in netstat_output.splitlines():
        parts = raw_line.split()
        if len(parts) < 5:
            continue
        protocol, local_address, _, state, pid = parts[:5]
        if protocol.upper() != "TCP" or state.upper() != "LISTENING":
            continue
        if _extract_port_from_endpoint(local_address) != port_text:
            continue
        if pid.isdigit():
            return int(pid)
    return None


def parse_windows_process_name(tasklist_output: str, pid: int) -> str | None:
    """Parse `tasklist /FO CSV /NH` output and return the process name for a PID."""
    for row in csv.reader(tasklist_output.splitlines()):
        if len(row) < 2:
            continue
        image_name, row_pid = row[0].strip(), row[1].strip()
        if row_pid.isdigit() and int(row_pid) == pid:
            return image_name or None
    return None


def parse_process_executable_output(command_output: str) -> str | None:
    """Return the first non-empty executable path line from command output."""
    for line in command_output.splitlines():
        value = line.strip()
        if value:
            return value
    return None


def find_listening_pid_for_port(port: int) -> int | None:
    """Return the PID currently listening on the given TCP port, if detectable."""
    if port <= 0:
        return None
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["netstat", "-ano", "-p", "tcp"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=3,
                **windows_hidden_process_kwargs(),
            )
            return parse_windows_listening_pid(result.stdout, port)

        result = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=3,
        )
        for line in result.stdout.splitlines():
            token = line.strip()
            if token.isdigit():
                return int(token)
    except Exception:
        return None
    return None


def find_process_name_by_pid(pid: int) -> str | None:
    """Return the process name for a PID, if detectable."""
    if pid <= 0:
        return None
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=3,
                **windows_hidden_process_kwargs(),
            )
            return parse_windows_process_name(result.stdout, pid)

        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "comm="],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=3,
        )
        name = result.stdout.strip()
        return name or None
    except Exception:
        return None


def find_process_executable_by_pid(pid: int) -> str | None:
    """Return the executable path for a PID, if detectable."""
    if pid <= 0:
        return None
    try:
        if os.name == "nt":
            powershell = shutil.which("powershell.exe") or "powershell.exe"
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-Command",
                    f"(Get-CimInstance Win32_Process -Filter \"ProcessId = {pid}\").ExecutablePath",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=4,
                **windows_hidden_process_kwargs(),
            )
            return parse_process_executable_output(result.stdout)

        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=4,
        )
        return parse_process_executable_output(result.stdout)
    except Exception:
        return None


def find_process_command_line_by_pid(pid: int) -> str | None:
    """Return the full command line for a PID, if detectable."""
    if pid <= 0:
        return None
    try:
        if os.name == "nt":
            powershell = shutil.which("powershell.exe") or "powershell.exe"
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-Command",
                    f"(Get-CimInstance Win32_Process -Filter \"ProcessId = {pid}\").CommandLine",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=4,
                **windows_hidden_process_kwargs(),
            )
            return parse_process_executable_output(result.stdout)

        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=4,
        )
        return parse_process_executable_output(result.stdout)
    except Exception:
        return None


def terminate_pid_tree(pid: int, *, grace_seconds: float = 1.5) -> bool:
    """Terminate a process tree by PID."""
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=max(3, int(grace_seconds) + 2),
                **windows_hidden_process_kwargs(),
            )
            return result.returncode == 0
        except Exception:
            return False
    try:
        os.kill(pid, 15)
        return True
    except Exception:
        return False


def build_frontend_dev_command(node_cmd: str | None = None, port: int | None = None) -> list[str]:
    """Build the frontend dev-server command without the npm wrapper process."""
    from backend.launcher.config import FRONTEND_PORT

    resolved_node = node_cmd or NODE_CMD
    vite_bin = FRONTEND_DIR / "node_modules" / "vite" / "bin" / "vite.js"
    resolved_port = port or FRONTEND_PORT
    if not resolved_node or not vite_bin.exists():
        return []
    return [
        resolved_node,
        str(vite_bin),
        "--host",
        "0.0.0.0",
        "--port",
        str(resolved_port),
        "--strictPort",
    ]


def is_http_200_line(line: str) -> bool:
    """Check if a log line is a benign HTTP 200 log line."""
    return bool(HTTP_200_LINE_PATTERN.search(line))


# Module-level resolved Python command
PYTHON_CMD = resolve_python()
NODE_CMD = resolve_node()

# GUI event directory for incident monitoring
GUI_EVENT_DIR = BASE_DIR / "incidents" / "gui_events"


def terminate_process_tree(process: subprocess.Popen | None, *, grace_seconds: float = 1.5) -> bool:
    """Terminate a process and its child processes."""
    if process is None:
        return True
    if process.poll() is not None:
        return True
    force_kill_succeeded = False

    try:
        process.terminate()
    except Exception:
        pass

    try:
        process.wait(timeout=grace_seconds)
        return True
    except Exception:
        pass

    if os.name == "nt":
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=max(3, int(grace_seconds) + 2),
                **windows_hidden_process_kwargs(),
            )
            force_kill_succeeded = result.returncode == 0
        except Exception:
            pass
    else:
        try:
            process.kill()
            force_kill_succeeded = True
        except Exception:
            pass

    try:
        process.wait(timeout=2)
    except Exception:
        pass
    return process.poll() is not None or force_kill_succeeded
