# -*- coding: utf-8 -*-
"""Process management utilities for dev server launcher."""

from __future__ import annotations

import ctypes
import os
import shutil
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


def is_http_200_line(line: str) -> bool:
    """Check if a log line is a benign HTTP 200 log line."""
    return bool(HTTP_200_LINE_PATTERN.search(line))


# Module-level resolved Python command
PYTHON_CMD = resolve_python()

# GUI event directory for incident monitoring
GUI_EVENT_DIR = BASE_DIR / "incidents" / "gui_events"
