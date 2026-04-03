import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))

from backend.services.tool_io_runtime import get_recent_notification_failures, get_recent_operation_errors


class ToolIoRuntimeSqlTests(unittest.TestCase):
    @patch("backend.services.tool_io_runtime.DatabaseManager")
    def test_get_recent_operation_errors_uses_operation_log_table(self, db_manager_cls):
        db_manager = db_manager_cls.return_value
        db_manager.execute_query.return_value = []

        get_recent_operation_errors(5)

        db_manager.execute_query.assert_called_once()
        sql, params = db_manager.execute_query.call_args.args
        self.assertIn("FROM [tool_io_operation_log]", sql)
        self.assertIn("ORDER BY [operation_time] DESC", sql)
        self.assertEqual(params, (5,))

    @patch("backend.services.tool_io_runtime.DatabaseManager")
    def test_get_recent_notification_failures_uses_notification_table(self, db_manager_cls):
        db_manager = db_manager_cls.return_value
        db_manager.execute_query.return_value = []

        get_recent_notification_failures(7)

        db_manager.execute_query.assert_called_once()
        sql, params = db_manager.execute_query.call_args.args
        self.assertIn("FROM [tool_io_notification]", sql)
        self.assertIn("ORDER BY [send_time] DESC", sql)
        self.assertEqual(params, (7,))


if __name__ == "__main__":
    unittest.main()
