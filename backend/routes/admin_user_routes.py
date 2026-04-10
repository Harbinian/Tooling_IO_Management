# -*- coding: utf-8 -*-
"""Administrator-only user management routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import (
    get_authenticated_user,
    get_json_dict,
    parse_positive_int_arg,
    require_auth,
    require_permission,
    validation_error,
)
from backend.services.admin_user_service import (
    assign_user_roles,
    create_user,
    get_user_detail,
    list_users,
    reset_user_password,
    update_user,
    update_user_status,
)
from backend.services.rbac_service import (
    assign_role_permissions,
    create_permission,
    create_role,
    delete_permission,
    delete_role,
    get_permissions,
    get_role_detail,
    get_role_permissions,
    get_roles,
    update_permission,
    update_role,
)
from backend.database.repositories.rbac_repository import RbacRepository

admin_user_bp = Blueprint("admin_user_routes", __name__)
logger = logging.getLogger(__name__)


@admin_user_bp.route("/api/admin/roles", methods=["GET"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_list_roles():
    try:
        data = get_roles(
            keyword=request.args.get("keyword", ""),
            status=request.args.get("status", ""),
            role_type=request.args.get("role_type", ""),
        )
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list admin roles: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles", methods=["POST"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_create_role():
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = create_role(payload, actor.get("user_id", ""))
        return jsonify({"success": True, "data": data}), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create admin role: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>", methods=["PUT"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_update_role(role_id):
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = update_role(role_id, payload, actor.get("user_id", ""))
        if not data:
            return jsonify({"success": False, "error": "role not found"}), 404
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update admin role: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>", methods=["DELETE"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_delete_role(role_id):
    try:
        success, message = delete_role(role_id)
        if not success and message == "role not found":
            return jsonify({"success": False, "error": message}), 404
        if not success:
            return validation_error(message)
        return jsonify({"success": True})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to delete admin role: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>/permissions", methods=["GET"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_get_role_permissions(role_id):
    try:
        # Use repository directly to avoid ensure_rbac_tables() which re-inserts
        # incremental defaults and pollutes explicitly assigned permission data.
        # NOTE: get_role_detail from rbac_service also triggers ensure_rbac_tables()
        # via _get_rbac_repository(), so we use repo.get_role_by_id() instead.
        repo = RbacRepository()
        if not repo.get_role_by_id(role_id):
            return jsonify({"success": False, "error": "role not found"}), 404
        raw_data = repo.get_role_permissions(role_id)
        return jsonify({"success": True, "data": raw_data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to get role permissions: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/roles/<role_id>/permissions", methods=["PUT"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_assign_role_permissions(role_id):
    try:
        payload = get_json_dict(required=True)
        permission_codes = payload.get("permission_codes") or []
        if not isinstance(permission_codes, list):
            raise ValueError("permission_codes must be an array")
        actor = get_authenticated_user()
        assign_role_permissions(role_id, permission_codes, actor.get("user_id", ""))
        # Use repository directly to avoid ensure_rbac_tables() which re-inserts
        # incremental defaults and resets explicitly assigned permissions.
        repo = RbacRepository()
        result_data = repo.get_role_permissions(role_id)
        return jsonify({"success": True, "data": result_data, "_debug_sent": permission_codes})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to assign role permissions: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/permissions", methods=["GET"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_list_permissions():
    try:
        data = get_permissions(
            keyword=request.args.get("keyword", ""),
            status=request.args.get("status", ""),
            page=parse_positive_int_arg("page", 1),
            page_size=parse_positive_int_arg("page_size", 20),
        )
        return jsonify(
            {
                "success": True,
                "data": data.get("items", []),
                "total": data.get("total", 0),
                "page": data.get("page", 1),
                "page_size": data.get("page_size", 20),
            }
        )
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list permissions: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/permissions", methods=["POST"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_create_permission():
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = create_permission(payload, actor.get("user_id", ""))
        return jsonify({"success": True, "data": data}), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create permission: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/permissions/<permission_code>", methods=["PUT"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_update_permission(permission_code):
    try:
        payload = get_json_dict(required=True)
        actor = get_authenticated_user()
        data = update_permission(permission_code, payload, actor.get("user_id", ""))
        if not data:
            return jsonify({"success": False, "error": "permission not found"}), 404
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update permission: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@admin_user_bp.route("/api/admin/permissions/<permission_code>", methods=["DELETE"])
@require_auth
@require_permission("admin:role_manage")
def api_admin_delete_permission(permission_code):
    try:
        success, message = delete_permission(permission_code)
        if not success and message == "permission not found":
            return jsonify({"success": False, "error": message}), 404
        if not success:
            return validation_error(message)
        return jsonify({"success": True})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to delete permission: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


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
