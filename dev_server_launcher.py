# -*- coding: utf-8 -*-
"""Dev server launcher GUI for Tooling IO Management."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
import ctypes
import atexit
import re
from pathlib import Path
from datetime import datetime

import requests

# --- Tkinter Tcl/Tk runtime initialization (MUST be before tkinter import) ---
# When frozen by PyInstaller, tcl8.6 and tk8.6 are bundled as datas (see spec).
# The bundled files go to _tcl_data and _tk_data (destination names in spec).
# PyInstaller's pyi_rth__tkinter.py runtime hook sets TCL_LIBRARY/TK_LIBRARY
# automatically; no manual configuration needed here.

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Error: tkinter is not available. Please use Python with tkinter support.")
    raise SystemExit(1)


BACKEND_PORT = 8151
FRONTEND_PORT = 8150
ACCESS_HOST = "192.168.19.199"
BACKEND_BASE_URL = f"http://{ACCESS_HOST}:{BACKEND_PORT}"
FRONTEND_BASE_URL = f"http://{ACCESS_HOST}:{FRONTEND_PORT}"
BACKEND_HEALTH_URL = f"{BACKEND_BASE_URL}/api/health"

STARTUP_INFO_FILE = ".devserver.startup"

STATUS_RUNNING = "服务在线"
STATUS_STOPPED = "服务离线"
STATUS_DEGRADED = "数据库异常"

_SINGLE_INSTANCE_MUTEX_NAME = "Global\\ToolingIO_DevServerLauncher_Singleton"
_SINGLE_INSTANCE_MUTEX_HANDLE = None
HTTP_200_LINE_PATTERN = re.compile(r'"\w+\s+[^"]+\s+HTTP/\d(?:\.\d+)?"\s+200\b')


def _get_base_dir() -> Path:
    """Return project root directory.

    When running as a PyInstaller frozen exe, sys.argv[0] may be a relative
    path or just the filename if launched from Explorer. We resolve it against
    the CWD, then walk up to find the directory that contains both the backend
    script and the frontend subdirectory.
    """
    if getattr(sys, "frozen", False):
        argv_path = Path(sys.argv[0])
        # If argv[0] is just a filename with no directory part,
        # resolve() will wrongly treat CWD as the script directory.
        # Use getattr to check if it's an absolute path to avoid this.
        if argv_path.is_absolute():
            exe_dir = argv_path.parent.resolve()
        else:
            # Try resolving against CWD first
            exe_dir = (Path.cwd() / argv_path).parent.resolve()

        # Walk up until we find a directory that has both web_server.py
        # and the frontend subdirectory (the project root)
        candidate = exe_dir
        for _ in range(5):  # max 5 levels up
            if (candidate / "web_server.py").exists() and (candidate / "frontend").is_dir():
                return candidate
            parent = candidate.parent
            if parent == candidate:
                break
            candidate = parent

        # Fallback: if exe is directly in a "dist" folder, go to parent
        if exe_dir.name.lower() == "dist":
            return exe_dir.parent.resolve()
        return exe_dir
    return Path(__file__).parent.resolve()


def _acquire_single_instance_lock() -> bool:
    """Return True if current process is the first launcher instance."""
    global _SINGLE_INSTANCE_MUTEX_HANDLE
    if os.name != "nt":
        return True
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, _SINGLE_INSTANCE_MUTEX_NAME)
    if not mutex:
        return True
    _SINGLE_INSTANCE_MUTEX_HANDLE = mutex
    # ERROR_ALREADY_EXISTS = 183
    return ctypes.windll.kernel32.GetLastError() != 183


def _release_single_instance_lock() -> None:
    global _SINGLE_INSTANCE_MUTEX_HANDLE
    if os.name != "nt" or not _SINGLE_INSTANCE_MUTEX_HANDLE:
        return
    ctypes.windll.kernel32.CloseHandle(_SINGLE_INSTANCE_MUTEX_HANDLE)
    _SINGLE_INSTANCE_MUTEX_HANDLE = None


def _python_candidates() -> list[str]:
    """Return safe python interpreter candidates for launcher subprocesses."""
    candidates: list[str] = [str(BASE_DIR / ".venv" / "Scripts" / "python.exe")]

    # In frozen mode, sys.executable points to this launcher exe.
    # Never treat launcher exe as a python interpreter candidate.
    if not getattr(sys, "frozen", False):
        candidates.append(sys.executable)

    # Fallback to PATH python.
    candidates.append("python")
    return candidates


BASE_DIR = _get_base_dir()
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_SCRIPT = BASE_DIR / "web_server.py"

# Pre-flight validation results (computed once at import time for the GUI)
_VALIDATION_ERRORS: list[str] = []


def _validate_installation() -> list[str]:
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

    # Check Python interpreter works and has requests
    python_candidates = _python_candidates()
    python_ok = False
    for candidate in python_candidates:
        if candidate and _is_python_runnable(candidate):
            # Check if it has requests
            try:
                popen_kwargs = _windows_hidden_process_kwargs()
                result = subprocess.run(
                    [candidate, "-c", "import requests"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                    timeout=5,
                    **popen_kwargs,
                )
                if result.returncode == 0:
                    python_ok = True
                    break
            except Exception:
                pass
    if not python_ok:
        errors.append(
            f"Python interpreter with 'requests' module not found. "
            f"Checked: {python_candidates}. "
            f"Ensure .venv is activated or requests is installed."
        )

    return errors


def _windows_hidden_process_kwargs() -> dict[str, object]:
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


def _is_python_runnable(python_cmd: str) -> bool:
    try:
        popen_kwargs = _windows_hidden_process_kwargs()
        result = subprocess.run(
            [python_cmd, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=3,
            **popen_kwargs,
        )
        return result.returncode == 0
    except Exception:
        return False


def _resolve_python() -> str:
    """Find a Python interpreter that (a) runs and (b) has the requests module."""
    candidates = _python_candidates()
    for candidate in candidates:
        if candidate and _is_python_runnable(candidate):
            # Verify it has requests to avoid WindowsApps Python
            try:
                popen_kwargs = _windows_hidden_process_kwargs()
                result = subprocess.run(
                    [candidate, "-c", "import requests"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                    timeout=5,
                    **popen_kwargs,
                )
                if result.returncode == 0:
                    return candidate
            except Exception:
                pass
    return ""


PYTHON_CMD = _resolve_python()


class DevServerLauncher:
    """Tkinter app for starting/stopping backend and frontend dev services."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tooling IO 开发服务启动器")
        self.root.geometry("980x680")
        self.root.minsize(900, 620)

        self.backend_process: subprocess.Popen | None = None
        self.frontend_process: subprocess.Popen | None = None
        self.start_backend_btn: tk.Button | None = None
        self.start_frontend_btn: tk.Button | None = None
        self.start_all_btn: tk.Button | None = None
        self.stop_backend_btn: tk.Button | None = None
        self.stop_frontend_btn: tk.Button | None = None
        self.stop_all_btn: tk.Button | None = None
        self.instance_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.instance_dir = BASE_DIR / "logs" / "dev_server_launcher" / self.instance_id
        self.instance_dir.mkdir(parents=True, exist_ok=True)
        self.backend_log_path = self.instance_dir / "backend.log"
        self.frontend_log_path = self.instance_dir / "frontend.log"
        self.backend_reachable = False
        self.backend_db_healthy = False
        self._health_check_inflight = False

        self._setup_ui()
        self._update_status_loop()

    def _setup_ui(self) -> None:
        top = tk.Frame(self.root, padx=16, pady=12)
        top.pack(fill="x")

        tk.Label(
            top,
            text="Tooling IO 开发服务启动器",
            font=("Microsoft YaHei UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            top,
            text="统一启动 Flask(8151) 与 Vite(8150)，并实时查看服务状态",
            font=("Microsoft YaHei UI", 10),
            fg="#555555",
        ).pack(anchor="w", pady=(4, 0))

        addr_frame = tk.LabelFrame(self.root, text="服务地址", padx=12, pady=8, font=("Microsoft YaHei UI", 10))
        addr_frame.pack(fill="x", padx=16, pady=(0, 8))

        self._add_address_row(addr_frame, "前端地址", FRONTEND_BASE_URL)
        self._add_address_row(addr_frame, "后端地址", BACKEND_BASE_URL)
        self._add_address_row(addr_frame, "健康检查", BACKEND_HEALTH_URL)
        quick_row = tk.Frame(addr_frame)
        quick_row.pack(fill="x", pady=(6, 0))
        tk.Label(quick_row, text="快捷访问:", width=10, anchor="w", font=("Microsoft YaHei UI", 10)).pack(side="left")
        tk.Button(quick_row, text="打开前端", width=10, command=lambda: self._open_url(FRONTEND_BASE_URL)).pack(side="left", padx=4)
        tk.Button(quick_row, text="打开后端", width=10, command=lambda: self._open_url(BACKEND_BASE_URL)).pack(side="left", padx=4)

        btn_container = tk.Frame(self.root, padx=16, pady=8)
        btn_container.pack(fill="x", pady=(0, 8))

        start_group = tk.LabelFrame(btn_container, text="启动", padx=8, pady=8, font=("Microsoft YaHei UI", 10))
        start_group.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.start_backend_btn = self._build_button(start_group, "启动后端", self._start_backend)
        self.start_backend_btn.pack(side="left", padx=4)
        self.start_frontend_btn = self._build_button(start_group, "启动前端", self._start_frontend)
        self.start_frontend_btn.pack(side="left", padx=4)
        self.start_all_btn = self._build_button(start_group, "启动全部", self._start_all)
        self.start_all_btn.pack(side="left", padx=4)

        stop_group = tk.LabelFrame(btn_container, text="停止", padx=8, pady=8, font=("Microsoft YaHei UI", 10))
        stop_group.pack(side="left", fill="both", expand=True, padx=6)
        self.stop_backend_btn = self._build_button(stop_group, "停止后端", self._stop_backend)
        self.stop_backend_btn.pack(side="left", padx=4)
        self.stop_frontend_btn = self._build_button(stop_group, "停止前端", self._stop_frontend)
        self.stop_frontend_btn.pack(side="left", padx=4)
        self.stop_all_btn = self._build_button(stop_group, "停止全部", self._stop_all)
        self.stop_all_btn.pack(side="left", padx=4)

        restart_group = tk.LabelFrame(btn_container, text="重启 / 日志", padx=8, pady=8, font=("Microsoft YaHei UI", 10))
        restart_group.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self._build_button(restart_group, "重启后端", self._restart_backend).pack(side="left", padx=4)
        self._build_button(restart_group, "重启前端", self._restart_frontend).pack(side="left", padx=4)
        self._build_button(restart_group, "重启全部", self._restart_all).pack(side="left", padx=4)
        self._build_button(restart_group, "打开日志目录", self._open_log_dir).pack(side="left", padx=4)

        status_frame = tk.LabelFrame(self.root, text="运行状态", padx=12, pady=10, font=("Microsoft YaHei UI", 10))
        status_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.backend_status_value = self._build_status_row(status_frame, "后端 Flask")
        self.frontend_status_value = self._build_status_row(status_frame, "前端 Vite")
        self.backend_health_value = self._build_status_row(status_frame, "后端数据库状态")

        self.status_bar = tk.Label(
            self.root,
            text=f"就绪 | 日志目录: {self.instance_dir}",
            bd=1,
            relief="sunken",
            anchor="w",
            font=("Microsoft YaHei UI", 9),
            padx=8,
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _add_address_row(self, parent: tk.Widget, label: str, url: str) -> None:
        row = tk.Frame(parent)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"{label}:", width=10, anchor="w", font=("Microsoft YaHei UI", 10)).pack(side="left")
        tk.Label(row, text=url, anchor="w", fg="#1f6feb", cursor="hand2", font=("Consolas", 10)).pack(side="left")
        tk.Button(row, text="打开", width=8, command=lambda: self._open_url(url)).pack(side="right")

    def _build_status_row(self, parent: tk.Widget, name: str) -> tk.Label:
        row = tk.Frame(parent)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"{name}:", width=12, anchor="w", font=("Microsoft YaHei UI", 10)).pack(side="left")
        value = tk.Label(row, text=STATUS_STOPPED, fg="red", font=("Microsoft YaHei UI", 10, "bold"))
        value.pack(side="left")
        return value

    def _build_button(self, parent: tk.Widget, text: str, cmd) -> tk.Button:
        return tk.Button(parent, text=text, command=cmd, width=10, height=2, font=("Microsoft YaHei UI", 10))

    def _set_button_state(self, btn: tk.Button | None, enabled: bool) -> None:
        if btn is None:
            return
        btn.config(state="normal" if enabled else "disabled")

    def _refresh_button_states(self, backend_running: bool, frontend_running: bool) -> None:
        self._set_button_state(self.start_backend_btn, not backend_running)
        self._set_button_state(self.stop_backend_btn, backend_running)
        self._set_button_state(self.start_frontend_btn, not frontend_running)
        self._set_button_state(self.stop_frontend_btn, frontend_running)
        self._set_button_state(self.start_all_btn, not (backend_running and frontend_running))
        self._set_button_state(self.stop_all_btn, backend_running or frontend_running)

    def _open_url(self, url: str) -> None:
        try:
            webbrowser.open(url)
            self._set_status(f"已打开: {url}")
        except Exception as exc:  # pragma: no cover - UI fallback
            self._set_status(f"打开地址失败: {exc}")

    def _open_log_dir(self) -> None:
        try:
            if os.name == "nt":
                os.startfile(str(self.instance_dir))
            else:
                webbrowser.open(self.instance_dir.as_uri())
            self._set_status(f"已打开日志目录: {self.instance_dir}")
        except Exception as exc:
            self._set_status(f"打开日志目录失败: {exc}")

    def _run_command(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        log_file: Path | None = None,
        drop_http_200: bool = False,
    ) -> subprocess.Popen | None:
        try:
            popen_kwargs = _windows_hidden_process_kwargs()
            merged_env = os.environ.copy()
            if env:
                merged_env.update(env)

            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd) if cwd else None,
                env=merged_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                **popen_kwargs,
            )

            if log_file and proc.stdout is not None:
                self._stream_process_output(proc, log_file, drop_http_200)
            return proc
        except FileNotFoundError as exc:
            err_msg = f"[LAUNCH ERROR] 命令不存在: {cmd[0]!r} — {exc}\n"
            self._append_log(log_file, err_msg)
            self._set_status(f"启动失败: 命令不存在 {cmd[0]!r}")
            return None
        except PermissionError as exc:
            err_msg = f"[LAUNCH ERROR] 权限拒绝: {' '.join(cmd[:3])} — {exc}\n"
            self._append_log(log_file, err_msg)
            self._set_status(f"启动失败: 权限拒绝 — {exc}")
            return None
        except Exception as exc:
            err_msg = f"[LAUNCH ERROR] 启动异常: {' '.join(cmd[:3])} — {exc}\n"
            self._append_log(log_file, err_msg)
            self._set_status(f"启动失败: {exc}")
            return None

    def _append_log(self, log_file: Path | None, msg: str) -> None:
        """Append a message to the log file, creating it if necessary."""
        if log_file is None:
            return
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(msg)
        except Exception:
            pass

    def _stream_process_output(self, process: subprocess.Popen, log_file: Path, drop_http_200: bool) -> None:
        def worker() -> None:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    assert process.stdout is not None
                    for line in process.stdout:
                        if drop_http_200 and self._is_http_200_line(line):
                            continue
                        f.write(line)
            except Exception:
                return

        threading.Thread(target=worker, daemon=True).start()

    def _is_http_200_line(self, line: str) -> bool:
        return bool(HTTP_200_LINE_PATTERN.search(line))

    def _reset_log_file(self, log_file: Path) -> None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "w", encoding="utf-8"):
            pass

    def _start_backend(self) -> None:
        if self.backend_process and self.backend_process.poll() is None:
            messagebox.showwarning("提示", "后端服务已在运行")
            return

        # Pre-flight: verify Python interpreter and script exist
        if not PYTHON_CMD:
            messagebox.showerror("启动失败", f"未找到有效的 Python 解释器（需已安装 requests 模块）。\n\n请确保已运行:\n  cd {BASE_DIR}\n  .venv/Scripts/Activate.ps1\n  pip install requests\n\n或使用项目自带的 .venv: {BASE_DIR / '.venv'}")
            self._set_status("后端启动失败: Python 解释器无效")
            return

        if not BACKEND_SCRIPT.exists():
            messagebox.showerror("启动失败", f"后端脚本不存在:\n{BACKEND_SCRIPT}\n\n请确认从项目根目录运行。")
            self._set_status("后端启动失败: 脚本不存在")
            return

        self._set_status("正在启动后端服务...")

        def do_start() -> None:
            self._write_startup_info("backend", os.getpid())
            log_path = self.backend_log_path
            self._reset_log_file(log_path)
            self.backend_process = self._run_command(
                [PYTHON_CMD, str(BACKEND_SCRIPT)],
                cwd=BASE_DIR,
                env={"FLASK_HOST": "0.0.0.0", "FLASK_PORT": str(BACKEND_PORT)},
                log_file=log_path,
                drop_http_200=True,
            )
            if self.backend_process:
                self._set_status(f"后端启动命令已发送，地址: {BACKEND_BASE_URL}，Python: {PYTHON_CMD}")
                self._watch_startup(self.backend_process, "后端", log_path)
            else:
                self._set_status("后端启动失败")

        threading.Thread(target=do_start, daemon=True).start()

    def _start_frontend(self) -> None:
        if self.frontend_process and self.frontend_process.poll() is None:
            messagebox.showwarning("提示", "前端服务已在运行")
            return

        # Pre-flight: verify frontend directory exists
        if not FRONTEND_DIR.is_dir():
            messagebox.showerror("启动失败", f"前端目录不存在:\n{FRONTEND_DIR}\n\n请确认从项目根目录运行。")
            self._set_status("前端启动失败: 目录不存在")
            return

        npm_cmd = shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
        if npm_cmd == "npm.cmd" and not shutil.which("npm.cmd"):
            # npm.cmd not found at all
            npm_check = shutil.which("npm")
            if not npm_check:
                messagebox.showerror("启动失败", "未找到 npm 命令。\n\n请确保已安装 Node.js: https://nodejs.org/")
                self._set_status("前端启动失败: npm 未安装")
                return

        self._set_status("正在启动前端服务...")

        def do_start() -> None:
            npm_cmd_val = shutil.which("npm.cmd") or shutil.which("npm") or "npm.cmd"
            log_path = self.frontend_log_path
            self._reset_log_file(log_path)
            self.frontend_process = self._run_command(
                [npm_cmd_val, "run", "dev"],
                cwd=FRONTEND_DIR,
                log_file=log_path,
                drop_http_200=True,
            )
            if self.frontend_process:
                self._set_status(f"前端启动命令已发送，地址: {FRONTEND_BASE_URL}")
                self._watch_startup(self.frontend_process, "前端", log_path)
            else:
                self._set_status("前端启动失败")

        threading.Thread(target=do_start, daemon=True).start()

    def _stop_backend(self) -> None:
        if self.backend_process and self.backend_process.poll() is None:
            self.backend_process.terminate()
            self._set_status("后端已停止")
            return
        self._set_status("后端未运行")

    def _stop_frontend(self) -> None:
        if self.frontend_process and self.frontend_process.poll() is None:
            self.frontend_process.terminate()
            self._set_status("前端已停止")
            return
        self._set_status("前端未运行")

    def _stop_all(self) -> None:
        self._stop_backend()
        self.root.after(300, self._stop_frontend)

    def _start_all(self) -> None:
        self._start_backend()
        self.root.after(800, self._start_frontend)

    def _restart_backend(self) -> None:
        self._stop_backend()
        self.root.after(500, self._start_backend)

    def _restart_frontend(self) -> None:
        self._stop_frontend()
        self.root.after(500, self._start_frontend)

    def _restart_all(self) -> None:
        self._stop_all()
        self.root.after(500, self._start_all)

    def _check_backend_running(self) -> bool:
        return bool(self.backend_process and self.backend_process.poll() is None)

    def _check_frontend_running(self) -> bool:
        return bool(self.frontend_process and self.frontend_process.poll() is None)

    def _refresh_backend_health_async(self) -> None:
        if self._health_check_inflight:
            return
        self._health_check_inflight = True

        def worker() -> None:
            reachable = False
            db_healthy = False
            try:
                response = requests.get(BACKEND_HEALTH_URL, timeout=2)
                reachable = True
                db_healthy = response.status_code == 200
                if db_healthy:
                    try:
                        payload = response.json()
                        if isinstance(payload, dict):
                            status = str(payload.get("status", "")).lower()
                            db_healthy = status in {"ok", "healthy"}
                    except ValueError:
                        pass
            except requests.RequestException:
                pass
            finally:
                self.backend_reachable = reachable
                self.backend_db_healthy = db_healthy
                self._health_check_inflight = False

        threading.Thread(target=worker, daemon=True).start()

    def _set_indicator(self, label: tk.Label, status: str) -> None:
        if status == STATUS_RUNNING:
            label.config(text=status, fg="green")
        elif status == STATUS_DEGRADED:
            label.config(text=status, fg="orange")
        else:
            label.config(text=status, fg="red")

    def _update_status_loop(self) -> None:
        backend_running = self._check_backend_running()
        frontend_running = self._check_frontend_running()
        if backend_running:
            self._refresh_backend_health_async()
        else:
            self.backend_reachable = False
            self.backend_db_healthy = False

        self._set_indicator(self.backend_status_value, STATUS_RUNNING if backend_running else STATUS_STOPPED)
        self._set_indicator(self.frontend_status_value, STATUS_RUNNING if frontend_running else STATUS_STOPPED)

        if backend_running and self.backend_db_healthy:
            self._set_indicator(self.backend_health_value, STATUS_RUNNING)
        elif backend_running and self.backend_reachable:
            self._set_indicator(self.backend_health_value, STATUS_DEGRADED)
        elif backend_running:
            self._set_indicator(self.backend_health_value, STATUS_DEGRADED)
        else:
            self._set_indicator(self.backend_health_value, STATUS_STOPPED)

        self._refresh_button_states(backend_running, frontend_running)
        self.root.after(2000, self._update_status_loop)

    def _write_startup_info(self, service: str, pid: int) -> None:
        try:
            with open(BASE_DIR / STARTUP_INFO_FILE, "w", encoding="utf-8") as f:
                f.write(f"{service}:{pid}\n")
        except Exception:
            return

    def _set_status(self, message: str) -> None:
        self.root.after(0, lambda: self.status_bar.config(text=message))

    def _watch_startup(self, process: subprocess.Popen, service_name: str, log_file: Path) -> None:
        def worker() -> None:
            time.sleep(3)
            if process.poll() is not None:
                exit_code = process.returncode
                log_hint = ""
                if log_file.exists():
                    try:
                        with open(log_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        # Append crash indicator to log if empty or missing startup output
                        if not content.strip():
                            self._append_log(
                                log_file,
                                f"[LAUNCH ERROR] {service_name} 进程启动后立即退出 (exit={exit_code})\n"
                                f"  cwd={BASE_DIR}\n"
                                f"  建议: 检查 Python/npm 环境，或直接运行前端/后端查看错误信息\n",
                            )
                            log_hint = f"，错误已写入 {log_file.name}"
                    except Exception:
                        log_hint = f"（日志文件读取失败）"
                self._set_status(
                    f"{service_name}启动后快速退出（exit={exit_code}）{log_hint}"
                    if log_hint
                    else f"{service_name}启动后快速退出（exit={exit_code}），请查看日志: {log_file.name}"
                )

        threading.Thread(target=worker, daemon=True).start()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    if not _acquire_single_instance_lock():
        raise SystemExit(0)
    atexit.register(_release_single_instance_lock)
    errors = _validate_installation()
    if errors:
        print("Launcher preflight warnings:")
        for err in errors:
            print(f" - {err}")
    root = tk.Tk()
    if errors:
        messagebox.showwarning("环境检查", "检测到潜在环境问题：\n\n" + "\n".join(errors))
    app = DevServerLauncher(root)
    app.run()


if __name__ == "__main__":
    main()
