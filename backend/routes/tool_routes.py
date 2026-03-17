# -*- coding: utf-8 -*-
"""Tool routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import (
    get_authenticated_user,
    get_json_dict,
    parse_positive_int_arg,
    require_permission,
    validation_error,
)

tool_bp = Blueprint("tool_routes", __name__)
logger = logging.getLogger(__name__)


@tool_bp.route("/api/tools/search", methods=["GET"])
@require_permission("tool:search")
def api_tools_search():
    try:
        from backend.services.tool_io_service import search_tool_inventory

        result = search_tool_inventory(
            {
                "keyword": request.args.get("keyword"),
                "status": request.args.get("status"),
                "location": request.args.get("location"),
                "location_id": request.args.get("location_id"),
                "page_no": parse_positive_int_arg("page_no", 1),
                "page_size": parse_positive_int_arg("page_size", 20),
            }
        )
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("tool search failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@tool_bp.route("/api/tools/batch-query", methods=["POST"])
@require_permission("tool:view")
def api_tools_batch_query():
    try:
        from backend.services.tool_io_service import batch_query_tools

        data = get_json_dict(required=True)
        tool_codes = data.get("tool_codes")
        if not isinstance(tool_codes, list):
            return validation_error("tool_codes must be a JSON array")
        result = batch_query_tools(tool_codes)
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("batch query failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@tool_bp.route("/api/tools/batch-status", methods=["PATCH"])
@require_permission("tool:status_update")
def api_batch_update_tool_status():
    try:
        from backend.services.tool_io_service import batch_update_tool_status

        data = get_json_dict(required=True)
        tool_codes = data.get("tool_codes")
        new_status = data.get("new_status")
        if not isinstance(tool_codes, list):
            return validation_error("tool_codes must be a JSON array")
        if not isinstance(new_status, str) or not new_status.strip():
            return validation_error("new_status is required")

        user = get_authenticated_user()
        client_ip = (request.headers.get("X-Forwarded-For") or request.remote_addr or "").split(",")[0].strip()
        result = batch_update_tool_status(
            tool_codes=tool_codes,
            new_status=new_status,
            remark=data.get("remark", ""),
            operator={
                "user_id": user.get("user_id", ""),
                "display_name": user.get("display_name", ""),
            },
            client_ip=client_ip,
        )
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("batch status update failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@tool_bp.route("/api/tools/status-history/<tool_code>", methods=["GET"])
@require_permission("tool:view")
def api_tool_status_history(tool_code: str):
    try:
        from backend.services.tool_io_service import get_tool_status_history

        result = get_tool_status_history(
            tool_code=tool_code,
            page_no=parse_positive_int_arg("page_no", 1),
            page_size=parse_positive_int_arg("page_size", 20),
        )
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("status history query failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
