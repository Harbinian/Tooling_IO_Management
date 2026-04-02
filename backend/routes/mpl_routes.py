# -*- coding: utf-8 -*-
"""MPL management routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import get_authenticated_user, get_json_dict, parse_positive_int_arg, require_permission, validation_error

mpl_bp = Blueprint("mpl_routes", __name__)
logger = logging.getLogger(__name__)


@mpl_bp.route("/api/mpl", methods=["GET"])
@require_permission("tool:view")
def api_list_mpl():
    try:
        from backend.services.tool_io_service import list_mpl_groups

        result = list_mpl_groups(
            {
                "page_no": parse_positive_int_arg("page_no", 1),
                "page_size": parse_positive_int_arg("page_size", 20),
                "drawing_no": request.args.get("drawing_no", ""),
                "keyword": request.args.get("keyword", ""),
            },
            current_user=get_authenticated_user(),
        )
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list mpl groups: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@mpl_bp.route("/api/mpl", methods=["POST"])
@require_permission("tool:view")
def api_create_mpl():
    try:
        from backend.services.tool_io_service import create_mpl_group

        result = create_mpl_group(get_json_dict(required=True), current_user=get_authenticated_user())
        return jsonify(result), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create mpl group: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@mpl_bp.route("/api/mpl/<mpl_no>", methods=["GET"])
@require_permission("tool:view")
def api_get_mpl(mpl_no):
    try:
        from backend.services.tool_io_service import get_mpl_group

        result = get_mpl_group(mpl_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to get mpl group %s: %s", mpl_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@mpl_bp.route("/api/mpl/<mpl_no>", methods=["PUT"])
@require_permission("tool:view")
def api_update_mpl(mpl_no):
    try:
        from backend.services.tool_io_service import update_mpl_group

        result = update_mpl_group(mpl_no, get_json_dict(required=True), current_user=get_authenticated_user())
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update mpl group %s: %s", mpl_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@mpl_bp.route("/api/mpl/<mpl_no>", methods=["DELETE"])
@require_permission("tool:view")
def api_delete_mpl(mpl_no):
    try:
        from backend.services.tool_io_service import delete_mpl_group

        result = delete_mpl_group(mpl_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to delete mpl group %s: %s", mpl_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@mpl_bp.route("/api/mpl/by-tool", methods=["GET"])
@require_permission("tool:view")
def api_get_mpl_by_tool():
    try:
        from backend.services.tool_io_service import get_mpl_by_tool

        drawing_no = str(request.args.get("drawing_no", "")).strip()
        revision = str(request.args.get("revision", "")).strip()
        if not drawing_no:
            return validation_error("drawing_no is required")
        if not revision:
            return validation_error("revision is required")
        result = get_mpl_by_tool(drawing_no, revision, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to query mpl by tool: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
