import sys
import types
from contextlib import ExitStack
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from web_server import app


@dataclass(frozen=True)
class EndpointCase:
    name: str
    method: str
    path: str
    permission: str
    patch_target: str
    patch_value: Any
    expected_status: int = 200
    json_body: dict | None = None


PROTECTED_ENDPOINTS = [
    EndpointCase(
        name="order_list",
        method="GET",
        path="/api/tool-io-orders",
        permission="order:list",
        patch_target="backend.services.tool_io_service.list_orders",
        patch_value={"success": True, "data": [], "total": 0, "page_no": 1, "page_size": 20},
    ),
    EndpointCase(
        name="order_create",
        method="POST",
        path="/api/tool-io-orders",
        permission="order:create",
        patch_target="backend.services.tool_io_service.create_order",
        patch_value={"success": True, "order_no": "ORD-001"},
        expected_status=201,
        json_body={},
    ),
    EndpointCase(
        name="order_detail",
        method="GET",
        path="/api/tool-io-orders/ORD-001",
        permission="order:view",
        patch_target="backend.services.tool_io_service.get_order_detail",
        patch_value={"order_no": "ORD-001", "items": []},
    ),
    EndpointCase(
        name="order_submit",
        method="POST",
        path="/api/tool-io-orders/ORD-001/submit",
        permission="order:submit",
        patch_target="backend.services.tool_io_service.submit_order",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="keeper_confirm",
        method="POST",
        path="/api/tool-io-orders/ORD-001/keeper-confirm",
        permission="order:keeper_confirm",
        patch_target="backend.services.tool_io_service.keeper_confirm",
        patch_value={"success": True},
        json_body={"items": []},
    ),
    EndpointCase(
        name="final_confirm",
        method="POST",
        path="/api/tool-io-orders/ORD-001/final-confirm",
        permission="order:final_confirm",
        patch_target="backend.services.tool_io_service.final_confirm",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="final_confirm_availability",
        method="GET",
        path="/api/tool-io-orders/ORD-001/final-confirm-availability",
        permission="order:view",
        patch_target="backend.services.tool_io_service.get_final_confirm_availability",
        patch_value={"success": True, "available": True, "order_type": "outbound"},
    ),
    EndpointCase(
        name="assign_transport",
        method="POST",
        path="/api/tool-io-orders/ORD-001/assign-transport",
        permission="order:keeper_confirm",
        patch_target="backend.services.tool_io_service.assign_transport",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="transport_start",
        method="POST",
        path="/api/tool-io-orders/ORD-001/transport-start",
        permission="order:transport_execute",
        patch_target="backend.services.tool_io_service.start_transport",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="transport_complete",
        method="POST",
        path="/api/tool-io-orders/ORD-001/transport-complete",
        permission="order:transport_execute",
        patch_target="backend.services.tool_io_service.complete_transport",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="transport_issues",
        method="GET",
        path="/api/tool-io-orders/ORD-001/transport-issues",
        permission="order:view",
        patch_target="backend.services.transport_issue_service.get_transport_issues",
        patch_value={"success": True, "data": []},
    ),
    EndpointCase(
        name="order_reject",
        method="POST",
        path="/api/tool-io-orders/ORD-001/reject",
        permission="order:cancel",
        patch_target="backend.services.tool_io_service.reject_order",
        patch_value={"success": True},
        json_body={"reject_reason": "out of scope"},
    ),
    EndpointCase(
        name="order_cancel",
        method="POST",
        path="/api/tool-io-orders/ORD-001/cancel",
        permission="order:cancel",
        patch_target="backend.services.tool_io_service.cancel_order",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="order_logs",
        method="GET",
        path="/api/tool-io-orders/ORD-001/logs",
        permission="order:view",
        patch_target="backend.services.tool_io_service.get_order_logs",
        patch_value={"success": True, "data": []},
    ),
    EndpointCase(
        name="notification_records",
        method="GET",
        path="/api/tool-io-orders/ORD-001/notification-records",
        permission="notification:view",
        patch_target="backend.services.tool_io_service.get_notification_records",
        patch_value={"success": True, "data": []},
    ),
    EndpointCase(
        name="notifications_list",
        method="GET",
        path="/api/notifications",
        permission="notification:view",
        patch_target="backend.services.tool_io_service.get_current_user_notifications",
        patch_value={"success": True, "data": []},
    ),
    EndpointCase(
        name="notification_mark_read",
        method="POST",
        path="/api/notifications/1/read",
        permission="notification:view",
        patch_target="backend.services.tool_io_service.mark_current_user_notification_read",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="pending_keeper",
        method="GET",
        path="/api/tool-io-orders/pending-keeper",
        permission="order:keeper_confirm",
        patch_target="backend.services.tool_io_service.get_pending_keeper_list",
        patch_value=[],
    ),
    EndpointCase(
        name="generate_keeper_text",
        method="GET",
        path="/api/tool-io-orders/ORD-001/generate-keeper-text",
        permission="notification:create",
        patch_target="backend.services.tool_io_service.generate_keeper_text",
        patch_value={"success": True, "text": "ok"},
    ),
    EndpointCase(
        name="generate_transport_text",
        method="GET",
        path="/api/tool-io-orders/ORD-001/generate-transport-text",
        permission="notification:create",
        patch_target="backend.services.tool_io_service.generate_transport_text",
        patch_value={"success": True, "text": "ok"},
    ),
    EndpointCase(
        name="notify_transport",
        method="POST",
        path="/api/tool-io-orders/ORD-001/notify-transport",
        permission="notification:send_feishu",
        patch_target="backend.services.tool_io_service.notify_transport",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="notify_keeper",
        method="POST",
        path="/api/tool-io-orders/ORD-001/notify-keeper",
        permission="notification:send_feishu",
        patch_target="backend.services.tool_io_service.notify_keeper",
        patch_value={"success": True},
        json_body={},
    ),
    EndpointCase(
        name="admin_roles",
        method="GET",
        path="/api/admin/roles",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.list_roles",
        patch_value=[],
    ),
    EndpointCase(
        name="admin_users_list",
        method="GET",
        path="/api/admin/users",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.list_users",
        patch_value=[],
    ),
    EndpointCase(
        name="admin_user_detail",
        method="GET",
        path="/api/admin/users/U001",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.get_user_detail",
        patch_value={"user_id": "U001"},
    ),
    EndpointCase(
        name="admin_user_create",
        method="POST",
        path="/api/admin/users",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.create_user",
        patch_value={"user_id": "U001"},
        json_body={"login_name": "demo", "display_name": "Demo"},
    ),
    EndpointCase(
        name="admin_user_update",
        method="PUT",
        path="/api/admin/users/U001",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.update_user",
        patch_value={"user_id": "U001"},
        json_body={"display_name": "Updated"},
    ),
    EndpointCase(
        name="admin_assign_roles",
        method="PUT",
        path="/api/admin/users/U001/roles",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.assign_user_roles",
        patch_value={"user_id": "U001"},
        json_body={"role_ids": ["ROLE_KEEPER"], "org_id": "ORG-1"},
    ),
    EndpointCase(
        name="admin_update_status",
        method="PUT",
        path="/api/admin/users/U001/status",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.update_user_status",
        patch_value={"user_id": "U001"},
        json_body={"status": "active"},
    ),
    EndpointCase(
        name="admin_reset_password",
        method="PUT",
        path="/api/admin/users/U001/password-reset",
        permission="admin:user_manage",
        patch_target="backend.routes.admin_user_routes.reset_user_password",
        patch_value={"user_id": "U001"},
        json_body={"new_password": "secret123"},
    ),
    EndpointCase(
        name="system_config_list",
        method="GET",
        path="/api/admin/system-config",
        permission="admin:user_manage",
        patch_target="backend.services.tool_io_service.list_system_configs",
        patch_value={"success": True, "data": []},
    ),
    EndpointCase(
        name="system_config_detail",
        method="GET",
        path="/api/admin/system-config/mpl_enabled",
        permission="admin:user_manage",
        patch_target="backend.services.tool_io_service.get_system_config",
        patch_value={"success": True, "data": {"config_key": "mpl_enabled", "config_value": "false"}},
    ),
    EndpointCase(
        name="system_config_update",
        method="PUT",
        path="/api/admin/system-config/mpl_enabled",
        permission="admin:user_manage",
        patch_target="backend.services.tool_io_service.update_system_config",
        patch_value={"success": True, "data": {"config_key": "mpl_enabled", "config_value": "true"}},
        json_body={"config_value": "true"},
    ),
    EndpointCase(
        name="org_list",
        method="GET",
        path="/api/orgs",
        permission="dashboard:view",
        patch_target="backend.services.org_service.list_organizations",
        patch_value=[],
    ),
    EndpointCase(
        name="org_tree",
        method="GET",
        path="/api/orgs/tree",
        permission="dashboard:view",
        patch_target="backend.services.org_service.get_org_tree",
        patch_value=[],
    ),
    EndpointCase(
        name="org_detail",
        method="GET",
        path="/api/orgs/ORG-1",
        permission="dashboard:view",
        patch_target="backend.services.org_service.get_organization",
        patch_value={"org_id": "ORG-1"},
    ),
    EndpointCase(
        name="org_create",
        method="POST",
        path="/api/orgs",
        permission="admin:user_manage",
        patch_target="backend.services.org_service.create_organization",
        patch_value={"success": True, "org_id": "ORG-1"},
        expected_status=201,
        json_body={"org_name": "Ops"},
    ),
    EndpointCase(
        name="org_update",
        method="PUT",
        path="/api/orgs/ORG-1",
        permission="admin:user_manage",
        patch_target="backend.services.org_service.update_organization",
        patch_value={"success": True, "org_id": "ORG-1"},
        json_body={"org_name": "Ops 2"},
    ),
    EndpointCase(
        name="tool_search",
        method="GET",
        path="/api/tools/search",
        permission="tool:search",
        patch_target="backend.services.tool_io_service.search_tool_inventory",
        patch_value={"success": True, "data": [], "total": 0},
    ),
    EndpointCase(
        name="tool_batch_query",
        method="POST",
        path="/api/tools/batch-query",
        permission="tool:view",
        patch_target="backend.services.tool_io_service.batch_query_tools",
        patch_value={"success": True, "data": []},
        json_body={"tool_codes": ["TOOL-1"]},
    ),
    EndpointCase(
        name="dashboard_metrics",
        method="GET",
        path="/api/dashboard/metrics",
        permission="order:list",
        patch_target="backend.services.tool_io_service.get_dashboard_stats",
        patch_value={"success": True, "data": {}},
    ),
    EndpointCase(
        name="recent_errors",
        method="GET",
        path="/api/system/diagnostics/recent-errors",
        permission="admin:user_manage",
        patch_target="backend.services.tool_io_runtime.get_recent_operation_errors",
        patch_value=[],
    ),
    EndpointCase(
        name="notification_failures",
        method="GET",
        path="/api/system/diagnostics/notification-failures",
        permission="admin:user_manage",
        patch_target="backend.services.tool_io_runtime.get_recent_notification_failures",
        patch_value=[],
    ),
    EndpointCase(
        name="db_test",
        method="GET",
        path="/api/db/test",
        permission="dashboard:view",
        patch_target="database.test_db_connection",
        patch_value=(True, "ok"),
    ),
]


