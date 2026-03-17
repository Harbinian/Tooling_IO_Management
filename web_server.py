# -*- coding: utf-8 -*-
"""Web server entrypoint for the Tooling IO Management System."""

from __future__ import annotations

import logging
import os

from flask import Flask

from backend.routes.admin_user_routes import admin_user_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.common import register_request_identity_hook
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.feedback_routes import feedback_bp
from backend.routes.order_routes import order_bp
from backend.routes.org_routes import org_bp
from backend.routes.page_routes import page_bp
from backend.routes.system_routes import system_bp
from backend.routes.tool_routes import tool_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

try:
    from config.settings import settings

    FLASK_HOST = settings.FLASK_HOST
    FLASK_PORT = settings.FLASK_PORT
    FLASK_DEBUG = settings.FLASK_DEBUG
    FLASK_THREADED = settings.FLASK_THREADED
    FLASK_USE_RELOADER = settings.FLASK_USE_RELOADER
    FLASK_RELOADER_TYPE = settings.FLASK_RELOADER_TYPE
    SECRET_KEY = settings.SECRET_KEY
except ImportError:
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    FLASK_THREADED = os.getenv("FLASK_THREADED", "True").lower() == "true"
    FLASK_USE_RELOADER = os.getenv("FLASK_USE_RELOADER", str(FLASK_DEBUG)).lower() == "true"
    FLASK_RELOADER_TYPE = os.getenv("FLASK_RELOADER_TYPE", "stat").strip().lower() or "stat"
    if FLASK_RELOADER_TYPE not in {"stat", "watchdog", "auto"}:
        FLASK_RELOADER_TYPE = "stat"
    SECRET_KEY = os.getenv("SECRET_KEY", "tooling-io-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = SECRET_KEY

register_request_identity_hook(app, logger)
app.register_blueprint(admin_user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(org_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(order_bp)
app.register_blueprint(tool_bp)
app.register_blueprint(page_bp)
app.register_blueprint(system_bp)


if __name__ == "__main__":
    logger.info("starting tooling io management server %s:%s", FLASK_HOST, FLASK_PORT)
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG,
        threaded=FLASK_THREADED,
        use_reloader=FLASK_USE_RELOADER,
        reloader_type=FLASK_RELOADER_TYPE,
    )
