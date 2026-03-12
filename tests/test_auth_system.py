import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services.auth_service import hash_password, verify_password
from web_server import app


class PasswordHashTests(unittest.TestCase):
    def test_hash_password_round_trip(self):
        password_hash = hash_password("admin123")

        self.assertTrue(password_hash.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password("admin123", password_hash))
        self.assertFalse(verify_password("wrong-password", password_hash))


class AuthenticationRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_login_route_returns_token_and_user(self):
        with patch(
            "backend.services.auth_service.authenticate_user",
            return_value={
                "token": "signed-token",
                "user": {
                    "user_id": "U001",
                    "display_name": "Admin",
                    "roles": [{"role_code": "sys_admin", "role_name": "System Administrator"}],
                    "permissions": ["dashboard:view"],
                },
            },
        ):
            response = self.client.post(
                "/api/auth/login",
                json={"login_name": "admin", "password": "admin123"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["token"], "signed-token")
        self.assertEqual(payload["user"]["user_id"], "U001")

    def test_auth_me_requires_bearer_token(self):
        response = self.client.get("/api/auth/me")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"]["code"], "AUTHENTICATION_REQUIRED")
        self.assertIn("authentication required", response.get_json()["error"]["message"])

    def test_auth_me_returns_permission_aware_user_context(self):
        with patch(
            "backend.services.auth_service.get_current_user_from_token",
            return_value={
                "user_id": "U001",
                "login_name": "admin",
                "display_name": "Admin",
                "roles": [{"role_code": "sys_admin", "role_name": "System Administrator", "is_primary": True}],
                "role_codes": ["sys_admin"],
                "permissions": ["dashboard:view", "admin:user_manage"],
                "default_org": {"org_id": "ORG_COMPANY", "org_name": "Example Company"},
                "current_org": {"org_id": "ORG_COMPANY", "org_name": "Example Company"},
                "role_orgs": [{"role_code": "sys_admin", "org_id": "ORG_COMPANY"}],
            },
        ):
            response = self.client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer signed-token"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["user"]
        self.assertEqual(payload["role_codes"], ["sys_admin"])
        self.assertIn("admin:user_manage", payload["permissions"])
        self.assertEqual(payload["current_org"]["org_id"], "ORG_COMPANY")

    def test_permission_guard_rejects_missing_permission(self):
        with patch(
            "backend.services.auth_service.get_current_user_from_token",
            return_value={
                "user_id": "U002",
                "display_name": "Viewer",
                "roles": [{"role_code": "auditor"}],
                "role_codes": ["auditor"],
                "permissions": ["dashboard:view"],
            },
        ):
            response = self.client.get(
                "/api/tool-io-orders",
                headers={"Authorization": "Bearer signed-token"},
            )

        self.assertEqual(response.status_code, 403)
        payload = response.get_json()["error"]
        self.assertEqual(payload["code"], "PERMISSION_DENIED")
        self.assertEqual(payload["details"]["required_permission"], "order:list")
        self.assertIn("missing required permission: order:list", payload["message"])

    def test_permission_guard_allows_authorized_request(self):
        with patch(
            "backend.services.auth_service.get_current_user_from_token",
            return_value={
                "user_id": "U003",
                "display_name": "Planner",
                "roles": [{"role_code": "planner"}],
                "role_codes": ["planner"],
                "permissions": ["order:list"],
            },
        ), patch(
            "backend.services.tool_io_service.list_orders",
            return_value={"success": True, "data": [], "total": 0, "page_no": 1, "page_size": 20},
        ):
            response = self.client.get(
                "/api/tool-io-orders",
                headers={"Authorization": "Bearer signed-token"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

    def test_permission_guard_returns_401_when_token_invalid(self):
        with patch(
            "backend.services.auth_service.get_current_user_from_token",
            side_effect=Exception("invalid authentication token"),
        ):
            response = self.client.get(
                "/api/tool-io-orders",
                headers={"Authorization": "Bearer signed-token"},
            )

        self.assertEqual(response.status_code, 401)
        payload = response.get_json()["error"]
        self.assertEqual(payload["code"], "AUTHENTICATION_REQUIRED")


if __name__ == "__main__":
    unittest.main()
