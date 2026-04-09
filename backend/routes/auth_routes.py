# -*- coding: utf-8 -*-
"""Authentication routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.extensions import limiter
from backend.routes.common import get_authenticated_user, get_json_dict, require_auth, validation_error

auth_bp = Blueprint("auth_routes", __name__)
logger = logging.getLogger(__name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
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


@auth_bp.route("/api/user/change-password", methods=["POST"])
@require_auth
def api_user_change_password():
    try:
        from backend.services.auth_service import (
            InvalidCredentialsError,
            change_current_user_password,
        )

        payload = get_json_dict(required=True)
        user = get_authenticated_user()
        change_current_user_password(
            user_id=user.get("user_id", ""),
            old_password=payload.get("old_password", ""),
            new_password=payload.get("new_password", ""),
            client_ip=request.remote_addr or "",
        )
        return jsonify({"success": True})
    except ValueError as exc:
        return validation_error(str(exc))
    except InvalidCredentialsError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        logger.error("change password failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@auth_bp.route("/api/auth/logout", methods=["POST"])
def api_auth_logout():
    """Logout endpoint.

    Since the auth system is stateless (token stored client-side),
    the server cannot invalidate the token. This endpoint exists
    for semantic completeness. Actual session cleanup is done client-side.
    """
    return jsonify({"success": True, "message": "logout success"})
