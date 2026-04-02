# -*- coding: utf-8 -*-
"""Inspection workflow API routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import (
    get_authenticated_user,
    get_json_dict,
    parse_positive_int_arg,
    require_permission,
    validation_error,
)

inspection_bp = Blueprint("inspection_routes", __name__)
logger = logging.getLogger(__name__)


@inspection_bp.route("/api/inspection/stats/summary", methods=["GET"])
@require_permission("inspection:list")
def api_inspection_stats_summary():
    try:
        from backend.services.inspection_stats_service import get_summary

        result = get_summary(current_user=get_authenticated_user())
        return jsonify(result)
    except Exception as exc:
        logger.error("failed to get inspection stats summary: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/plans", methods=["GET"])
@require_permission("inspection:list")
def api_inspection_plan_list():
    try:
        from backend.services.inspection_plan_service import list_plans

        result = list_plans(
            {
                "status": request.args.get("status"),
                "plan_year": request.args.get("plan_year"),
                "plan_month": request.args.get("plan_month"),
                "creator_id": request.args.get("creator_id"),
                "inspection_type": request.args.get("inspection_type"),
                "keyword": request.args.get("keyword"),
                "page_no": parse_positive_int_arg("page_no", 1),
                "page_size": parse_positive_int_arg("page_size", 20),
            },
            current_user=get_authenticated_user(),
        )
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list inspection plans: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/plans", methods=["POST"])
@require_permission("inspection:create")
def api_inspection_plan_create():
    try:
        from backend.services.inspection_plan_service import create_plan

        result = create_plan(get_json_dict(required=True), current_user=get_authenticated_user())
        return (jsonify(result), 201) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create inspection plan: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/plans/<plan_no>", methods=["GET"])
@require_permission("inspection:view")
def api_inspection_plan_detail(plan_no):
    try:
        from backend.services.inspection_plan_service import get_plan

        result = get_plan(plan_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to get inspection plan %s: %s", plan_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/plans/<plan_no>", methods=["PUT"])
@require_permission("inspection:write")
def api_inspection_plan_update(plan_no):
    try:
        from backend.services.inspection_plan_service import update_plan

        result = update_plan(plan_no, get_json_dict(required=True), current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        return jsonify(result), 404 if result.get("error") == "inspection plan not found" else 400
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update inspection plan %s: %s", plan_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/plans/<plan_no>/publish", methods=["POST"])
@require_permission("inspection:publish")
def api_inspection_plan_publish(plan_no):
    try:
        from backend.services.inspection_plan_service import publish_plan

        result = publish_plan(plan_no, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        return jsonify(result), 404 if result.get("error") == "inspection plan not found" else 400
    except Exception as exc:
        logger.error("failed to publish inspection plan %s: %s", plan_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/plans/<plan_no>/preview-tasks", methods=["GET"])
@require_permission("inspection:list")
def api_inspection_plan_preview(plan_no):
    try:
        from backend.services.inspection_plan_service import preview_tasks

        result = preview_tasks(plan_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to preview inspection plan tasks %s: %s", plan_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/plans/<plan_no>/close", methods=["POST"])
@require_permission("inspection:close")
def api_inspection_plan_close(plan_no):
    try:
        from backend.services.inspection_plan_service import close_plan

        result = close_plan(plan_no, current_user=get_authenticated_user())
        if result.get("success"):
            return jsonify(result)
        return jsonify(result), 404 if result.get("error") == "inspection plan not found" else 400
    except Exception as exc:
        logger.error("failed to close inspection plan %s: %s", plan_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks", methods=["GET"])
@require_permission("inspection:list")
def api_inspection_task_list():
    try:
        from backend.services.inspection_task_service import list_tasks

        result = list_tasks(
            {
                "task_status": request.args.get("task_status"),
                "plan_no": request.args.get("plan_no"),
                "assigned_to_id": request.args.get("assigned_to_id"),
                "inspection_result": request.args.get("inspection_result"),
                "report_no": request.args.get("report_no"),
                "keyword": request.args.get("keyword"),
                "page_no": parse_positive_int_arg("page_no", 1),
                "page_size": parse_positive_int_arg("page_size", 20),
            },
            current_user=get_authenticated_user(),
        )
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to list inspection tasks: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>", methods=["GET"])
@require_permission("inspection:view")
def api_inspection_task_detail(task_no):
    try:
        from backend.services.inspection_task_service import get_task

        result = get_task(task_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to get inspection task %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/receive", methods=["POST"])
@require_permission("inspection:execute")
def api_inspection_task_receive(task_no):
    try:
        from backend.services.inspection_task_service import receive_task

        result = receive_task(task_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to receive inspection task %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/start-inspection", methods=["POST"])
@require_permission("inspection:execute")
def api_inspection_task_start(task_no):
    try:
        from backend.services.inspection_task_service import start_inspection

        result = start_inspection(task_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to start inspection task %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/submit-report", methods=["POST"])
@require_permission("inspection:execute")
def api_inspection_task_submit_report(task_no):
    try:
        from backend.services.inspection_task_service import submit_report

        result = submit_report(task_no, get_json_dict(required=True), current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to submit inspection report for %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/accept", methods=["POST"])
@require_permission("inspection:accept")
def api_inspection_task_accept(task_no):
    try:
        from backend.services.inspection_task_service import accept_report

        result = accept_report(task_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to accept inspection report for %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/reject", methods=["POST"])
@require_permission("inspection:accept")
def api_inspection_task_reject(task_no):
    try:
        from backend.services.inspection_task_service import reject_report

        payload = get_json_dict(required=True)
        result = reject_report(task_no, str(payload.get("reject_reason") or "").strip(), current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to reject inspection report for %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/create-outbound", methods=["POST"])
@require_permission("inspection:execute")
def api_inspection_task_create_outbound(task_no):
    try:
        from backend.services.inspection_task_service import create_outbound_link

        payload = get_json_dict(required=True)
        result = create_outbound_link(task_no, str(payload.get("order_no") or "").strip(), current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to link outbound order for %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/create-inbound", methods=["POST"])
@require_permission("inspection:execute")
def api_inspection_task_create_inbound(task_no):
    try:
        from backend.services.inspection_task_service import create_inbound_link

        payload = get_json_dict(required=True)
        result = create_inbound_link(task_no, str(payload.get("order_no") or "").strip(), current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to link inbound order for %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/close", methods=["POST"])
@require_permission("inspection:close")
def api_inspection_task_close(task_no):
    try:
        from backend.services.inspection_task_service import close_task

        result = close_task(task_no, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to close inspection task %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/reschedule", methods=["PUT"])
@require_permission("inspection:execute")
def api_inspection_task_reschedule(task_no):
    try:
        from backend.services.inspection_task_service import reschedule_task

        payload = get_json_dict(required=True)
        new_deadline = payload.get("deadline")
        if not new_deadline:
            return validation_error("deadline is required")
        result = reschedule_task(task_no, new_deadline, current_user=get_authenticated_user())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to reschedule inspection task %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/tasks/<task_no>/linked-orders", methods=["GET"])
@require_permission("inspection:view")
def api_inspection_task_linked_orders(task_no):
    try:
        from backend.services.inspection_task_service import get_linked_orders

        result = get_linked_orders(task_no)
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to get linked orders for %s: %s", task_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/orders/<order_no>/link-task", methods=["POST"])
@require_permission("inspection:execute")
def api_inspection_order_link_task(order_no):
    try:
        from backend.services.inspection_task_service import link_order_to_task

        payload = get_json_dict(required=True)
        result = link_order_to_task(order_no, str(payload.get("task_no") or "").strip())
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to link order %s to task: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/status/<serial_no>", methods=["GET"])
@require_permission("inspection:list")
def api_inspection_status(serial_no):
    try:
        from backend.services.inspection_task_service import get_status_by_serial_no

        result = get_status_by_serial_no(serial_no)
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to query inspection status %s: %s", serial_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@inspection_bp.route("/api/inspection/advance-by-order/<order_no>", methods=["POST"])
@require_permission("inspection:execute")
def api_inspection_advance_by_order(order_no):
    try:
        from backend.services.inspection_task_service import check_and_advance_by_order_status

        result = check_and_advance_by_order_status(order_no)
        return jsonify(result) if result.get("success") else (jsonify(result), 400)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to advance inspection task by order %s: %s", order_no, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
