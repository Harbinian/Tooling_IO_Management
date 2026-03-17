import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services.rbac_data_scope_service import (
    build_order_scope_sql,
    order_matches_scope,
    resolve_order_data_scope,
)


class RBACDataScopeServiceTests(unittest.TestCase):
    def test_resolve_order_data_scope_preserves_role_to_org_binding(self):
        user = {
            "user_id": "U001",
            "roles": [
                {"role_id": "ROLE_PLANNER", "role_code": "planner", "org_id": "ORG_FACTORY"},
                {"role_id": "ROLE_AUDITOR", "role_code": "auditor", "org_id": "ORG_GROUP"},
            ],
            "current_org": {"org_id": "ORG_CURRENT"},
            "default_org": {"org_id": "ORG_DEFAULT"},
            "role_orgs": [{"org_id": "ORG_GROUP"}],
        }

        with patch(
            "backend.services.rbac_data_scope_service.load_role_data_scopes",
            return_value=[
                {"role_id": "ROLE_PLANNER", "scope_type": "ORG"},
                {"role_id": "ROLE_AUDITOR", "scope_type": "SELF"},
            ],
        ), patch(
            "backend.services.rbac_data_scope_service.load_user_ids_for_org_ids",
            return_value=["U100", "U200"],
        ):
            scope = resolve_order_data_scope(user)

        self.assertEqual(scope["org_ids"], ["ORG_FACTORY"])
        self.assertEqual(scope["self_user_ids"], ["U001"])
        self.assertEqual(scope["assignment_scopes"][0]["org_id"], "ORG_FACTORY")
        self.assertEqual(scope["assignment_scopes"][1]["scope_types"], ["SELF"])

    def test_resolve_order_data_scope_expands_children_per_assignment(self):
        user = {
            "user_id": "U001",
            "roles": [{"role_id": "ROLE_KEEPER", "role_code": "keeper", "org_id": "ORG_PARENT"}],
            "current_org": {"org_id": "ORG_CURRENT"},
            "default_org": {"org_id": "ORG_DEFAULT"},
        }

        with patch(
            "backend.services.rbac_data_scope_service.load_role_data_scopes",
            return_value=[{"role_id": "ROLE_KEEPER", "scope_type": "ORG_AND_CHILDREN"}],
        ), patch(
            "backend.services.rbac_data_scope_service.get_descendant_org_ids",
            side_effect=lambda org_id: [org_id, f"{org_id}_CHILD"],
        ), patch(
            "backend.services.rbac_data_scope_service.load_user_ids_for_org_ids",
            return_value=["U101"],
        ):
            scope = resolve_order_data_scope(user)

        self.assertEqual(scope["org_ids"], ["ORG_PARENT", "ORG_PARENT_CHILD"])

    def test_build_order_scope_sql_filters_by_order_org_ownership(self):
        sql, params = build_order_scope_sql(
            {
                "all_access": False,
                "self_user_ids": ["U001"],
                "assigned_user_ids": ["U001"],
                "org_ids": ["ORG_FACTORY", "ORG_TEAM"],
            }
        )

        self.assertIn("发起人ID IN (?)", sql)
        self.assertIn("保管员ID IN (?)", sql)
        self.assertIn("org_idIN(?,?)", sql.replace(" ", ""))
        self.assertEqual(params, ("U001", "U001", "U001", "ORG_FACTORY", "ORG_TEAM"))

    def test_order_matches_scope_checks_order_org_ownership(self):
        scope = {
            "all_access": False,
            "self_user_ids": ["U001"],
            "assigned_user_ids": ["U002"],
            "org_ids": ["ORG_FACTORY"],
        }

        self.assertTrue(order_matches_scope({"initiator_id": "U001", "org_id": "ORG_OTHER"}, scope))
        self.assertTrue(order_matches_scope({"keeper_id": "U002", "org_id": "ORG_OTHER"}, scope))
        self.assertTrue(order_matches_scope({"org_id": "ORG_FACTORY"}, scope))
        self.assertFalse(order_matches_scope({"transport_assignee_id": "U999", "org_id": "ORG_OTHER"}, scope))

    def test_order_matches_scope_allows_keeper_to_see_submitted_same_org_without_keeper_id(self):
        scope = {
            "all_access": False,
            "self_user_ids": [],
            "assigned_user_ids": [],
            "org_ids": ["ORG_DEPT_005"],
            "user_roles": [{"role_code": "keeper"}],
            "assignment_scopes": [{"role_code": "keeper", "org_id": "ORG_DEPT_005"}],
        }

        self.assertTrue(
            order_matches_scope(
                {"order_status": "submitted", "org_id": "ORG_DEPT_005", "keeper_id": ""},
                scope,
            )
        )

    def test_order_matches_scope_does_not_expand_team_leader_visibility_for_submitted(self):
        scope = {
            "all_access": False,
            "self_user_ids": [],
            "assigned_user_ids": [],
            "org_ids": ["ORG_DEPT_005"],
            "user_roles": [{"role_code": "team_leader"}],
            "assignment_scopes": [{"role_code": "team_leader", "org_id": "ORG_DEPT_005"}],
        }

        self.assertFalse(
            order_matches_scope(
                {"order_status": "submitted", "org_id": "ORG_OTHER", "keeper_id": ""},
                scope,
            )
        )


if __name__ == "__main__":
    unittest.main()
