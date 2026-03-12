# -*- coding: utf-8 -*-
"""Dashboard routes."""

import logging
from flask import Blueprint, jsonify
from backend.routes.common import get_authenticated_user, require_permission

dashboard_bp = Blueprint("dashboard_routes", __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route("/api/dashboard/metrics", methods=["GET"])
@require_permission("order:list") # Reusing list permission for dashboard overview
def api_dashboard_metrics():
    try:
        from backend.services.tool_io_service import get_dashboard_stats
        result = get_dashboard_stats(current_user=get_authenticated_user())
        return jsonify(result)
    except Exception as exc:
        logger.error("failed to get dashboard metrics: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
