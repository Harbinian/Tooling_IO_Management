# -*- coding: utf-8 -*-
"""Dev server launcher GUI for Tooling IO Management."""

from __future__ import annotations

import atexit
import json
import os
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from backend.launcher.config import (
    BACKEND_BASE_URL,
    BACKEND_HEALTH_URL,
    BACKEND_PORT,
    FRONTEND_BASE_URL,
    FRONTEND_PORT,
    STARTUP_INFO_FILE,
    STATUS_DEGRADED,
    STATUS_RUNNING,
    STATUS_STOPPED,
)
from backend.launcher.process_manager import (
    BASE_DIR,
    FRONTEND_DIR,
    BACKEND_SCRIPT,
    GUI_EVENT_DIR,
    PYTHON_CMD,
    NODE_CMD,
    acquire_single_instance_lock,
    build_backend_launch_env,
    build_frontend_dev_command,
    find_process_executable_by_pid,
    find_process_command_line_by_pid,
    find_listening_pid_for_port,
    find_process_name_by_pid,
    is_http_200_line,
    is_local_port_accepting_connections,
    release_mutex,
    set_mutex_handle,
    terminate_pid_tree,
    terminate_process_tree,
    windows_hidden_process_kwargs,
)

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Error: tkinter is not available. Please use Python with tkinter support.")
    raise SystemExit(1)


def _get_base_dir() -> Path:
    """Return project root directory."""
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


