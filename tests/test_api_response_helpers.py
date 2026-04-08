import sys
import types

from flask import Flask

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.utils.response import error_response, result_response, success_response


def test_success_response_includes_canonical_data_and_compat_fields():
    app = Flask(__name__)
    with app.app_context():
        response, status_code = success_response({"token": "signed-token"}, token="signed-token")

    assert status_code == 200
    assert response.get_json() == {
        "success": True,
        "data": {"token": "signed-token"},
        "token": "signed-token",
    }


def test_error_response_uses_structured_error_body():
    app = Flask(__name__)
    with app.app_context():
        response, status_code = error_response(
            "order not found",
            error_code="NOT_FOUND",
            status_code=404,
            details={"order_no": "IO-001"},
        )

    assert status_code == 404
    assert response.get_json() == {
        "success": False,
        "error": {
            "code": "NOT_FOUND",
            "message": "order not found",
            "details": {"order_no": "IO-001"},
        },
    }


def test_result_response_wraps_success_payload_without_existing_data_key():
    app = Flask(__name__)
    with app.app_context():
        response, status_code = result_response({"success": True, "notify_id": 12, "wechat_text": "hi"})

    assert status_code == 200
    assert response.get_json() == {
        "success": True,
        "data": {"notify_id": 12, "wechat_text": "hi"},
        "notify_id": 12,
        "wechat_text": "hi",
    }


def test_result_response_maps_error_status_and_preserves_extra_fields():
    app = Flask(__name__)
    with app.app_context():
        response, status_code = result_response(
            {"success": False, "error": "order not found", "data": []},
            error_status_map={"order not found": 404},
        )

    assert status_code == 404
    assert response.get_json() == {
        "success": False,
        "error": {
            "code": "NOT_FOUND",
            "message": "order not found",
        },
        "data": [],
    }
