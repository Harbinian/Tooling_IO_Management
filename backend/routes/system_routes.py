# -*- coding: utf-8 -*-
"""Health and system routes."""

import logging

from flask import Blueprint, jsonify

from backend.routes.common import require_permission, get_authenticated_user

system_bp = Blueprint("system_routes", __name__)
logger = logging.getLogger(__name__)


@system_bp.route("/api/health")
def api_health():
    """Basic health check - database connectivity only."""
    try:
        from database import test_db_connection

        db_ok, db_msg = test_db_connection()
        status_code = 200 if db_ok else 503
        return jsonify({"status": "ok" if db_ok else "error", "database": db_msg}), status_code
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@system_bp.route("/api/system/health")
def api_system_health():
    """Comprehensive system health check with Feishu readiness."""
    try:
        from database import test_db_connection
        from config import settings

        # Check database
        db_ok, db_msg = test_db_connection()

        # Check Feishu configuration
        feishu_configured = bool(
            settings.FEISHU_APP_ID and
            settings.FEISHU_APP_SECRET and
            settings.FEISHU_APP_TOKEN
        )
        feishu_status = "configured" if feishu_configured else "not_configured"

        # Overall status
        if db_ok and feishu_configured:
            overall_status = "healthy"
            status_code = 200
        elif db_ok and not feishu_configured:
            overall_status = "degraded"
            status_code = 200
        else:
            overall_status = "unhealthy"
            status_code = 503

        return jsonify({
            "status": overall_status,
            "checks": {
                "database": {
                    "status": "ok" if db_ok else "error",
                    "message": db_msg
                },
                "feishu": {
                    "status": feishu_status,
                    "message": "Feishu app credentials configured" if feishu_configured else "Feishu app credentials not configured"
                }
            }
        }), status_code
    except Exception as exc:
        logger.error("system health check failed: %s", exc)
        return jsonify({"status": "error", "message": str(exc)}), 500


@system_bp.route("/api/system/diagnostics/recent-errors")
@require_permission("admin:user_manage")
def api_recent_errors():
    """Query recent errors from logs - admin only."""
    try:
        from backend.services.tool_io_runtime import get_recent_operation_errors

        limit = 20
        errors = get_recent_operation_errors(limit)
        return jsonify({"success": True, "data": errors})
    except Exception as exc:
        logger.error("failed to query recent errors: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@system_bp.route("/api/system/diagnostics/notification-failures")
@require_permission("admin:user_manage")
def api_notification_failures():
    """Query recent notification failures - admin only."""
    try:
        from backend.services.tool_io_runtime import get_recent_notification_failures

        limit = 20
        failures = get_recent_notification_failures(limit)
        return jsonify({"success": True, "data": failures})
    except Exception as exc:
        logger.error("failed to query notification failures: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@system_bp.route("/api/db/test")
@require_permission("dashboard:view")
def api_db_test():
    try:
        from database import test_db_connection

        ok, msg = test_db_connection()
        return jsonify({"success": ok, "message": msg})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500
