# -*- coding: utf-8 -*-
"""Feedback routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import (
    get_authenticated_user,
    get_json_dict,
    require_auth,
    require_permission,
    validation_error,
)

feedback_bp = Blueprint("feedback_routes", __name__)
logger = logging.getLogger(__name__)


@feedback_bp.route("/api/feedback", methods=["GET"])
@require_auth
def api_feedback_list():
    try:
        from backend.services.feedback_service import list_feedback, resolve_feedback_owner_filter

        user = get_authenticated_user()
        login_name_filter = resolve_feedback_owner_filter(
            requested_login_name=request.args.get("login_name", ""),
            current_user=user,
        )
        data = list_feedback(
            login_name=login_name_filter,
            status=request.args.get("status", ""),
            limit=request.args.get("limit", 200),
        )
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list feedback: %s", exc)
        return jsonify({"success": False, "error": str(exc), "data": []}), 500


@feedback_bp.route("/api/feedback", methods=["POST"])
@require_auth
def api_feedback_create():
    try:
        from backend.services.feedback_service import create_feedback

        payload = get_json_dict(required=True)
        user = get_authenticated_user()
        data = create_feedback(
            payload,
            login_name=user.get("login_name", ""),
            user_name=user.get("display_name", ""),
        )
        return jsonify({"success": True, "data": data}), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create feedback: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@feedback_bp.route("/api/feedback/<int:feedback_id>", methods=["DELETE"])
@require_auth
def api_feedback_delete(feedback_id: int):
    try:
        from backend.services.feedback_service import delete_feedback

        user = get_authenticated_user()
        permissions = set(user.get("permissions") or [])
        deleted = delete_feedback(
            feedback_id,
            login_name=user.get("login_name", ""),
            is_admin="admin:user_manage" in permissions,
        )
        if not deleted:
            return jsonify({"success": False, "error": "feedback not found"}), 404
        return jsonify({"success": True})
    except Exception as exc:
        logger.error("failed to delete feedback %s: %s", feedback_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@feedback_bp.route("/api/feedback/all", methods=["GET"])
@require_permission("admin:user_manage")
def api_admin_feedback_list_all():
    try:
        from backend.services.feedback_service import list_all_feedback

        data, total = list_all_feedback(
            status=request.args.get("status", ""),
            category=request.args.get("category", ""),
            keyword=request.args.get("keyword", ""),
            limit=request.args.get("limit", 50),
            offset=request.args.get("offset", 0),
        )
        return jsonify({"success": True, "data": data, "total": total})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list all feedback for admin: %s", exc)
        return jsonify({"success": False, "error": str(exc), "data": [], "total": 0}), 500


@feedback_bp.route("/api/feedback/<int:feedback_id>/status", methods=["PUT"])
@require_permission("admin:user_manage")
def api_admin_feedback_update_status(feedback_id: int):
    try:
        from backend.services.feedback_service import update_feedback_status

        payload = get_json_dict(required=True)
        user = get_authenticated_user()
        data = update_feedback_status(
            feedback_id,
            payload.get("new_status", ""),
            login_name=user.get("login_name", ""),
            user_name=user.get("display_name", ""),
        )
        if not data:
            return jsonify({"success": False, "error": "feedback not found"}), 404
        return jsonify({"success": True, "data": data})
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update feedback status %s: %s", feedback_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@feedback_bp.route("/api/feedback/<int:feedback_id>/reply", methods=["POST"])
@require_permission("admin:user_manage")
def api_admin_feedback_add_reply(feedback_id: int):
    try:
        from backend.services.feedback_service import add_feedback_reply

        payload = get_json_dict(required=True)
        user = get_authenticated_user()
        data = add_feedback_reply(
            feedback_id,
            payload.get("content", ""),
            login_name=user.get("login_name", ""),
            user_name=user.get("display_name", ""),
        )
        if not data:
            return jsonify({"success": False, "error": "feedback not found"}), 404
        return jsonify({"success": True, "data": data}), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to add feedback reply %s: %s", feedback_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@feedback_bp.route("/api/feedback/<int:feedback_id>/replies", methods=["GET"])
@require_permission("admin:user_manage")
def api_admin_feedback_get_replies(feedback_id: int):
    try:
        from backend.services.feedback_service import get_feedback_replies

        data = get_feedback_replies(feedback_id)
        return jsonify({"success": True, "data": data})
    except Exception as exc:
        logger.error("failed to get feedback replies %s: %s", feedback_id, exc)
        return jsonify({"success": False, "error": str(exc), "data": []}), 500
