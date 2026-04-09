import sys
import types
import unittest
from unittest.mock import Mock
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services import rbac_service


class RBACServiceTests(unittest.TestCase):
    def test_incremental_defaults_add_team_leader_order_view_permission(self):
        db = Mock()

        rbac_service._ensure_incremental_permission_defaults(db)

        executed_sql = "\n".join(call.args[0] for call in db.execute_query.call_args_list)
        self.assertIn("ROLE_TEAM_LEADER", executed_sql)
        self.assertIn("order:view", executed_sql)

    def test_incremental_defaults_add_admin_delete_permission_for_upgraded_envs(self):
        db = Mock()

        rbac_service._ensure_incremental_permission_defaults(db)

        executed_sql = "\n".join(call.args[0] for call in db.execute_query.call_args_list)
        self.assertIn("order:delete", executed_sql)
        self.assertIn("ROLE_SYS_ADMIN", executed_sql)

    def test_incremental_defaults_create_notification_permissions_for_upgraded_envs(self):
        db = Mock()

        rbac_service._ensure_incremental_permission_defaults(db)

        executed_sql = "\n".join(call.args[0] for call in db.execute_query.call_args_list)
        self.assertIn("INSERT INTO sys_permission", executed_sql)
        self.assertIn("ROLE_KEEPER", executed_sql)
        self.assertIn("notification:view", executed_sql)
        self.assertIn("notification:create", executed_sql)
        self.assertIn("notification:send_feishu", executed_sql)

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