class DevServerLauncher:
    """Tkinter app for starting/stopping backend and frontend services."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tooling IO 开发服务启动器")
        self.root.geometry("1120x760")
        self.root.minsize(1040, 720)

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
        self._last_backend_health_error: str | None = None
        self._backend_was_running = False
        self._frontend_was_running = False
        self._expected_stops: dict[str, bool] = {
            "backend": False,
            "frontend": False,
        }

        self._setup_ui()
        self._refresh_button_states(False, False)

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
            text="统一启动 Flask(8151) 与 Vite(8150)",
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
        self._build_button(restart_group, "手动刷新", self._manual_refresh_status).pack(side="left", padx=4)
        self._build_button(restart_group, "打开日志目录", self._open_log_dir).pack(side="left", padx=4)

        status_frame = tk.LabelFrame(self.root, text="运行状态", padx=12, pady=10, font=("Microsoft YaHei UI", 10))
        status_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.backend_status_value = self._build_status_row(status_frame, "后端 Flask")
        self.frontend_status_value = self._build_status_row(status_frame, "前端 Vite")
        self.backend_pid_value = self._build_status_row(status_frame, "后端 PID", default_text="-", text_color="#333333")
        self.frontend_pid_value = self._build_status_row(status_frame, "前端 PID", default_text="-", text_color="#333333")
        self.backend_port_pid_value = self._build_status_row(status_frame, "后端端口占用 PID", default_text="-", text_color="#805d00")
        self.frontend_port_pid_value = self._build_status_row(status_frame, "前端端口占用 PID", default_text="-", text_color="#805d00")
        self.backend_port_name_value = self._build_status_row(status_frame, "后端占用进程名", default_text="-", text_color="#805d00")
        self.frontend_port_name_value = self._build_status_row(status_frame, "前端占用进程名", default_text="-", text_color="#805d00")
        self.backend_port_path_value = self._build_status_row(status_frame, "后端占用路径", default_text="-", text_color="#805d00")
        self.frontend_port_path_value = self._build_status_row(status_frame, "前端占用路径", default_text="-", text_color="#805d00")
        self.backend_health_value = self._build_status_row(status_frame, "后端数据库状态")
        self._make_value_copyable(self.backend_pid_value, "后端 PID")
        self._make_value_copyable(self.frontend_pid_value, "前端 PID")
        self._make_value_copyable(self.backend_port_pid_value, "后端端口占用 PID")
        self._make_value_copyable(self.frontend_port_pid_value, "前端端口占用 PID")
        self._make_value_copyable(self.backend_port_name_value, "后端占用进程名")
        self._make_value_copyable(self.frontend_port_name_value, "前端占用进程名")
        self._make_value_copyable(self.backend_port_path_value, "后端占用路径")
        self._make_value_copyable(self.frontend_port_path_value, "前端占用路径")

        self.status_bar = tk.Label(
            self.root,
            text=f"就绪 | 手动刷新模式 | 日志目录: {self.instance_dir}",
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

    def _build_status_row(
        self,
        parent: tk.Widget,
        name: str,
        default_text: str = STATUS_STOPPED,
        text_color: str = "red",
    ) -> tk.Label:
        row = tk.Frame(parent)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"{name}:", width=12, anchor="w", font=("Microsoft YaHei UI", 10)).pack(side="left")
        value = tk.Label(row, text=default_text, fg=text_color, font=("Microsoft YaHei UI", 10, "bold"))
        value.pack(side="left")
        return value

    def _build_button(self, parent: tk.Widget, text: str, cmd) -> tk.Button:
        return tk.Button(parent, text=text, command=cmd, width=10, height=2, font=("Microsoft YaHei UI", 10))

    def _make_value_copyable(self, label: tk.Label, field_name: str) -> None:
        label.config(cursor="hand2", fg="#1f6feb")
        label.bind("<Button-1>", lambda _event: self._copy_label_value(label, field_name))

    def _copy_label_value(self, label: tk.Label, field_name: str) -> None:
        value = str(label.cget("text")).strip()
        if not value or value == "-":
            self._set_status(f"{field_name} 当前无可复制值")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            self.root.update()
            self._set_status(f"已复制 {field_name}: {value}；可在任务管理器“详细信息”页按 PID 列查找")
        except Exception as exc:
            self._set_status(f"复制 {field_name} 失败: {exc}")

    def _set_button_state(self, btn: tk.Button | None, enabled: bool) -> None:
        if btn is None:
            return
        btn.config(state="normal" if enabled else "disabled")

    def _schedule_status_refresh(self, *, refresh_health: bool) -> None:
        self.root.after(0, lambda: self._refresh_status_snapshot(refresh_health=refresh_health))

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
        except Exception as exc:
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
            popen_kwargs = windows_hidden_process_kwargs()
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
                        if drop_http_200 and is_http_200_line(line):
                            continue
                        f.write(line)
            except Exception:
                return

        threading.Thread(target=worker, daemon=True).start()

    def _reset_log_file(self, log_file: Path) -> None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "w", encoding="utf-8"):
            pass

    def _read_log_tail(self, log_file: Path, max_lines: int = 50) -> str:
        if not log_file.exists():
            return ""
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                return "".join(f.readlines()[-max_lines:])
        except Exception:
            return ""

    def _write_gui_event(self, event_data: dict) -> None:
        def worker() -> None:
            try:
                GUI_EVENT_DIR.mkdir(parents=True, exist_ok=True)
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M%S_%f")
                event_type = str(event_data.get("event_type", "unknown"))
                event_id = f"GUI_EVENT_{timestamp}_{event_type}"
                event_file = GUI_EVENT_DIR / f"{event_id}.json"
                event = {
                    "event_id": event_id,
                    "timestamp": now.isoformat(),
                    "source": "dev_server_launcher",
                    "session_id": self.instance_id,
                    **event_data,
                }
                with open(event_file, "w", encoding="utf-8") as f:
                    json.dump(event, f, ensure_ascii=False, indent=2)
            except Exception:
                return

        threading.Thread(target=worker, daemon=True).start()

    def _start_backend(self) -> None:
        if self.backend_process and self.backend_process.poll() is None:
            messagebox.showwarning("提示", "后端服务已在运行")
            return

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
            self._expected_stops["backend"] = False
            log_path = self.backend_log_path
            self._reset_log_file(log_path)
            self.backend_process = self._run_command(
                [PYTHON_CMD, str(BACKEND_SCRIPT)],
                cwd=BASE_DIR,
                env=build_backend_launch_env(BACKEND_PORT),
                log_file=log_path,
                drop_http_200=True,
            )
            if self.backend_process:
                self._write_startup_info("backend", self.backend_process.pid)
                self._refresh_button_states(True, self._is_frontend_process_running())
                self._schedule_status_refresh(refresh_health=False)
                self._set_status(f"后端启动命令已发送，地址: {BACKEND_BASE_URL}，Python: {PYTHON_CMD}")
                self._watch_startup(self.backend_process, "后端", log_path)
            else:
                self._set_status("后端启动失败")

        threading.Thread(target=do_start, daemon=True).start()

    def _start_frontend(self) -> None:
        if self._is_frontend_process_running():
            messagebox.showwarning("提示", "前端服务已在运行")
            return

        if not FRONTEND_DIR.is_dir():
            messagebox.showerror("启动失败", f"前端目录不存在:\n{FRONTEND_DIR}\n\n请确认从项目根目录运行。")
            self._set_status("前端启动失败: 目录不存在")
            return

        if self._is_frontend_port_occupied():
            self._write_gui_event(
                {
                    "event_type": "startup_failure",
                    "severity": "high",
                    "affected_service": "frontend",
                    "error_summary": f"前端启动失败: 端口 {FRONTEND_PORT} 已被占用",
                    "error_details": {
                        "port": FRONTEND_PORT,
                        "log_file": str(self.frontend_log_path),
                    },
                }
            )
            messagebox.showerror(
                "启动失败",
                f"前端固定端口 {FRONTEND_PORT} 已被占用，启动器不会切换端口。\n\n"
                "请先释放该端口后再重试。",
            )
            self._set_status(f"前端启动失败: 端口 {FRONTEND_PORT} 已被占用")
            return

        frontend_command = build_frontend_dev_command(NODE_CMD, FRONTEND_PORT)
        if not NODE_CMD:
            messagebox.showerror("启动失败", "未找到 Node.js 可执行文件。\n\n请确保已安装 Node.js: https://nodejs.org/")
            self._set_status("前端启动失败: Node.js 未安装")
            return
        if not frontend_command:
            messagebox.showerror("启动失败", f"未找到 Vite 启动脚本。\n\n请先安装前端依赖:\n  cd {FRONTEND_DIR}\n  npm install")
            self._set_status("前端启动失败: Vite 脚本不存在")
            return

        self._set_status("正在启动前端服务...")

        def do_start() -> None:
            self._expected_stops["frontend"] = False
            log_path = self.frontend_log_path
            self._reset_log_file(log_path)
            self.frontend_process = self._run_command(
                frontend_command,
                cwd=FRONTEND_DIR,
                log_file=log_path,
                drop_http_200=True,
            )
            if self.frontend_process:
                self._refresh_button_states(self._check_backend_running(), True)
                self._schedule_status_refresh(refresh_health=False)
                self._set_status(f"前端启动命令已发送，地址: {FRONTEND_BASE_URL}")
                self._watch_startup(self.frontend_process, "前端", log_path)
            else:
                self._set_status("前端启动失败")

        threading.Thread(target=do_start, daemon=True).start()

    def _stop_service(
        self,
        *,
        service_key: str,
        process: subprocess.Popen | None,
        is_running: bool,
        stopped_message: str,
        idle_message: str,
    ) -> None:
        if is_running and process is not None:
            self._expected_stops[service_key] = True
            terminate_process_tree(process)
            self._refresh_button_states(self._check_backend_running(), self._is_frontend_process_running())
            self._set_status(stopped_message)
            return
        self._set_status(idle_message)

    def _stop_backend(self) -> None:
        self._stop_service(
            service_key="backend",
            process=self.backend_process,
            is_running=bool(self.backend_process and self.backend_process.poll() is None),
            stopped_message="后端已停止",
            idle_message="后端未运行",
        )

    def _stop_frontend(self) -> None:
        if self._is_frontend_process_running():
            self._stop_service(
                service_key="frontend",
                process=self.frontend_process,
                is_running=True,
                stopped_message="前端已停止",
                idle_message="前端未运行",
            )
            return

        if self._stop_frontend_port_owner_if_safe():
            self._expected_stops["frontend"] = True
            self._refresh_button_states(self._check_backend_running(), False)
            self._schedule_status_refresh(refresh_health=False)
            self._set_status("前端端口占用进程已停止")
            return

        self._set_status("前端未运行")

    def _format_process_pid(self, process: subprocess.Popen | None, is_running: bool) -> str:
        if not is_running or process is None:
            return "-"
        return str(process.pid)

    def _format_port_owner_pid(self, port: int) -> str:
        owner_pid = find_listening_pid_for_port(port)
        if owner_pid is None:
            return "-"
        return str(owner_pid)

    def _format_process_name(self, pid: int | None) -> str:
        if pid is None:
            return "-"
        process_name = find_process_name_by_pid(pid)
        if not process_name:
            return "-"
        return process_name

    def _format_process_executable(self, pid: int | None) -> str:
        if pid is None:
            return "-"
        executable = find_process_executable_by_pid(pid)
        if not executable:
            return "-"
        return executable

    def _matches_repo_frontend_process(self, pid: int | None) -> bool:
        if pid is None or pid <= 0:
            return False
        command_line = find_process_command_line_by_pid(pid)
        if not command_line:
            return False
        normalized = command_line.replace("/", "\\").lower()
        frontend_root = str(FRONTEND_DIR).replace("/", "\\").lower()
        vite_script = str(FRONTEND_DIR / "node_modules" / "vite" / "bin" / "vite.js").replace("/", "\\").lower()
        return frontend_root in normalized and vite_script in normalized

    def _stop_frontend_port_owner_if_safe(self) -> bool:
        owner_pid = find_listening_pid_for_port(FRONTEND_PORT)
        if not self._matches_repo_frontend_process(owner_pid):
            return False
        return terminate_pid_tree(owner_pid)

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
        return self._is_frontend_process_running()

    def _is_frontend_process_running(self) -> bool:
        return bool(self.frontend_process and self.frontend_process.poll() is None)

    def _is_frontend_port_occupied(self) -> bool:
        return is_local_port_accepting_connections(FRONTEND_PORT)

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
                self._last_backend_health_error = None
            except requests.RequestException as exc:
                error_message = str(exc)
                if self._last_backend_health_error != error_message:
                    self._write_gui_event(
                        {
                            "event_type": "health_check_failed",
                            "severity": "high",
                            "affected_service": "backend",
                            "error_summary": f"后端健康检查失败: {error_message}",
                            "error_details": {
                                "exception": error_message,
                                "health_check_url": BACKEND_HEALTH_URL,
                            },
                        }
                    )
                    self._last_backend_health_error = error_message
            finally:
                self.backend_reachable = reachable
                self.backend_db_healthy = db_healthy
                self._health_check_inflight = False
                self.root.after(0, lambda: self._refresh_status_snapshot(refresh_health=False))

        threading.Thread(target=worker, daemon=True).start()

    def _set_indicator(self, label: tk.Label, status: str) -> None:
        if status == STATUS_RUNNING:
            label.config(text=status, fg="green")
        elif status == STATUS_DEGRADED:
            label.config(text=status, fg="orange")
        else:
            label.config(text=status, fg="red")

    def _refresh_status_snapshot(self, *, refresh_health: bool) -> None:
        backend_running = self._check_backend_running()
        frontend_running = self._is_frontend_process_running()
        backend_port_owner_pid = find_listening_pid_for_port(BACKEND_PORT)
        frontend_port_owner_pid = find_listening_pid_for_port(FRONTEND_PORT)
        if backend_running and refresh_health:
            self._refresh_backend_health_async()
        else:
            if not backend_running:
                self.backend_reachable = False
                self.backend_db_healthy = False

        self._set_indicator(self.backend_status_value, STATUS_RUNNING if backend_running else STATUS_STOPPED)
        self._set_indicator(self.frontend_status_value, STATUS_RUNNING if frontend_running else STATUS_STOPPED)
        self.backend_pid_value.config(text=self._format_process_pid(self.backend_process, backend_running))
        self.frontend_pid_value.config(text=self._format_process_pid(self.frontend_process, frontend_running))
        self.backend_port_pid_value.config(text="-" if backend_port_owner_pid is None else str(backend_port_owner_pid))
        self.frontend_port_pid_value.config(text="-" if frontend_port_owner_pid is None else str(frontend_port_owner_pid))
        self.backend_port_name_value.config(text=self._format_process_name(backend_port_owner_pid))
        self.frontend_port_name_value.config(text=self._format_process_name(frontend_port_owner_pid))
        self.backend_port_path_value.config(text=self._format_process_executable(backend_port_owner_pid))
        self.frontend_port_path_value.config(text=self._format_process_executable(frontend_port_owner_pid))

        if backend_running and self.backend_db_healthy:
            self._set_indicator(self.backend_health_value, STATUS_RUNNING)
        elif backend_running and self.backend_reachable:
            self._set_indicator(self.backend_health_value, STATUS_DEGRADED)
        elif backend_running:
            self._set_indicator(self.backend_health_value, STATUS_DEGRADED)
        else:
            self._set_indicator(self.backend_health_value, STATUS_STOPPED)

        if self._backend_was_running and not backend_running:
            if self._expected_stops["backend"]:
                self._expected_stops["backend"] = False
            else:
                exit_code = self.backend_process.returncode if self.backend_process else None
                self._write_gui_event(
                    {
                        "event_type": "process_crash",
                        "severity": "critical",
                        "affected_service": "backend",
                        "error_summary": f"后端进程运行中退出 (exit={exit_code})",
                        "error_details": {
                            "exit_code": exit_code,
                            "log_file": str(self.backend_log_path),
                            "log_content": self._read_log_tail(self.backend_log_path),
                        },
                    }
                )
        if self._frontend_was_running and not frontend_running:
            if self._expected_stops["frontend"]:
                self._expected_stops["frontend"] = False
            else:
                exit_code = self.frontend_process.returncode if self.frontend_process else None
                self._write_gui_event(
                    {
                        "event_type": "process_crash",
                        "severity": "critical",
                        "affected_service": "frontend",
                        "error_summary": f"前端进程运行中退出 (exit={exit_code})",
                        "error_details": {
                            "exit_code": exit_code,
                            "log_file": str(self.frontend_log_path),
                            "log_content": self._read_log_tail(self.frontend_log_path),
                        },
                    }
                )
        self._backend_was_running = backend_running
        self._frontend_was_running = frontend_running

        self._refresh_button_states(backend_running, frontend_running)

    def _manual_refresh_status(self) -> None:
        self._set_status(f"正在手动刷新状态... | 日志目录: {self.instance_dir}")
        self._refresh_status_snapshot(refresh_health=True)

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
                log_content = self._read_log_tail(log_file)
                if log_file.exists():
                    try:
                        with open(log_file, "r", encoding="utf-8") as f:
                            content = f.read()
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
                self._write_gui_event(
                    {
                        "event_type": "startup_failure",
                        "severity": "critical",
                        "affected_service": service_name,
                        "error_summary": f"{service_name} 进程启动后立即退出 (exit={exit_code})",
                        "error_details": {
                            "exit_code": exit_code,
                            "log_file": str(log_file),
                            "log_content": log_content,
                        },
                    }
                )
                self._set_status(
                    f"{service_name}启动后快速退出（exit={exit_code}）{log_hint}"
                    if log_hint
                    else f"{service_name}启动后快速退出（exit={exit_code}），请查看日志: {log_file.name}"
                )

        threading.Thread(target=worker, daemon=True).start()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    if not acquire_single_instance_lock():
        raise SystemExit(0)
    atexit.register(release_mutex)
    from backend.launcher.process_manager import validate_installation
    errors = validate_installation()
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
