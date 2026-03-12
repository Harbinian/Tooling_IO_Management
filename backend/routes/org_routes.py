# -*- coding: utf-8 -*-
"""Organization routes."""

import logging

from flask import Blueprint, jsonify, request

from backend.routes.common import get_authenticated_user, get_json_dict, require_permission, validation_error

org_bp = Blueprint("org_routes", __name__)
logger = logging.getLogger(__name__)


@org_bp.route("/api/orgs", methods=["GET"])
@require_permission("dashboard:view")
def api_org_list():
    try:
        from backend.services.org_service import list_organizations

        include_disabled = request.args.get("include_disabled", "true").lower() == "true"
        return jsonify({"success": True, "data": list_organizations(include_disabled=include_disabled)})
    except Exception as exc:
        logger.error("failed to list organizations: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@org_bp.route("/api/orgs/tree", methods=["GET"])
@require_permission("dashboard:view")
def api_org_tree():
    try:
        from backend.services.org_service import get_org_tree

        include_disabled = request.args.get("include_disabled", "true").lower() == "true"
        return jsonify({"success": True, "data": get_org_tree(include_disabled=include_disabled)})
    except Exception as exc:
        logger.error("failed to build organization tree: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@org_bp.route("/api/orgs/<org_id>", methods=["GET"])
@require_permission("dashboard:view")
def api_org_detail(org_id):
    try:
        from backend.services.org_service import get_organization

        organization = get_organization(org_id)
        if not organization:
            return jsonify({"success": False, "error": "organization not found"}), 404
        return jsonify({"success": True, "data": organization})
    except Exception as exc:
        logger.error("failed to load organization %s: %s", org_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@org_bp.route("/api/orgs", methods=["POST"])
@require_permission("admin:user_manage")
def api_org_create():
    try:
        from backend.services.org_service import create_organization

        data = get_json_dict(required=True)
        result = create_organization(data, actor_user_id=get_authenticated_user().get("user_id", ""))
        return jsonify(result), 201
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to create organization: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@org_bp.route("/api/orgs/<org_id>", methods=["PUT"])
@require_permission("admin:user_manage")
def api_org_update(org_id):
    try:
        from backend.services.org_service import update_organization

        data = get_json_dict(required=True)
        result = update_organization(org_id, data, actor_user_id=get_authenticated_user().get("user_id", ""))
        if result.get("success"):
            return jsonify(result)
        return jsonify(result), 404
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update organization %s: %s", org_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
