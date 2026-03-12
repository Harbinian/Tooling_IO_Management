import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services.org_service import build_org_tree, create_organization, resolve_user_org_context, update_organization


class OrgServiceTests(unittest.TestCase):
    def test_build_org_tree_nests_children(self):
        tree = build_org_tree(
            [
                {"org_id": "ORG_COMPANY", "org_name": "Company", "org_type": "company", "parent_org_id": "", "sort_no": 1, "status": "active"},
                {"org_id": "ORG_FACTORY", "org_name": "Factory", "org_type": "factory", "parent_org_id": "ORG_COMPANY", "sort_no": 2, "status": "active"},
                {"org_id": "ORG_TEAM", "org_name": "Team", "org_type": "team", "parent_org_id": "ORG_FACTORY", "sort_no": 3, "status": "active"},
            ]
        )

        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]["org_id"], "ORG_COMPANY")
        self.assertEqual(tree[0]["children"][0]["org_id"], "ORG_FACTORY")
        self.assertEqual(tree[0]["children"][0]["children"][0]["org_id"], "ORG_TEAM")

    def test_create_organization_rejects_self_parent(self):
        with patch("backend.services.org_service.ensure_org_tables"):
            with self.assertRaises(ValueError):
                create_organization(
                    {
                        "org_id": "ORG_SELF",
                        "org_name": "Self",
                        "org_type": "team",
                        "parent_org_id": "ORG_SELF",
                    }
                )

    def test_update_organization_rejects_simple_cycle(self):
        with patch("backend.services.org_service.ensure_org_tables"), patch(
            "backend.services.org_service.get_organization",
            side_effect=[
                {"org_id": "ORG_PARENT", "org_name": "Parent", "org_type": "factory", "parent_org_id": ""},
                {"org_id": "ORG_CHILD", "org_name": "Child", "org_type": "team", "parent_org_id": "ORG_PARENT"},
                {"org_id": "ORG_CHILD", "org_name": "Child", "org_type": "team", "parent_org_id": "ORG_PARENT"},
                {"org_id": "ORG_PARENT", "org_name": "Parent", "org_type": "factory", "parent_org_id": "ORG_CHILD"},
            ],
        ):
            with self.assertRaises(ValueError):
                update_organization("ORG_PARENT", {"parent_org_id": "ORG_CHILD"})

    def test_resolve_user_org_context_prefers_role_org(self):
        with patch(
            "backend.services.org_service.get_role_assignments_with_org_context",
            return_value=[
                {
                    "role_id": "ROLE_KEEPER",
                    "role_code": "keeper",
                    "role_name": "Keeper",
                    "org_id": "ORG_WAREHOUSE",
                    "org_name": "Warehouse East",
                    "org_type": "warehouse",
                    "org_status": "active",
                }
            ],
        ), patch(
            "backend.services.org_service.get_organization",
            side_effect=lambda org_id: {
                "ORG_FACTORY": {"org_id": "ORG_FACTORY", "org_name": "Factory A"},
                "ORG_WAREHOUSE": {"org_id": "ORG_WAREHOUSE", "org_name": "Warehouse East"},
            }.get(org_id),
        ):
            context = resolve_user_org_context("U_KEEPER", "ORG_FACTORY")

        self.assertEqual(context["default_org"]["org_id"], "ORG_FACTORY")
        self.assertEqual(context["current_org"]["org_id"], "ORG_WAREHOUSE")
        self.assertEqual(context["role_orgs"][0]["org_id"], "ORG_WAREHOUSE")


if __name__ == "__main__":
    unittest.main()
