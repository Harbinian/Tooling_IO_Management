import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services import rbac_service


class RBACServiceTests(unittest.TestCase):
    def test_load_user_roles_returns_normalized_assignments(self):
        with patch("backend.services.org_service.ensure_org_tables"), patch(
            "backend.services.rbac_service.DatabaseManager.execute_query",
            return_value=[
                {
                    "role_id": "ROLE_KEEPER",
                    "role_code": "keeper",
                    "role_name": "Keeper",
                    "org_id": "ORG_WAREHOUSE",
                    "org_name": "Warehouse East",
                    "org_type": "warehouse",
                    "org_status": "active",
                    "is_primary": 1,
                }
            ],
        ):
            roles = rbac_service.load_user_roles("U001")

        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0]["role_code"], "keeper")
        self.assertTrue(roles[0]["is_primary"])

    def test_build_permission_context_merges_distinct_permissions(self):
        roles = [
            {"role_id": "ROLE_KEEPER", "role_code": "keeper"},
            {"role_id": "ROLE_AUDITOR", "role_code": "auditor"},
        ]
        with patch(
            "backend.services.rbac_service.DatabaseManager.execute_query",
            return_value=[
                {"permission_code": "dashboard:view"},
                {"permission_code": "notification:view"},
                {"permission_code": "order:list"},
            ],
        ):
            context = rbac_service.build_permission_context("U001", roles)

        self.assertEqual(context["role_codes"], ["keeper", "auditor"])
        self.assertEqual(
            context["permissions"],
            ["dashboard:view", "notification:view", "order:list"],
        )

    def test_has_permission_handles_missing_user(self):
        self.assertFalse(rbac_service.has_permission(None, "order:list"))
        self.assertTrue(rbac_service.has_permission({"permissions": ["order:list"]}, "order:list"))


if __name__ == "__main__":
    unittest.main()
