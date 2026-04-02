# -*- coding: utf-8 -*-
"""System configuration routes."""

import logging

from flask import Blueprint, jsonify

from backend.routes.common import get_json_dict, get_authenticated_user, require_permission, validation_error

system_config_bp = Blueprint("system_config_routes", __name__)
logger = logging.getLogger(__name__)


@system_config_bp.route("/api/admin/system-config", methods=["GET"])
@require_permission("admin:user_manage")
def api_list_system_configs():
    try:
        from backend.services.tool_io_service import list_system_configs

        return jsonify(list_system_configs())
    except Exception as exc:
        logger.error("failed to list system configs: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@system_config_bp.route("/api/admin/system-config/<config_key>", methods=["GET"])
@require_permission("admin:user_manage")
def api_get_system_config(config_key):
    try:
        from backend.services.tool_io_service import get_system_config

        result = get_system_config(config_key)
        return jsonify(result) if result.get("success") else (jsonify(result), 404)
    except Exception as exc:
        logger.error("failed to get system config %s: %s", config_key, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@system_config_bp.route("/api/admin/system-config/<config_key>", methods=["PUT"])
@require_permission("admin:user_manage")
def api_update_system_config(config_key):
    try:
        from backend.services.tool_io_service import update_system_config

        result = update_system_config(config_key, get_json_dict(required=True), current_user=get_authenticated_user())
        return jsonify(result)
    except ValueError as exc:
        return validation_error(str(exc))
    except Exception as exc:
        logger.error("failed to update system config %s: %s", config_key, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# Feature flag endpoints
@system_config_bp.route("/api/admin/feature-flags", methods=["GET"])
@require_permission("admin:user_manage")
def api_list_feature_flags():
    try:
        from backend.services.feature_flag_service import get_feature_flag_service

        service = get_feature_flag_service()
        flags = service.get_all_flags()
        return jsonify({"success": True, "data": flags})
    except Exception as exc:
        logger.error("failed to list feature flags: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@system_config_bp.route("/api/admin/feature-flags/<flag_key>", methods=["PUT"])
@require_permission("admin:user_manage")
def api_update_feature_flag(flag_key):
    try:
        from backend.services.feature_flag_service import get_feature_flag_service

        service = get_feature_flag_service()
        payload = get_json_dict(required=True)
        value = payload.get("value")
        operator_id = get_authenticated_user().get("user_id", "unknown") if get_authenticated_user() else "unknown"
        success = service.set_flag(flag_key, value, operator_id)
        if success:
            return jsonify({"success": True, "data": {"config_key": flag_key, "config_value": value}})
        return jsonify({"success": False, "error": "Failed to update feature flag"}), 500
    except Exception as exc:
        logger.error("failed to update feature flag %s: %s", flag_key, exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@system_config_bp.route("/api/feature-flags/<flag_key>/enabled", methods=["GET"])
def api_is_feature_flag_enabled(flag_key):
    try:
        from backend.services.feature_flag_service import get_feature_flag_service

        service = get_feature_flag_service()
        enabled = service.is_enabled(flag_key)
        return jsonify({"success": True, "data": {"config_key": flag_key, "enabled": enabled}})
    except Exception as exc:
        logger.error("failed to check feature flag %s: %s", flag_key, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
