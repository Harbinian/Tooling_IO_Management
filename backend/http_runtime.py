# -*- coding: utf-8 -*-
"""HTTP runtime helpers for API CORS and global error handling."""

from __future__ import annotations

import logging
from typing import Iterable

from flask import Flask, request
from flask_limiter.errors import RateLimitExceeded
from werkzeug.exceptions import HTTPException

from backend.routes.common import json_error

try:
    from flask_cors import CORS
except ImportError:  # pragma: no cover - exercised only when dependency is absent
    CORS = None


def _normalize_cors_origins(configured_origins: Iterable[str]) -> tuple[str, ...]:
    return tuple(str(origin).strip() for origin in configured_origins if str(origin).strip())


def resolve_api_cors_origins(*, flask_env: str, configured_origins: Iterable[str]) -> str | tuple[str, ...]:
    normalized_origins = _normalize_cors_origins(configured_origins)
    if flask_env != "production":
        return "*"
    return normalized_origins


def _apply_fallback_cors(app: Flask, origins: str | tuple[str, ...]) -> None:
    allowed_methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    allowed_headers = "Authorization, Content-Type"

    @app.after_request
    def add_api_cors_headers(response):
        if not request.path.startswith("/api/"):
            return response

        origin = (request.headers.get("Origin") or "").strip()
        allow_any_origin = origins == "*"
        allow_specific_origin = bool(origin) and isinstance(origins, tuple) and origin in origins
        if not (allow_any_origin or allow_specific_origin):
            return response

        response.headers["Access-Control-Allow-Origin"] = "*" if allow_any_origin else origin
        response.headers["Access-Control-Allow-Methods"] = allowed_methods
        response.headers["Access-Control-Allow-Headers"] = allowed_headers
        response.headers["Access-Control-Max-Age"] = "600"
        if not allow_any_origin:
            response.headers["Vary"] = "Origin"
        return response


def configure_api_cors(app: Flask, *, flask_env: str, configured_origins: Iterable[str]) -> str | tuple[str, ...]:
    origins = resolve_api_cors_origins(flask_env=flask_env, configured_origins=configured_origins)
    if CORS is not None:
        CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=False)
    else:
        app.logger.warning("flask-cors is not installed; using fallback API CORS headers")
        _apply_fallback_cors(app, origins)

    if flask_env == "production" and not origins:
        app.logger.warning("CORS_ORIGINS is empty in production; cross-origin API access is disabled")
    return origins


def _is_api_request() -> bool:
    return request.path.startswith("/api/")


def _http_error_code(exc: HTTPException) -> str:
    if exc.code == 404:
        return "NOT_FOUND"
    if exc.code == 405:
        return "METHOD_NOT_ALLOWED"
    if exc.code == 400:
        return "INVALID_PARAMS"
    if exc.code == 429:
        return "RATE_LIMIT_EXCEEDED"
    return (exc.name or "HTTP_ERROR").upper().replace(" ", "_")


def register_api_error_handlers(app: Flask, logger: logging.Logger | None = None) -> None:
    runtime_logger = logger or app.logger

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(exc: RateLimitExceeded):
        if not _is_api_request():
            return exc.get_response()
        return json_error(
            str(exc.description or "rate limit exceeded"),
            status_code=429,
            code="RATE_LIMIT_EXCEEDED",
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        if not _is_api_request():
            return exc.get_response()
        return json_error(
            str(exc.description or exc.name or "HTTP error"),
            status_code=int(exc.code or 500),
            code=_http_error_code(exc),
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        from backend.services.auth_service import AuthenticationRequiredError, PermissionDeniedError

        if isinstance(exc, AuthenticationRequiredError):
            return json_error(str(exc), status_code=401, code="AUTHENTICATION_REQUIRED")
        if isinstance(exc, PermissionDeniedError):
            return json_error(str(exc), status_code=403, code="PERMISSION_DENIED")
        if isinstance(exc, ValueError):
            return json_error(str(exc), status_code=400, code="INVALID_PARAMS")

        runtime_logger.exception("unhandled exception for request %s %s", request.method, request.path)
        if _is_api_request():
            return json_error("Internal server error", status_code=500, code="INTERNAL_ERROR")
        return "Internal server error", 500
