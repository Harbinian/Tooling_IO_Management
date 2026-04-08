import sys
import types
from unittest.mock import Mock

import pytest
from flask import Flask
from werkzeug.exceptions import NotFound

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.http_runtime import configure_api_cors, register_api_error_handlers, resolve_api_cors_origins
from backend.services.auth_service import AuthenticationRequiredError


def create_app(*, flask_env="default", configured_origins=()):
    app = Flask(__name__)
    configure_api_cors(app, flask_env=flask_env, configured_origins=configured_origins)
    register_api_error_handlers(app, Mock())

    @app.route("/api/boom")
    def api_boom():
        raise RuntimeError("boom")

    @app.route("/api/value-error")
    def api_value_error():
        raise ValueError("bad payload")

    @app.route("/api/auth-required")
    def api_auth_required():
        raise AuthenticationRequiredError("authentication required")

    @app.route("/page-boom")
    def page_boom():
        raise RuntimeError("boom")

    return app


def test_resolve_api_cors_origins_uses_wildcard_outside_production():
    assert resolve_api_cors_origins(flask_env="development", configured_origins=("https://example.com",)) == "*"


def test_resolve_api_cors_origins_uses_configured_values_in_production():
    assert resolve_api_cors_origins(
        flask_env="production",
        configured_origins=(" https://a.example.com ", "https://b.example.com"),
    ) == ("https://a.example.com", "https://b.example.com")


def test_api_runtime_returns_uniform_internal_error_payload():
    client = create_app().test_client()

    response = client.get("/api/boom")

    assert response.status_code == 500
    assert response.get_json() == {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Internal server error",
        },
    }


def test_api_runtime_maps_value_error_to_invalid_params():
    client = create_app().test_client()

    response = client.get("/api/value-error")

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "INVALID_PARAMS"
    assert response.get_json()["error"]["message"] == "bad payload"


def test_api_runtime_maps_authentication_error():
    client = create_app().test_client()

    response = client.get("/api/auth-required")

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_api_runtime_maps_http_exception_to_json_for_api_routes():
    app = Flask(__name__)
    configure_api_cors(app, flask_env="default", configured_origins=())
    register_api_error_handlers(app, Mock())

    @app.route("/api/missing")
    def api_missing():
        raise NotFound("missing route resource")

    response = app.test_client().get("/api/missing")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"


def test_non_api_runtime_keeps_plain_text_500_response():
    client = create_app().test_client()

    response = client.get("/page-boom")

    assert response.status_code == 500
    assert response.get_data(as_text=True) == "Internal server error"


def test_api_cors_allows_dev_origin_for_api_routes():
    client = create_app().test_client()

    response = client.options(
        "/api/boom",
        headers={
            "Origin": "http://localhost:8150",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_api_cors_allows_only_configured_origin_in_production():
    client = create_app(
        flask_env="production",
        configured_origins=("https://frontend.example.com",),
    ).test_client()

    allowed = client.options(
        "/api/boom",
        headers={
            "Origin": "https://frontend.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    blocked = client.options(
        "/api/boom",
        headers={
            "Origin": "https://blocked.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.headers["Access-Control-Allow-Origin"] == "https://frontend.example.com"
    assert "Access-Control-Allow-Origin" not in blocked.headers
