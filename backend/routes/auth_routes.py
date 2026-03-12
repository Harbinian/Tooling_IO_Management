# -*- coding: utf-8 -*-
"""Authentication routes."""

import logging

from flask import Blueprint, jsonify

from backend.routes.common import get_authenticated_user, get_json_dict, require_auth, validation_error

auth_bp = Blueprint("auth_routes", __name__)
logger = logging.getLogger(__name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    try:
        from backend.services.auth_service import AuthError, authenticate_user

        data = get_json_dict(required=True)
        result = authenticate_user(data.get("login_name", ""), data.get("password", ""))
        return jsonify({"success": True, **result})
    except ValueError as exc:
        return validation_error(str(exc))
    except AuthError as exc:
        return jsonify({"success": False, "error": str(exc)}), 401
    except Exception as exc:
        logger.error("login failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@auth_bp.route("/api/auth/me", methods=["GET"])
@require_auth
def api_auth_me():
    return jsonify({"success": True, "user": get_authenticated_user()})
