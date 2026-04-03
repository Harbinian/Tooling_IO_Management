# -*- coding: utf-8 -*-
"""Workflow user lookup routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import require_permission, validation_error
from backend.services.user_service import list_users_by_role

user_bp = Blueprint("user_routes", __name__)
logger = logging.getLogger(__name__)


@user_bp.route("/api/users/by-role/<role_code>", methods=["GET"])
@require_permission("dashboard:view")
def api_get_users_by_role(role_code):
    """Return active users for one role code, optionally filtered by org_id."""
    try:
        data = list_users_by_role(role_code, request.args.get("org_id", ""))
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list users by role %s: %s", role_code, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
