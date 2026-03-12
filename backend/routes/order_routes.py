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
@require_permission("order:list")
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
@require_permission("order:create")
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
@require_permission("order:view")
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


@order_bp.route("/api/tool-io-orders/<order_no>/submit", methods=["POST"])
@require_permission("order:submit")
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
@require_permission("order:keeper_confirm")
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
@require_permission("order:final_confirm")
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
@require_permission("order:view")
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
@require_permission("order:keeper_confirm")
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
@require_permission("order:transport_execute")
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
@require_permission("order:transport_execute")
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


@order_bp.route("/api/tool-io-orders/<order_no>/reject", methods=["POST"])
@require_permission("order:cancel")
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


@order_bp.route("/api/tool-io-orders/<order_no>/cancel", methods=["POST"])
@require_permission("order:cancel")
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


@order_bp.route("/api/tool-io-orders/<order_no>/logs", methods=["GET"])
@require_permission("order:view")
def api_tool_io_order_logs(order_no):
    try:
        from backend.services.tool_io_service import get_order_logs

        result = get_order_logs(order_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to load order logs %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/notification-records", methods=["GET"])
@require_permission("notification:view")
def api_tool_io_order_notification_records(order_no):
    try:
        from backend.services.tool_io_service import get_notification_records

        result = get_notification_records(order_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to load notification records %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc), "data": []}), 500


@order_bp.route("/api/notifications", methods=["GET"])
@require_permission("notification:view")
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
@require_permission("notification:view")
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
@require_permission("order:keeper_confirm")
def api_tool_io_orders_pending_keeper():
    try:
        from backend.services.tool_io_service import get_pending_keeper_list

        orders = get_pending_keeper_list(request.args.get("keeper_id"), current_user=get_authenticated_user())
        return jsonify({"success": True, "data": orders})
    except Exception as exc:
        logger.error("failed to load pending keeper orders: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/generate-keeper-text", methods=["GET"])
@require_permission("notification:create")
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


@order_bp.route("/api/tool-io-orders/<order_no>/generate-transport-text", methods=["GET"])
@require_permission("notification:create")
def api_generate_transport_text(order_no):
    try:
        from backend.services.tool_io_service import generate_transport_text

        result = generate_transport_text(order_no, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        return jsonify(result), 404 if result.get("error") == "order not found" else 400
    except Exception as exc:
        logger.error("failed to generate transport text %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@order_bp.route("/api/tool-io-orders/<order_no>/notify-transport", methods=["POST"])
@require_permission("notification:send_feishu")
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
@require_permission("notification:send_feishu")
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
