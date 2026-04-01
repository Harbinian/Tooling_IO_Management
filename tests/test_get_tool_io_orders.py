import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services.tool_io_runtime import (
    get_order_detail_runtime,
    keeper_confirm_runtime,
    list_pending_keeper_orders,
)
from backend.services.tool_io_service import (
    create_order,
    final_confirm,
    generate_keeper_text,
    generate_transport_text,
    get_final_confirm_availability,
    get_order_detail,
    get_notification_records,
    list_orders,
    notify_transport,
)
from database import get_tool_io_orders


class FakeRow(dict):
    def __init__(self, mapping=None, fallback=None):
        super().__init__(mapping or {})
        self.fallback = fallback

    def get(self, key, default=None):
        if key in self:
            return super().get(key, default)
        if self.fallback is not None:
            return self.fallback
        return default


class FakeRuntimeDatabaseManager:
    def __init__(self):
        self.calls = []
        self.updated_items = []
        self.updated_orders = []
        self.select_calls = 0

    def execute_query(self, sql, params=None, fetch=True):
        self.calls.append((sql, params, fetch))

        if not fetch and "UPDATE" in sql:
            if len(self.updated_items) < 2:
                self.updated_items.append(params)
            else:
                self.updated_orders.append(params)
            return []

        self.select_calls += 1
        if self.select_calls == 1:
            return [FakeRow({"order_no": "TO-001", "order_status": "submitted"}, fallback="submitted")]
        if self.select_calls == 2:
            return [FakeRow(fallback="T-01"), FakeRow(fallback="T-02")]
        if self.select_calls == 3:
            return [{"notify_type": "transport_notice"}]
        return []