def make_user(*permissions: str, role_code: str = "tester") -> dict:
    return {
        "user_id": f"U_{role_code.upper()}",
        "login_name": role_code,
        "display_name": role_code.replace("_", " ").title(),
        "roles": [{"role_code": role_code, "role_name": role_code.replace("_", " ").title()}],
        "role_codes": [role_code],
        "permissions": list(permissions),
        "current_org": {"org_id": "ORG-1", "org_name": "Org 1"},
        "default_org": {"org_id": "ORG-1", "org_name": "Org 1"},
    }


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def request_endpoint(client, case: EndpointCase, *, user: dict | None = None, side_effect=None):
    headers = {}
    if user is not None:
        headers["Authorization"] = "Bearer signed-token"

    with ExitStack() as stack:
        if user is not None:
            stack.enter_context(
                patch("backend.services.auth_service.get_current_user_from_token", return_value=user)
            )
        if side_effect is not None:
            stack.enter_context(patch(case.patch_target, side_effect=side_effect))
        else:
            stack.enter_context(patch(case.patch_target, return_value=case.patch_value))
        return client.open(case.path, method=case.method, json=case.json_body, headers=headers)


@pytest.mark.parametrize("case", PROTECTED_ENDPOINTS, ids=lambda case: case.name)
def test_protected_endpoints_require_authentication(client, case: EndpointCase):
    response = client.open(case.path, method=case.method, json=case.json_body)

    assert response.status_code == 401
    payload = response.get_json()["error"]
    assert payload["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.parametrize("case", PROTECTED_ENDPOINTS, ids=lambda case: case.name)
def test_protected_endpoints_reject_wrong_permission(client, case: EndpointCase):
    response = request_endpoint(client, case, user=make_user(role_code="auditor"))

    assert response.status_code == 403
    payload = response.get_json()["error"]
    assert payload["code"] == "PERMISSION_DENIED"
    assert payload["details"]["required_permission"] == case.permission


@pytest.mark.parametrize("case", PROTECTED_ENDPOINTS, ids=lambda case: case.name)
def test_protected_endpoints_allow_authorized_user(client, case: EndpointCase):
    response = request_endpoint(client, case, user=make_user(case.permission, role_code="sys_admin"))

    assert response.status_code == case.expected_status


def test_order_create_allows_team_leader_but_rejects_keeper(client):
    case = next(item for item in PROTECTED_ENDPOINTS if item.name == "order_create")

    allowed = request_endpoint(client, case, user=make_user("order:create", role_code="team_leader"))
    rejected = request_endpoint(client, case, user=make_user("order:keeper_confirm", role_code="keeper"))

    assert allowed.status_code == 201
    assert rejected.status_code == 403


def test_keeper_confirm_allows_keeper_but_rejects_team_leader(client):
    case = next(item for item in PROTECTED_ENDPOINTS if item.name == "keeper_confirm")

    allowed = request_endpoint(client, case, user=make_user("order:keeper_confirm", role_code="keeper"))
    rejected = request_endpoint(client, case, user=make_user("order:create", role_code="team_leader"))

    assert allowed.status_code == 200
    assert rejected.status_code == 403


@pytest.mark.parametrize("endpoint_name", ["assign_transport", "transport_start", "transport_complete"])
def test_transport_endpoints_allow_keeper_transport_permissions(endpoint_name: str, client):
    case = next(item for item in PROTECTED_ENDPOINTS if item.name == endpoint_name)

    allowed = request_endpoint(
        client,
        case,
        user=make_user(case.permission, role_code="keeper"),
    )
    rejected = request_endpoint(
        client,
        case,
        user=make_user("order:view", role_code="team_leader"),
    )

    assert allowed.status_code == case.expected_status
    assert rejected.status_code == 403


@pytest.mark.parametrize(
    ("payload", "expected_role"),
    [
        ({"operator_role": "initiator"}, "initiator"),
        ({"operator_role": "keeper"}, "keeper"),
    ],
)
def test_final_confirm_endpoint_preserves_role_specific_payload(payload: dict, expected_role: str, client):
    case = next(item for item in PROTECTED_ENDPOINTS if item.name == "final_confirm")
    captured = {}

    def fake_final_confirm(order_no, request_payload, current_user=None):
        captured["order_no"] = order_no
        captured["operator_role"] = request_payload.get("operator_role")
        return {"success": True}

    response = request_endpoint(
        client,
        EndpointCase(**{**case.__dict__, "json_body": payload}),
        user=make_user("order:final_confirm", role_code="sys_admin"),
        side_effect=fake_final_confirm,
    )

    assert response.status_code == 200
    assert captured["order_no"] == "ORD-001"
    assert captured["operator_role"] == expected_role


def test_admin_endpoints_only_allow_admin_permission(client):
    case = next(item for item in PROTECTED_ENDPOINTS if item.name == "admin_users_list")

    allowed = request_endpoint(client, case, user=make_user("admin:user_manage", role_code="sys_admin"))
    rejected = request_endpoint(client, case, user=make_user("dashboard:view", role_code="keeper"))

    assert allowed.status_code == 200
    assert rejected.status_code == 403


def test_public_health_endpoints_are_intentionally_unprotected(client):
    # These endpoints are intentionally public. They were scanned during the stage 302
    # RBAC audit and should remain outside permission enforcement.
    with patch("database.test_db_connection", return_value=(True, "ok")):
        health_response = client.get("/api/health")
        db_test_response = client.get("/api/system/health")

    assert health_response.status_code == 200
    assert db_test_response.status_code in {200, 500}
