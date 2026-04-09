import sys
import types
import unittest
from unittest.mock import patch

import pytest

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))

from backend.services import tool_io_service


@pytest.mark.integration
class ToolIoServiceSubmitTests(unittest.TestCase):
    @patch("backend.services.tool_io_service._emit_internal_notification")
    @patch("backend.services.tool_io_service.submit_tool_io_order")
    @patch("backend.services.tool_io_service.get_order_detail")
    def test_idempotent_submit_skips_notification_side_effects(
        self,
        mock_get_order_detail,
        mock_submit_tool_io_order,
        mock_emit_internal_notification,
    ):
        mock_get_order_detail.return_value = {
            "order_no": "ORD-001",
            "org_id": "ORG-01",
            "initiator_id": "U_INIT",
            "initiator_name": "Initiator",
        }
        mock_submit_tool_io_order.return_value = {
            "success": True,
            "order_no": "ORD-001",
            "status": "submitted",
            "idempotent": True,
        }

        result = tool_io_service.submit_order(
            "ORD-001",
            {
                "operator_id": "U_INIT",
                "operator_name": "Initiator",
                "operator_role": "team_leader",
            },
            current_user={"user_id": "U_INIT"},
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["idempotent"])
        self.assertEqual(mock_get_order_detail.call_count, 1)
        mock_emit_internal_notification.assert_not_called()


if __name__ == "__main__":
    unittest.main()
