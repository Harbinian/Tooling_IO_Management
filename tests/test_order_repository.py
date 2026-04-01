import sys
import types
import unittest
from unittest.mock import Mock, patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))

from backend.database.repositories.order_repository import OrderRepository


class OrderRepositoryDeleteTests(unittest.TestCase):
    def test_delete_order_allows_non_draft_and_cleans_up_dependents(self):
        db = Mock()
        db.execute_query.side_effect = [
            [{"order_status": "submitted"}],
            None,
            None,
            None,
            None,
        ]

        repo = OrderRepository(db_manager=db)
        repo.add_tool_io_log = Mock(return_value=True)

        result = repo.delete_order(
            "ORD-001",
            operator_id="U_ADMIN",
            operator_name="Admin",
            operator_role="sys_admin",
        )

        self.assertEqual(result, {"success": True})
        executed_sql = "\n".join(call.args[0] for call in db.execute_query.call_args_list)
        self.assertIn("DELETE FROM [tool_io_order_item]", executed_sql)
        self.assertIn("DELETE FROM [tool_io_operation_log]", executed_sql)
        self.assertIn("DELETE FROM [tool_io_notification]", executed_sql)
        self.assertIn("UPDATE [tool_io_order] SET", executed_sql)
        repo.add_tool_io_log.assert_called_once()
        logged = repo.add_tool_io_log.call_args.args[0]
        self.assertEqual(logged["before_status"], "submitted")
        self.assertEqual(logged["after_status"], "deleted")


class OrderRepositoryCreateWarningTests(unittest.TestCase):
    @patch("backend.database.services.order_service.generate_order_no_atomic", return_value="TO-OUT-20260323-001")
    def test_create_order_returns_warning_when_tools_exist_in_other_drafts(
        self,
        _generate_order_no,
    ):
        db = Mock()

        def execute_query_side_effect(sql, params=None, fetch=True):
            sql_text = str(sql or "")
            if "AS tool_code" in sql_text and "Tooling_ID_Main" in sql_text:
                return [
                    {
                        "tool_code": "T000001",
                        "tool_name": "Tool A",
                        "drawing_no": "D-01",
                        "spec_model": "M1",
                        "status_text": "in_storage",
                        "current_location_text": "A-01",
                    }
                ]
            if "= 'draft'" in sql_text:
                return [{"tool_code": "T000001", "order_no": "TO-OUT-20260322-009"}]
            if "IN (" in sql_text and "main.[单据状态] IN" in sql_text:
                return []
            return []

        db.execute_query.side_effect = execute_query_side_effect

        repo = OrderRepository(db_manager=db)
        repo.add_tool_io_log = Mock(return_value=True)
        result = repo.create_order(
            {
                "order_type": "outbound",
                "initiator_id": "U001",
                "initiator_name": "Alice",
                "initiator_role": "team_leader",
                "items": [{"tool_id": "1", "tool_code": "T000001", "apply_qty": 1}],
            }
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["order_no"], "TO-OUT-20260323-001")
        self.assertIn("warning", result)
        self.assertIn("T000001", result["warning"])
        self.assertIn("TO-OUT-20260322-009", result["warning"])

    @patch("backend.database.services.order_service.generate_order_no_atomic", return_value="TO-OUT-20260323-002")
    def test_create_order_without_draft_conflict_has_no_warning(
        self,
        _generate_order_no,
    ):
        db = Mock()

        def execute_query_side_effect(sql, params=None, fetch=True):
            sql_text = str(sql or "")
            if "AS tool_code" in sql_text and "Tooling_ID_Main" in sql_text:
                return [
                    {
                        "tool_code": "T000001",
                        "tool_name": "Tool A",
                        "drawing_no": "D-01",
                        "spec_model": "M1",
                        "status_text": "in_storage",
                        "current_location_text": "A-01",
                    }
                ]
            if "= 'draft'" in sql_text:
                return []
            if "IN (" in sql_text and "main.[单据状态] IN" in sql_text:
                return []
            return []

        db.execute_query.side_effect = execute_query_side_effect

        repo = OrderRepository(db_manager=db)
        repo.add_tool_io_log = Mock(return_value=True)
        result = repo.create_order(
            {
                "order_type": "outbound",
                "initiator_id": "U001",
                "initiator_name": "Alice",
                "initiator_role": "team_leader",
                "items": [{"tool_id": "1", "tool_code": "T000001", "apply_qty": 1}],
            }
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["order_no"], "TO-OUT-20260323-002")
        self.assertNotIn("warning", result)


class OrderRepositoryPendingKeeperTests(unittest.TestCase):
    def test_pending_keeper_orders_keep_submitted_visible_across_orgs(self):
        db = Mock()
        db.execute_query.return_value = []
        repo = OrderRepository(db_manager=db)

        repo.get_pending_keeper_orders("U_KEEPER_001")

        db.execute_query.assert_called_once()
        sql, params = db.execute_query.call_args.args
        self.assertIn("order_status = 'submitted' OR keeper_id = ? OR keeper_id IS NULL", sql)
        self.assertEqual(params, ("U_KEEPER_001",))


class OrderRepositoryCancellationAndResetTests(unittest.TestCase):
    def test_cancel_order_persists_cancel_reason_to_reject_and_cancel_reason_columns(self):
        db = Mock()
        db.execute_query.side_effect = [
            [{"order_status": "submitted"}],
            None,
            None,
        ]
        repo = OrderRepository(db_manager=db)
        repo.add_tool_io_log = Mock(return_value=True)

        result = repo.cancel_order(
            "ORD-001",
            operator_id="U_KEEPER",
            operator_name="Keeper",
            operator_role="keeper",
            cancel_reason="库存异常",
        )

        self.assertEqual(result, {"success": True})
        update_call = db.execute_query.call_args_list[1]
        self.assertIn("reject_reason", update_call.args[0])
        self.assertIn("cancel_reason", update_call.args[0])
        self.assertEqual(update_call.args[1], ("库存异常", "库存异常", "ORD-001"))
        logged = repo.add_tool_io_log.call_args.args[0]
        self.assertIn("库存异常", logged["content"])

    def test_reset_order_to_draft_allows_cancelled_for_initiator(self):
        db = Mock()
        db.execute_query.side_effect = [
            [{"order_status": "cancelled", "initiator_id": "U_INIT"}],
            None,
        ]
        repo = OrderRepository(db_manager=db)
        repo.add_tool_io_log = Mock(return_value=True)

        result = repo.reset_order_to_draft(
            "ORD-001",
            operator_id="U_INIT",
            operator_name="Initiator",
            operator_role="team_leader",
        )

        self.assertEqual(result, {"success": True, "status": "draft"})
        update_call = db.execute_query.call_args_list[1]
        self.assertIn("cancel_reason", update_call.args[0])

    def test_reset_order_to_draft_rejects_non_initiator(self):
        db = Mock()
        db.execute_query.return_value = [{"order_status": "cancelled", "initiator_id": "U_INIT"}]
        repo = OrderRepository(db_manager=db)
        repo.add_tool_io_log = Mock(return_value=True)

        result = repo.reset_order_to_draft(
            "ORD-001",
            operator_id="U_OTHER",
            operator_name="Other",
            operator_role="team_leader",
        )

        self.assertEqual(result["success"], False)
        self.assertIn("只有订单发起人可以重置为草稿", result["error"])
        self.assertEqual(db.execute_query.call_count, 1)
        repo.add_tool_io_log.assert_not_called()


if __name__ == "__main__":
    unittest.main()
