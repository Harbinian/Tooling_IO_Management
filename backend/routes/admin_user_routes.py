# -*- coding: utf-8 -*-
"""Administrator-only user management routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import get_authenticated_user, get_json_dict, require_permission, validation_error
from backend.services.admin_user_service import (
    assign_user_roles,
    create_user,
    get_user_detail,
    list_roles,
    list_users,
    reset_user_password,
    update_user,
    update_user_status,
)

admin_user_bp = Blueprint("admin_user_routes", __name__)
logger = logging.getLogger(__name__)


@admin_user_bp.route("/api/admin/roles", methods=["GET"])
@require_permission("admin:user_manage")
def api_admin_list_roles():
    return jsonify({"success": True, "data": list_roles()})


@admin_user_bp.route("/api/admin/users", methods=["GET"])
@require_permission("admin:user_manage")
def api_admin_list_users():
    try:
        data = list_users(
            keyword=request.args.get("keyword", ""),
            status=request.args.get("status", ""),
            org_id=request.args.get("org_id", ""),
        )
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list admin users: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/users/<user_id>", methods=["GET"])
@require_permission("admin:user_manage")
def api_admin_get_user(user_id):
    try:
        data = get_user_detail(user_id)
        if not data:
            return jsonify({"success": False, "error": "user not found"}), 404
        return jsonify({"success": True, "data": data})
    except Exception as exc:
        logger.error("failed to get admin user detail: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/users", methods=["POST"])
@require_permission("admin:user_manage")
def api_admin_create_user():
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = create_user(payload, actor.get("user_id", ""))
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create admin user: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/users/<user_id>", methods=["PUT"])
@require_permission("admin:user_manage")
def api_admin_update_user(user_id):
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = update_user(user_id, payload, actor.get("user_id", ""))
        if not data:
            return jsonify({"success": False, "error": "user not found"}), 404
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update admin user: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/users/<user_id>/roles", methods=["PUT"])
@require_permission("admin:user_manage")
def api_admin_assign_user_roles(user_id):
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = assign_user_roles(
            user_id,
            payload.get("role_ids") or [],
            payload.get("org_id") or "",
            actor.get("user_id", ""),
        )
        if not data:
            return jsonify({"success": False, "error": "user not found"}), 404
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to assign admin user roles: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/users/<user_id>/status", methods=["PUT"])
@require_permission("admin:user_manage")
def api_admin_update_user_status(user_id):
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = update_user_status(user_id, payload.get("status", ""), actor.get("user_id", ""))
        if not data:
            return jsonify({"success": False, "error": "user not found"}), 404
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update admin user status: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/users/<user_id>/password-reset", methods=["PUT"])
@require_permission("admin:user_manage")
def api_admin_reset_user_password(user_id):
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = reset_user_password(user_id, payload.get("new_password", ""), actor.get("user_id", ""))
        if not data:
            return jsonify({"success": False, "error": "user not found"}), 404
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to reset admin user password: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
