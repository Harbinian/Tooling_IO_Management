# -*- coding: utf-8 -*-
"""
Configuration settings for Tooling IO Management System.
"""

import os
import logging
import secrets
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    def load_dotenv():
        return False

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatabaseSettings:
    server: str
    database: str
    username: str
    password: str
    driver: str
    timeout_seconds: int
    pool_size: int


@dataclass(frozen=True)
class Settings:
    SECRET_KEY: str
    FLASK_HOST: str
    FLASK_PORT: int
    FLASK_DEBUG: bool
    FLASK_THREADED: bool
    FLASK_USE_RELOADER: bool
    FLASK_RELOADER_TYPE: str
    FEISHU_APP_ID: str
    FEISHU_APP_SECRET: str
    FEISHU_APP_TOKEN: str
    FEISHU_WEBHOOK_URL: str
    FEISHU_WEBHOOK_TRANSPORT: str
    FEISHU_WEBHOOK_SUPPLY_TEAM: str
    FEISHU_NOTIFICATION_ENABLED: bool
    FEISHU_NOTIFICATION_TIMEOUT_SECONDS: int
    db: DatabaseSettings

    @property
    def DB_SERVER(self) -> str:
        return self.db.server

    @property
    def DB_DATABASE(self) -> str:
        return self.db.database

    @property
    def DB_USERNAME(self) -> str:
        return self.db.username

    @property
    def DB_PASSWORD(self) -> str:
        return self.db.password

    @property
    def DB_DRIVER(self) -> str:
        return self.db.driver

    @property
    def DB_TIMEOUT(self) -> int:
        return self.db.timeout_seconds

    @property
    def DB_POOL_SIZE(self) -> int:
        return self.db.pool_size


def _get_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() == 'true'


def _resolve_secret_key(flask_env: str) -> str:
    secret_key = os.getenv('SECRET_KEY', '').strip()
    if secret_key:
        return secret_key

    if flask_env == 'production':
        raise ValueError('SECRET_KEY environment variable must be set in production')

    generated_key = secrets.token_urlsafe(32)
    logger.warning('SECRET_KEY not set; generated an ephemeral development key for the current process')
    return generated_key


def _build_settings() -> Settings:
    flask_env = os.getenv('FLASK_ENV', 'default').lower()
    flask_debug = _get_bool('FLASK_DEBUG', flask_env != 'production')
    if flask_env == 'production':
        flask_debug = False
    flask_threaded = _get_bool('FLASK_THREADED', True)
    flask_use_reloader = _get_bool('FLASK_USE_RELOADER', flask_debug)
    flask_reloader_type = os.getenv('FLASK_RELOADER_TYPE', 'stat').strip().lower() or 'stat'
    if flask_reloader_type not in {'stat', 'watchdog', 'auto'}:
        flask_reloader_type = 'stat'

    db = DatabaseSettings(
        server=os.getenv('CESOFT_DB_SERVER', '192.168.19.220,1433'),
        database=os.getenv('CESOFT_DB_DATABASE', 'CXSYSYS'),
        username=os.getenv('CESOFT_DB_USERNAME', 'sa'),
        password=os.getenv('CESOFT_DB_PASSWORD', ''),
        driver=os.getenv('CESOFT_DB_DRIVER', '{SQL Server}'),
        timeout_seconds=int(os.getenv('CESOFT_DB_TIMEOUT', '30')),
        pool_size=int(os.getenv('CESOFT_DB_POOL_SIZE', '5'))
    )

    return Settings(
        SECRET_KEY=_resolve_secret_key(flask_env),
        FLASK_HOST=os.getenv('FLASK_HOST', '0.0.0.0'),
        FLASK_PORT=int(os.getenv('FLASK_PORT', '5000')),
        FLASK_DEBUG=flask_debug,
        FLASK_THREADED=flask_threaded,
        FLASK_USE_RELOADER=flask_use_reloader,
        FLASK_RELOADER_TYPE=flask_reloader_type,
        FEISHU_APP_ID=os.getenv('FEISHU_APP_ID', ''),
        FEISHU_APP_SECRET=os.getenv('FEISHU_APP_SECRET', ''),
        FEISHU_APP_TOKEN=os.getenv('FEISHU_APP_TOKEN', ''),
        FEISHU_WEBHOOK_URL=os.getenv('FEISHU_WEBHOOK_URL', ''),
        FEISHU_WEBHOOK_TRANSPORT=os.getenv('FEISHU_WEBHOOK_TRANSPORT', ''),
        FEISHU_WEBHOOK_SUPPLY_TEAM=os.getenv('FEISHU_WEBHOOK_SUPPLY_TEAM', ''),
        FEISHU_NOTIFICATION_ENABLED=_get_bool('FEISHU_NOTIFICATION_ENABLED', False),
        FEISHU_NOTIFICATION_TIMEOUT_SECONDS=int(os.getenv('FEISHU_NOTIFICATION_TIMEOUT_SECONDS', '10')),
        db=db
    )


settings = _build_settings()
