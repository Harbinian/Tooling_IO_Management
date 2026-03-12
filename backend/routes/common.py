# -*- coding: utf-8 -*-
"""Shared Flask route helpers."""

from __future__ import annotations

from functools import wraps

from flask import g, jsonify, request


def parse_positive_int_arg(arg_name: str, default: int) -> int:
    raw_value = request.args.get(arg_name, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{arg_name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{arg_name} must be greater than 0")
    return value


def get_json_dict(required: bool = False):
    data = request.get_json(silent=True)
    if required and data is None:
        raise ValueError("request body must be a JSON object")
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")
    return data


def validation_error(message: str):
    return jsonify({"success": False, "error": message}), 400


def json_error(message: str, *, status_code: int, code: str, details=None):
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), status_code


def extract_bearer_token():
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header:
        return ""
    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return ""
    return parts[1].strip()


def set_request_user_context(user):
    g.current_user = user
    request_ctx = request._get_current_object()
    request_ctx.current_user = user
    request_ctx.user_id = user.get("user_id")
    request_ctx.roles = [role.get("role_code") for role in user.get("roles", [])]
    request_ctx.role_codes = user.get("role_codes", request_ctx.roles)
    request_ctx.permissions = user.get("permissions", [])
    request_ctx.current_org = user.get("current_org")
    request_ctx.current_org_id = (user.get("current_org") or {}).get("org_id", "")
    request_ctx.default_org = user.get("default_org")
    request_ctx.default_org_id = (user.get("default_org") or {}).get("org_id", user.get("default_org_id", ""))


def get_authenticated_user():
    user = getattr(g, "current_user", None)
    if not user:
        from backend.services.auth_service import AuthenticationRequiredError

        raise AuthenticationRequiredError("authentication required")
    return user


def build_actor_payload(data, *, role_fallback="initiator"):
    user = get_authenticated_user()
    data["operator_id"] = user.get("user_id", "")
    data["operator_name"] = user.get("display_name", "")
    data["operator_role"] = data.get("operator_role") or role_fallback
    return data


def build_initiator_payload(data):
    user = get_authenticated_user()
    data["initiator_id"] = user.get("user_id", "")
    data["initiator_name"] = user.get("display_name", "")
    data["initiator_role"] = data.get("initiator_role") or "initiator"
    return data


def build_keeper_payload(data):
    user = get_authenticated_user()
    data["keeper_id"] = user.get("user_id", "")
    data["keeper_name"] = user.get("display_name", "")
    data["operator_id"] = user.get("user_id", "")
    data["operator_name"] = user.get("display_name", "")
    data["operator_role"] = data.get("operator_role") or "keeper"
    return data


def require_permission(permission_code):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from backend.services.auth_service import (
                AuthenticationRequiredError,
                PermissionDeniedError,
                require_permission as ensure_permission,
            )

            try:
                user = get_authenticated_user()
                ensure_permission(user, permission_code)
            except AuthenticationRequiredError as exc:
                return json_error(str(exc), status_code=401, code="AUTHENTICATION_REQUIRED")
            except PermissionDeniedError as exc:
                return json_error(
                    str(exc),
                    status_code=403,
                    code="PERMISSION_DENIED",
                    details={"required_permission": permission_code},
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from backend.services.auth_service import AuthenticationRequiredError

        try:
            get_authenticated_user()
        except AuthenticationRequiredError as exc:
            return json_error(str(exc), status_code=401, code="AUTHENTICATION_REQUIRED")
        return func(*args, **kwargs)

    return wrapper


def register_request_identity_hook(app, logger):
    @app.before_request
    def load_request_identity():
        g.current_user = None
        token = extract_bearer_token()
        if not token:
            return None
        try:
            from backend.services.auth_service import get_current_user_from_token

            user = get_current_user_from_token(token)
            set_request_user_context(user)
        except Exception as exc:
            logger.warning("failed to resolve request identity: %s", exc)
            g.current_user = None
        return None

