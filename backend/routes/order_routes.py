# -*- coding: utf-8 -*-
"""Order routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import (
    build_actor_payload,
    build_initiator_payload,
    build_keeper_payload,
    get_authenticated_user,
    get_json_dict,
    parse_positive_int_arg,
    require_permission,
    validation_error,
)

order_bp = Blueprint("order_routes", __name__)
logger = logging.getLogger(__name__)


@order_bp.route("/api/tool-io-orders", methods=["GET"])
@require_permission("order:list")  # TEAM_LEADER, KEEPER
def api_tool_io_orders_list():
    try:
        from backend.services.tool_io_service import list_orders

        result = list_orders(
            {
                "order_type": request.args.get("order_type"),
                "order_status": request.args.get("order_status"),
                "initiator_id": request.args.get("initiator_id"),
                "keeper_id": request.args.get("keeper_id"),
                "keyword": request.args.get("keyword"),
                "date_from": request.args.get("date_from"),
                "date_to": request.args.get("date_to"),
                "page_no": parse_positive_int_arg("page_no", 1),
                "page_size": parse_positive_int_arg("page_size", 20),
            },
            current_user=get_authenticated_user(),
        )
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list tool io orders: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders", methods=["POST"])
@require_permission("order:create")  # TEAM_LEADER
def api_tool_io_orders_create():
    try:
        from backend.services.tool_io_service import create_order

        data = build_initiator_payload(get_json_dict(required=True))
        result = create_order(data, current_user=get_authenticated_user())
        return (jsonify(result), 201) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create tool io order: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>", methods=["GET"])
@require_permission("order:view")  # TEAM_LEADER, KEEPER
def api_tool_io_order_detail(order_no):
    try:
        from backend.services.tool_io_service import get_order_detail

        order = get_order_detail(order_no, current_user=get_authenticated_user())
        if not order:
            return jsonify({"success": False, "error": "order not found"}), 404
        return jsonify({"success": True, "data": order})
    except Exception as exc:
        logger.error("failed to get order detail %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>", methods=["PUT"])
@require_permission("order:submit")  # TEAM_LEADER
def api_tool_io_order_update(order_no):
    """Update order content (items, remark) when order is in draft status."""
    try:
        from backend.services.tool_io_service import update_order

        result = update_order(
            order_no,
            get_json_dict(required=True),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update order %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/submit", methods=["POST"])
@require_permission("order:submit")  # TEAM_LEADER
def api_tool_io_order_submit(order_no):
    try:
        from backend.services.tool_io_service import submit_order

        result = submit_order(
            order_no,
            build_actor_payload(get_json_dict(required=True)),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to submit order %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/keeper-confirm", methods=["POST"])
@require_permission("order:keeper_confirm")  # KEEPER
def api_tool_io_order_keeper_confirm(order_no):
    try:
        from backend.services.tool_io_service import keeper_confirm

        data = build_keeper_payload(get_json_dict(required=True))
        if not isinstance(data.get("items"), list):
            return validation_error("items must be a JSON array")
        result = keeper_confirm(order_no, data, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("keeper confirmation failed for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/final-confirm", methods=["POST"])
@require_permission("order:final_confirm")  # TEAM_LEADER
def api_tool_io_order_final_confirm(order_no):
    try:
        from backend.services.tool_io_service import final_confirm

        result = final_confirm(
            order_no,
            build_actor_payload(get_json_dict(required=True)),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("final confirmation failed for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/final-confirm-availability", methods=["GET"])
@require_permission("order:view")  # TEAM_LEADER, KEEPER
def api_tool_io_order_final_confirm_availability(order_no):
    try:
        from backend.services.tool_io_service import get_final_confirm_availability

        user = get_authenticated_user()
        operator_role = "keeper" if "order:keeper_confirm" in set(user.get("permissions", [])) else "initiator"
        result = get_final_confirm_availability(order_no, user.get("user_id", ""), operator_role, current_user=user)
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to query final confirm availability %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc), "available": False}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/assign-transport", methods=["POST"])
@require_permission("order:keeper_confirm")  # KEEPER
def api_tool_io_order_assign_transport(order_no):
    try:
        from backend.services.tool_io_service import assign_transport

        result = assign_transport(
            order_no,
            build_actor_payload(get_json_dict(required=True), role_fallback="keeper"),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to assign transport for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/transport-start", methods=["POST"])
@require_permission("order:transport_execute")  # PRODUCTION_PREP, SYS_ADMIN
def api_tool_io_order_transport_start(order_no):
    try:
        from backend.services.tool_io_service import start_transport

        result = start_transport(
            order_no,
            build_actor_payload(get_json_dict(), role_fallback="transport_operator"),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to start transport for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/transport-complete", methods=["POST"])
@require_permission("order:transport_execute")  # PRODUCTION_PREP, SYS_ADMIN
def api_tool_io_order_transport_complete(order_no):
    try:
        from backend.services.tool_io_service import complete_transport

        result = complete_transport(
            order_no,
            build_actor_payload(get_json_dict(), role_fallback="transport_operator"),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to complete transport for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/report-transport-issue", methods=["POST"])
@require_permission("order:transport_execute")  # PRODUCTION_PREP, KEEPER, SYS_ADMIN
def api_tool_io_order_report_transport_issue(order_no):
    try:
        from backend.services.transport_issue_service import report_transport_issue

        result = report_transport_issue(
            order_no,
            get_json_dict(required=True),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result), 201
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to report transport issue for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/transport-issues", methods=["GET"])
@require_permission("order:view")  # TEAM_LEADER, KEEPER, PLANNER, AUDITOR
def api_tool_io_order_transport_issues(order_no):
    try:
        from backend.services.transport_issue_service import get_transport_issues

        result = get_transport_issues(order_no, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except Exception as exc:
        logger.error("failed to query transport issues for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/resolve-transport-issue", methods=["POST"])
@require_permission("order:keeper_confirm")  # KEEPER
def api_tool_io_order_resolve_transport_issue(order_no):
    try:
        from backend.services.transport_issue_service import resolve_transport_issue

        result = resolve_transport_issue(
            order_no,
            get_json_dict(required=True),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        if result.get("error") == "issue not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to resolve transport issue for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/reject", methods=["POST"])
@require_permission("order:cancel")  # TEAM_LEADER, KEEPER
def api_tool_io_order_reject(order_no):
    try:
        from backend.services.tool_io_service import reject_order

        data = build_actor_payload(get_json_dict(required=True))
        if not data.get("reject_reason"):
            return validation_error("reject_reason is required")
        result = reject_order(order_no, data, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to reject order %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/reset-to-draft", methods=["POST"])
@require_permission("order:submit")  # TEAM_LEADER
def api_tool_io_order_reset_to_draft(order_no):
    try:
        from backend.services.tool_io_service import reset_order_to_draft

        result = reset_order_to_draft(
            order_no,
            build_actor_payload(get_json_dict(required=True)),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to reset order %s to draft: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/cancel", methods=["POST"])
@require_permission("order:cancel")  # TEAM_LEADER, KEEPER
def api_tool_io_order_cancel(order_no):
    try:
        from backend.services.tool_io_service import cancel_order

        result = cancel_order(
            order_no,
            build_actor_payload(get_json_dict(required=True)),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to cancel order %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>", methods=["DELETE"])
def api_tool_io_order_delete(order_no):
    # Custom permission check: SYS_ADMIN (order:delete) OR TEAM_LEADER (delete own draft)
    user = get_authenticated_user()
    user_permissions = set(user.get("permissions") or [])
    user_role_codes = set(user.get("role_codes") or [])

    is_admin = "order:delete" in user_permissions or "admin:user_manage" in user_permissions
    # NOTE: All role_code comparisons must be case-insensitive.
    is_team_leader = any(str(role_code).strip().lower() == "team_leader" for role_code in user_role_codes)

    if not (is_admin or is_team_leader):
        return jsonify({"success": False, "error": "无权删除单据"}), 403

    try:
        from backend.services.tool_io_service import delete_order

        # For team_leader, pass role so repository can do ownership check
        payload = build_actor_payload(get_json_dict(required=True))
        if is_team_leader and not is_admin:
            # Override operator_role to team_leader for business rule check in repository
            payload["operator_role"] = "team_leader"

        result = delete_order(
            order_no,
            payload,
            current_user=user,
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to delete order %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/logs", methods=["GET"])
@require_permission("order:view")  # TEAM_LEADER, KEEPER
def api_tool_io_order_logs(order_no):
    try:
        from backend.services.tool_io_service import get_order_logs

        result = get_order_logs(order_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to load order logs %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/notification-records", methods=["GET"])
@require_permission("notification:view")  # TEAM_LEADER, KEEPER, PLANNER, AUDITOR
def api_tool_io_order_notification_records(order_no):
    try:
        from backend.services.tool_io_service import get_notification_records

        result = get_notification_records(order_no, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        if result.get("error") == "authentication required":
            return jsonify(result), 401
        return jsonify(result), 500
    except Exception as exc:
        logger.error("failed to load notification records %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc), "data": []}), 500


@order_bp.route("/api/notifications", methods=["GET"])
@require_permission("notification:view")  # TEAM_LEADER, KEEPER, PLANNER, AUDITOR
def api_notifications_list():
    try:
        from backend.services.tool_io_service import get_current_user_notifications

        result = get_current_user_notifications(
            {
                "status": request.args.get("status", ""),
                "page_no": parse_positive_int_arg("page_no", 1),
                "page_size": parse_positive_int_arg("page_size", 20),
            },
            current_user=get_authenticated_user(),
        )
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list current user notifications: %s", exc)
        return jsonify({"success": False, "error": str(exc), "data": []}), 500


@order_bp.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@require_permission("notification:view")  # TEAM_LEADER, KEEPER, PLANNER, AUDITOR
def api_notification_mark_read(notification_id):
    try:
        from backend.services.tool_io_service import mark_current_user_notification_read

        result = mark_current_user_notification_read(notification_id, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "notification not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except Exception as exc:
        logger.error("failed to mark notification %s as read: %s", notification_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/pending-keeper", methods=["GET"])
@require_permission("order:keeper_confirm")  # KEEPER
def api_tool_io_orders_pending_keeper():
    try:
        from backend.services.tool_io_service import get_pending_keeper_list

        orders = get_pending_keeper_list(request.args.get("keeper_id"), current_user=get_authenticated_user())
        return jsonify({"success": True, "data": orders})
    except Exception as exc:
        logger.error("failed to load pending keeper orders: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/pre-transport", methods=["GET"])
@require_permission("order:transport_execute")  # PRODUCTION_PREP, KEEPER, SYS_ADMIN
def api_tool_io_orders_pre_transport():
    try:
        from backend.services.tool_io_service import get_pre_transport_orders

        result = get_pre_transport_orders(current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        return jsonify(result), 400
    except Exception as exc:
        logger.error("failed to load pre-transport orders: %s", exc)
        return jsonify({"success": False, "error": str(exc), "orders": []}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/generate-keeper-text", methods=["GET"])
@require_permission("notification:create")  # KEEPER
def api_generate_keeper_text(order_no):
    try:
        from backend.services.tool_io_service import generate_keeper_text

        result = generate_keeper_text(order_no, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        return jsonify(result), 404 if result.get("error") == "order not found" else 400
    except Exception as exc:
        logger.error("failed to generate keeper text %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/preview-keeper-text", methods=["POST"])
@require_permission("notification:create")  # KEEPER
def api_preview_keeper_text():
    try:
        from backend.services.tool_io_service import preview_keeper_text

        data = build_initiator_payload(get_json_dict(required=True))
        result = preview_keeper_text(data, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to preview keeper text: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/generate-transport-text", methods=["GET"])
@require_permission("notification:create")  # KEEPER
def api_generate_transport_text(order_no):
    try:
        from backend.services.tool_io_service import generate_transport_text

        result = generate_transport_text(order_no, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        # Return 200 with error message for business logic errors (e.g., no approved items)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 200  # Return 200 with success: false for business errors
    except Exception as exc:
        logger.error("failed to generate transport text %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/notify-transport", methods=["POST"])
@require_permission("notification:send_feishu")  # KEEPER
def api_notify_transport(order_no):
    try:
        from backend.services.tool_io_service import notify_transport

        result = notify_transport(
            order_no,
            build_actor_payload(get_json_dict(), role_fallback="keeper"),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("transport notification failed for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/notify-keeper", methods=["POST"])
@require_permission("notification:send_feishu")  # KEEPER
def api_notify_keeper(order_no):
    try:
        from backend.services.tool_io_service import notify_keeper

        result = notify_keeper(
            order_no,
            build_actor_payload(get_json_dict()),
            current_user=get_authenticated_user(),
        )
        if result.get("success"):
            return jsonify(result)
        if result.get("error") == "order not found":
            return jsonify(result), 404
        return jsonify(result), 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("keeper notification failed for %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