class ToolIOOrderQueryTests(unittest.TestCase):
    def test_get_tool_io_orders_keeps_filtered_query_params_aligned(self):
        repo = patch("database.OrderRepository").start()()
        self.addCleanup(patch.stopall)
        repo.get_orders.return_value = {
            "success": True,
            "data": [{"order_no": "TO-OUT-20260312-001", "order_status": "draft"}],
            "total": 2,
            "page_no": 2,
            "page_size": 20,
        }

        result = get_tool_io_orders(status="submitted", keyword="P-001", page=2, page_size=20)

        self.assertTrue(result["success"])
        repo.get_orders.assert_called_once()
        kwargs = repo.get_orders.call_args.kwargs
        self.assertEqual(kwargs["order_status"], "submitted")
        self.assertEqual(kwargs["keyword"], "P-001")
        self.assertEqual(kwargs["page_no"], 2)
        self.assertEqual(kwargs["page_size"], 20)

    def test_get_tool_io_orders_returns_rows_from_paginated_query(self):
        repo = patch("database.OrderRepository").start()()
        self.addCleanup(patch.stopall)
        repo.get_orders.return_value = {
            "success": True,
            "data": [{"order_no": "TO-OUT-20260312-001", "order_status": "draft"}],
            "total": 2,
            "page_no": 1,
            "page_size": 10,
        }
        result = get_tool_io_orders(page=1, page_size=10)

        self.assertEqual(
            result,
            {
                "success": True,
                "data": [{"order_no": "TO-OUT-20260312-001", "order_status": "draft"}],
                "total": 2,
                "page_no": 1,
                "page_size": 10,
            },
        )
        repo.get_orders.assert_called_once()
        kwargs = repo.get_orders.call_args.kwargs
        self.assertEqual(kwargs["page_no"], 1)
        self.assertEqual(kwargs["page_size"], 10)

    def test_list_orders_applies_scope_sql_from_current_user(self):
        with patch(
            "backend.services.tool_io_service.get_tool_io_orders",
            return_value={
                "success": True,
                "data": [
                    {"order_no": "TO-001", "initiator_id": "U001"},
                    {"order_no": "TO-002", "initiator_id": "U999"},
                ],
                "total": 2,
                "page_no": 1,
                "page_size": 5000,
            },
        ) as get_orders, patch(
            "backend.services.tool_io_service.resolve_order_data_scope",
            return_value={"all_access": False, "self_user_ids": ["U001"], "assigned_user_ids": [], "org_user_ids": []},
        ), patch(
            "backend.services.tool_io_service.order_matches_scope",
            side_effect=[True, False],
        ):
            result = list_orders({"page_no": 1, "page_size": 20}, current_user={"user_id": "U001"})

        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["data"], [{"order_no": "TO-001", "initiator_id": "U001"}])
        self.assertEqual(get_orders.call_args.kwargs["page"], 1)
        self.assertEqual(get_orders.call_args.kwargs["page_size"], 5000)

    def test_list_orders_filters_draft_for_all_access_user(self):
        with patch(
            "backend.services.tool_io_service.get_tool_io_orders",
            return_value={
                "success": True,
                "data": [
                    {"order_no": "TO-001", "order_status": "draft"},
                    {"order_no": "TO-002", "order_status": "submitted"},
                ],
                "total": 2,
                "page_no": 1,
                "page_size": 5000,
            },
        ), patch(
            "backend.services.tool_io_service.resolve_order_data_scope",
            return_value={
                "all_access": True,
                "scope_types": ["ALL"],
                "org_ids": [],
                "org_user_ids": [],
                "self_user_ids": [],
                "assigned_user_ids": [],
                "current_user_id": "U-ADMIN",
            },
        ):
            result = list_orders({"page_no": 1, "page_size": 20}, current_user={"user_id": "U-ADMIN"})

        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["data"], [{"order_no": "TO-002", "order_status": "submitted"}])

    def test_list_orders_keeps_draft_for_non_all_access_user_when_scope_allows(self):
        with patch(
            "backend.services.tool_io_service.get_tool_io_orders",
            return_value={
                "success": True,
                "data": [{"order_no": "TO-003", "order_status": "draft", "initiator_id": "U001"}],
                "total": 1,
                "page_no": 1,
                "page_size": 5000,
            },
        ), patch(
            "backend.services.tool_io_service.resolve_order_data_scope",
            return_value={
                "all_access": False,
                "scope_types": ["SELF"],
                "org_ids": [],
                "org_user_ids": [],
                "self_user_ids": ["U001"],
                "assigned_user_ids": [],
                "current_user_id": "U001",
            },
        ):
            result = list_orders({"page_no": 1, "page_size": 20}, current_user={"user_id": "U001"})

        self.assertTrue(result["success"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(
            result["data"],
            [{"order_no": "TO-003", "order_status": "draft", "initiator_id": "U001"}],
        )

    def test_create_order_stamps_org_id_from_authenticated_context(self):
        with patch("backend.services.tool_io_service.ensure_tool_io_tables"), patch(
            "backend.services.tool_io_service.create_tool_io_order",
            return_value={"success": True, "order_no": "TO-001"},
        ) as create_db_order:
            result = create_order(
                {"order_type": "outbound", "items": [{"tool_code": "T-01"}]},
                current_user={
                    "current_org": {"org_id": "ORG_TEAM"},
                    "default_org": {"org_id": "ORG_FACTORY"},
                },
            )

        self.assertTrue(result["success"])
        self.assertEqual(create_db_order.call_args.args[0]["org_id"], "ORG_TEAM")


class ToolIORuntimeTests(unittest.TestCase):
    def test_list_pending_keeper_orders_adds_keeper_filter(self):
        with patch(
            "backend.services.tool_io_runtime.get_pending_keeper_orders",
            return_value=[{"order_no": "TO-001"}],
        ) as get_pending:
            result = list_pending_keeper_orders("U-KEEPER")

        self.assertEqual(result, [{"order_no": "TO-001"}])
        get_pending.assert_called_once_with("U-KEEPER")

    def test_get_order_detail_runtime_includes_items_and_notifications(self):
        with patch(
            "backend.services.tool_io_runtime.get_tool_io_order",
            return_value={"order_no": "TO-001", "items": [FakeRow(fallback="T-01"), FakeRow(fallback="T-02")]},
        ):
            result = get_order_detail_runtime("TO-001")

        self.assertEqual(result["items"], [FakeRow(fallback="T-01"), FakeRow(fallback="T-02")])
        self.assertEqual(result["notification_records"], [])

    def test_keeper_confirm_runtime_updates_items_order_and_log(self):
        with patch(
            "backend.services.tool_io_runtime.keeper_confirm_order",
            return_value={"success": True, "status": "partially_confirmed", "approved_count": 1},
        ) as keeper_confirm_order_mock:
            result = keeper_confirm_runtime(
                "TO-001",
                "U-KEEPER",
                "Keeper",
                {
                    "transport_type": "manual",
                    "transport_assignee_name": "Transport User",
                    "keeper_remark": "checked",
                    "items": [
                        {
                            "tool_code": "T-01",
                            "location_text": "A-01",
                            "approved_qty": 1,
                            "status": "approved",
                        },
                        {
                            "tool_code": "T-02",
                            "location_text": "A-02",
                            "approved_qty": 0,
                            "status": "rejected",
                        },
                    ],
                },
                "U-KEEPER",
                "Keeper",
                "keeper",
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "partially_confirmed")
        self.assertEqual(result["approved_count"], 1)
        self.assertEqual(result["before_status"], "submitted")
        self.assertEqual(result["after_status"], "partially_confirmed")
        self.assertEqual(result["keeper_remark"], "checked")
        keeper_confirm_order_mock.assert_called_once()

    def test_keeper_confirm_runtime_rejects_unknown_tool_code(self):
        with patch(
            "backend.services.tool_io_runtime.keeper_confirm_order",
            return_value={"success": False, "error": "tool code T-99 does not belong to order TO-001"},
        ):
            result = keeper_confirm_runtime(
                "TO-001",
                "U-KEEPER",
                "Keeper",
                {"items": [{"tool_code": "T-99", "status": "approved"}]},
                "U-KEEPER",
                "Keeper",
                "keeper",
            )

        self.assertFalse(result["success"])
        self.assertIn("does not belong to order", result["error"])


class ToolIOFinalConfirmationServiceTests(unittest.TestCase):
    def test_get_final_confirm_availability_allows_outbound_initiator(self):
        with patch(
            "backend.services.tool_io_service.get_order_detail_runtime",
            return_value={
                "order_no": "TO-001",
                "order_type": "outbound",
                "order_status": "transport_notified",
                "initiator_id": "U-INIT",
            },
        ):
            result = get_final_confirm_availability("TO-001", "U-INIT", "initiator")

        self.assertTrue(result["success"])
        self.assertTrue(result["available"])
        self.assertEqual(result["expected_role"], "initiator")

    def test_get_final_confirm_availability_rejects_wrong_role(self):
        with patch(
            "backend.services.tool_io_service.get_order_detail_runtime",
            return_value={
                "order_no": "TO-002",
                "order_type": "inbound",
                "order_status": "transport_notified",
                "keeper_id": "U-KEEPER",
            },
        ):
            result = get_final_confirm_availability("TO-002", "U-KEEPER", "initiator")

        self.assertTrue(result["success"])
        self.assertFalse(result["available"])
        self.assertIn("requires role keeper", result["reason"])

    def test_final_confirm_blocks_ineligible_status(self):
        with patch(
            "backend.services.tool_io_service.get_order_detail_runtime",
            return_value={
                "order_no": "TO-003",
                "order_type": "outbound",
                "order_status": "keeper_confirmed",
                "initiator_id": "U-INIT",
            },
        ), patch("backend.services.tool_io_service.final_confirm_order") as final_confirm_order_mock:
            result = final_confirm(
                "TO-003",
                {"operator_id": "U-INIT", "operator_name": "Init User", "operator_role": "initiator"},
            )

        self.assertFalse(result["success"])
        final_confirm_order_mock.assert_not_called()

    def test_final_confirm_returns_updated_detail(self):
        detail_before = {
            "order_no": "TO-004",
            "order_type": "inbound",
            "order_status": "final_confirmation_pending",
            "keeper_id": "U-KEEPER",
        }
        detail_after = {
            "order_no": "TO-004",
            "order_type": "inbound",
            "order_status": "completed",
            "keeper_id": "U-KEEPER",
        }

        with patch(
            "backend.services.tool_io_service.get_order_detail_runtime",
            side_effect=[detail_before, detail_after],
        ), patch(
            "backend.services.tool_io_service.final_confirm_order",
            return_value={"success": True},
        ) as final_confirm_order_mock:
            result = final_confirm(
                "TO-004",
                {"operator_id": "U-KEEPER", "operator_name": "Keeper User", "operator_role": "keeper"},
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["after_status"], "completed")
        self.assertEqual(result["data"]["order_status"], "completed")
        final_confirm_order_mock.assert_called_once_with("TO-004", "U-KEEPER", "Keeper User", "keeper")


class ToolIONotificationUsageTests(unittest.TestCase):
    def test_get_notification_records_returns_order_notifications(self):
        with patch(
            "backend.services.tool_io_service._load_order_scope_projection",
            return_value={"order_no": "TO-005", "order_status": "submitted", "initiator_id": "U001"},
        ), patch(
            "backend.services.tool_io_service._is_order_accessible",
            return_value=True,
        ), patch(
            "backend.services.tool_io_service.list_notifications_by_order",
            return_value={"success": True, "data": [{"notify_type": "transport_notice"}]},
        ):
            result = get_notification_records("TO-005", current_user={"user_id": "U001"})

        self.assertEqual(result, {"success": True, "data": [{"notify_type": "transport_notice"}]})

    def test_get_notification_records_returns_not_found_when_scope_rejects_order(self):
        with patch(
            "backend.services.tool_io_service._load_order_scope_projection",
            return_value={"order_no": "TO-005"},
        ), patch(
            "backend.services.tool_io_service._is_order_accessible",
            return_value=False,
        ):
            result = get_notification_records("TO-005", current_user={"user_id": "U001"})

        self.assertEqual(result, {"success": False, "error": "order not found", "data": []})

    def test_get_order_detail_returns_empty_when_scope_rejects_order(self):
        with patch(
            "backend.services.tool_io_service.get_order_detail_runtime",
            return_value={"order_no": "TO-010", "initiator_id": "U999"},
        ), patch(
            "backend.services.tool_io_service.order_matches_scope",
            return_value=False,
        ), patch(
            "backend.services.tool_io_service.resolve_order_data_scope",
            return_value={"all_access": False, "self_user_ids": ["U001"], "assigned_user_ids": [], "org_user_ids": []},
        ):
            result = get_order_detail("TO-010", current_user={"user_id": "U001"})

        self.assertEqual(result, {})

    def test_generate_keeper_text_creates_internal_notification_record(self):
        order = {
            "order_no": "TO-006",
            "order_type": "outbound",
            "initiator_name": "Alice",
            "initiator_id": "U-INIT",
            "items": [{"tool_code": "T-01", "tool_name": "Clamp", "drawing_no": "D-01", "apply_qty": 2}],
        }

        with patch("backend.services.tool_io_service.get_order_detail", return_value=order), patch(
            "backend.services.tool_io_service._create_notification_record"
        ) as create_record:
            result = generate_keeper_text("TO-006")

        self.assertTrue(result["success"])
        create_record.assert_called_once()
        self.assertEqual(create_record.call_args.kwargs["notify_type"], "keeper_request")
        self.assertEqual(create_record.call_args.kwargs["notify_channel"], "internal")

    def test_generate_transport_text_creates_preview_record(self):
        order = {
            "order_no": "TO-007",
            "transport_type": "manual",
            "transport_assignee_name": "Bob",
            "items": [
                {
                    "tool_code": "T-02",
                    "tool_name": "Fixture",
                    "location_text": "A-01",
                    "approved_qty": 1,
                    "item_status": "approved",
                }
            ],
        }

        with patch("backend.services.tool_io_service.get_order_detail", return_value=order), patch(
            "backend.services.tool_io_service._create_notification_record"
        ) as create_record:
            result = generate_transport_text("TO-007")

        self.assertTrue(result["success"])
        create_record.assert_called_once()
        self.assertEqual(create_record.call_args.kwargs["notify_type"], "transport_preview")
        self.assertEqual(create_record.call_args.kwargs["copy_text"], result["wechat_text"])

    def test_notify_transport_fails_without_advancing_state_when_send_fails(self):
        order = {
            "order_no": "TO-008",
            "order_status": "keeper_confirmed",
            "transport_assignee_name": "Bob",
        }

        with patch("backend.services.tool_io_service.get_order_detail", return_value=order), patch(
            "backend.services.tool_io_service.generate_transport_text",
            return_value={"success": True, "text": "transport", "wechat_text": "wechat"},
        ), patch(
            "backend.services.tool_io_service.deliver_notification_to_feishu",
            return_value={
                "success": False,
                "notification_id": 99,
                "send_status": "failed",
                "send_result": "Feishu send failed",
            },
        ), patch("backend.services.tool_io_service.DatabaseManager") as db_mock, patch(
            "backend.services.tool_io_service.write_order_audit_log"
        ) as add_log:
            result = notify_transport("TO-008", {"operator_name": "Keeper", "receiver": "Bob"})

        self.assertFalse(result["success"])
        self.assertEqual(result["send_status"], "failed")
        self.assertIn("Feishu send failed", result["send_result"])
        db_mock.return_value.execute_query.assert_not_called()
        add_log.assert_called_once()
        self.assertEqual(add_log.call_args.kwargs["new_status"], "keeper_confirmed")

    def test_notify_transport_advances_state_when_send_succeeds(self):
        order = {
            "order_no": "TO-009",
            "order_status": "keeper_confirmed",
            "transport_assignee_name": "Bob",
        }

        with patch("backend.services.tool_io_service.get_order_detail", return_value=order), patch(
            "backend.services.tool_io_service.generate_transport_text",
            return_value={"success": True, "text": "transport", "wechat_text": "wechat"},
        ), patch(
            "backend.services.tool_io_service.deliver_notification_to_feishu",
            return_value={
                "success": True,
                "notification_id": 100,
                "send_status": "sent",
                "send_result": "ok",
            },
        ), patch("backend.services.tool_io_service.DatabaseManager") as db_mock, patch(
            "backend.services.tool_io_service.write_order_audit_log"
        ) as add_log:
            result = notify_transport("TO-009", {"operator_name": "Keeper", "receiver": "Bob"})

        self.assertTrue(result["success"])
        self.assertEqual(result["send_status"], "sent")
        self.assertEqual(result["send_result"], "ok")
        db_mock.return_value.execute_query.assert_called_once()
        add_log.assert_called_once()
        self.assertEqual(add_log.call_args.kwargs["new_status"], "transport_notified")


if __name__ == "__main__":
    unittest.main()



