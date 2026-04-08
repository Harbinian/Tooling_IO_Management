# -*- coding: utf-8 -*-
"""Configuration constants for dev server launcher."""

from __future__ import annotations

# Server ports
BACKEND_PORT = 8151
FRONTEND_PORT = 8150
ACCESS_HOST = "192.168.19.199"

# Base URLs
BACKEND_BASE_URL = f"http://{ACCESS_HOST}:{BACKEND_PORT}"
FRONTEND_BASE_URL = f"http://{ACCESS_HOST}:{FRONTEND_PORT}"
BACKEND_HEALTH_URL = f"{BACKEND_BASE_URL}/api/health"

# Startup info
STARTUP_INFO_FILE = ".devserver.startup"

# Status messages
STATUS_RUNNING = "服务在线"
STATUS_STOPPED = "服务离线"
STATUS_DEGRADED = "数据库异常"

# Singleton mutex
SINGLE_INSTANCE_MUTEX_NAME = "Global\\ToolingIO_DevServerLauncher_Singleton"
