# -*- coding: utf-8 -*-
"""Shared API response helpers."""

from __future__ import annotations

from typing import Any, Mapping

from flask import jsonify


def success_response(data: Any = None, *, status_code: int = 200, **extra: Any):
    """Return a uniform success payload."""
    payload = {"success": True, "data": data}
    payload.update(extra)
    return jsonify(payload), status_code


def error_response(
    message: str,
    *,
    error_code: str = "INVALID_REQUEST",
    status_code: int = 400,
    details: Any = None,
    **extra: Any,
):
    """Return a uniform error payload."""
    payload = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    payload.update(extra)
    return jsonify(payload), status_code


def result_response(
    result: Mapping[str, Any] | None,
    *,
    success_status: int = 200,
    default_error_status: int = 400,
    default_error_code: str = "INVALID_REQUEST",
    error_status_map: Mapping[str, int] | None = None,
):
    """Convert a service-layer result dict into a uniform Flask response."""
    normalized = dict(result or {})
    if normalized.get("success"):
        normalized.pop("success", None)
        data = normalized.pop("data", None)
        if data is None and normalized:
            data = dict(normalized)
        return success_response(data, status_code=success_status, **normalized)

    normalized.pop("success", None)
    error_value = normalized.pop("error", None)
    message_value = normalized.pop("message", None)
    details = normalized.pop("details", None)
    error_code = str(normalized.pop("error_code", None) or default_error_code)

    if isinstance(error_value, Mapping):
        details = error_value.get("details", details)
        error_code = str(error_value.get("code") or error_code)
        message = str(error_value.get("message") or message_value or "request failed")
    else:
        message = str(error_value or message_value or "request failed")

    status_code = _resolve_error_status(
        message=message,
        error_code=error_code,
        error_status_map=error_status_map,
        default_error_status=default_error_status,
    )
    resolved_error_code = _resolve_error_code(
        current_code=error_code,
        status_code=status_code,
        default_error_code=default_error_code,
    )
    return error_response(
        message,
        error_code=resolved_error_code,
        status_code=status_code,
        details=details,
        **normalized,
    )


def _resolve_error_status(
    *,
    message: str,
    error_code: str,
    error_status_map: Mapping[str, int] | None,
    default_error_status: int,
) -> int:
    if not error_status_map:
        return default_error_status
    if error_code in error_status_map:
        return error_status_map[error_code]
    if message in error_status_map:
        return error_status_map[message]
    return default_error_status


def _resolve_error_code(*, current_code: str, status_code: int, default_error_code: str) -> str:
    normalized = str(current_code or "").strip() or default_error_code
    if normalized != default_error_code:
        return normalized
    if status_code == 401:
        return "AUTHENTICATION_REQUIRED"
    if status_code == 403:
        return "PERMISSION_DENIED"
    if status_code == 404:
        return "NOT_FOUND"
    if status_code == 409:
        return "CONFLICT"
    if status_code >= 500:
        return "INTERNAL_ERROR"
    return normalized
