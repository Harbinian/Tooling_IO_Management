import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services.notification_service import list_notifications_by_order


class NotificationServiceTests(unittest.TestCase):
    def test_list_notifications_by_order_bootstraps_tables_before_query(self):
        fake_rows = [
            {
                "notification_id": 101,
                "order_id": "TO-OUT-20260316-003",
                "notification_type": "transport_notice",
                "notify_channel": "feishu",
                "receiver": "name:Bob",
                "message_title": "Transport notification",
                "message_body": "Ready to move",
                "status": "sent",
                "send_result": "ok",
                "copy_text": '{"target_user_id":"U100","target_user_name":"Bob","target_role":"keeper","metadata":{"source":"transport"}}',
            }
        ]

        with patch("backend.services.notification_service.ensure_tool_io_tables") as ensure_tables, patch(
            "backend.services.notification_service.DatabaseManager"
        ) as db_manager:
            db_manager.return_value.execute_query.return_value = fake_rows

            result = list_notifications_by_order("TO-OUT-20260316-003")

        ensure_tables.assert_called_once_with()
        db_manager.return_value.execute_query.assert_called_once()
        self.assertTrue(result["success"])
        self.assertEqual(result["data"][0]["notification_id"], 101)
        self.assertEqual(result["data"][0]["order_id"], "TO-OUT-20260316-003")
        self.assertEqual(result["data"][0]["target_user_id"], "U100")
        self.assertEqual(result["data"][0]["metadata"], {"source": "transport"})


if __name__ == "__main__":
    unittest.main()
