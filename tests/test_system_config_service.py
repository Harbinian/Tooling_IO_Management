import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services.tool_io_service import get_system_config, list_system_configs, update_system_config


class SystemConfigServiceTests(unittest.TestCase):
    def test_list_system_configs_only_requires_system_config_table(self):
        repo = patch("backend.services.tool_io_service.SystemConfigRepository").start()()
        ensure_mock = patch("backend.database.schema.schema_manager.ensure_system_config_table", return_value=True).start()
        unrelated_ensure = patch(
            "backend.services.tool_io_service.ensure_tool_io_tables",
            side_effect=AssertionError("system config flow should not depend on ensure_tool_io_tables"),
        ).start()
        self.addCleanup(patch.stopall)
        repo.list_configs.return_value = [{"config_key": "mpl_enabled", "config_value": "false"}]

        result = list_system_configs()

        self.assertEqual(result, {"success": True, "data": [{"config_key": "mpl_enabled", "config_value": "false"}]})
        ensure_mock.assert_called_once_with()
        unrelated_ensure.assert_not_called()

    def test_get_system_config_returns_not_found_without_touching_full_schema_setup(self):
        repo = patch("backend.services.tool_io_service.SystemConfigRepository").start()()
        ensure_mock = patch("backend.database.schema.schema_manager.ensure_system_config_table", return_value=True).start()
        unrelated_ensure = patch(
            "backend.services.tool_io_service.ensure_tool_io_tables",
            side_effect=AssertionError("system config flow should not depend on ensure_tool_io_tables"),
        ).start()
        self.addCleanup(patch.stopall)
        repo.get_config.return_value = None

        result = get_system_config("unknown_key")

        self.assertEqual(result, {"success": False, "error": "config not found"})
        ensure_mock.assert_called_once_with()
        unrelated_ensure.assert_not_called()

    def test_update_system_config_normalizes_boolean_and_uses_targeted_bootstrap(self):
        repo = patch("backend.services.tool_io_service.SystemConfigRepository").start()()
        ensure_mock = patch("backend.database.schema.schema_manager.ensure_system_config_table", return_value=True).start()
        unrelated_ensure = patch(
            "backend.services.tool_io_service.ensure_tool_io_tables",
            side_effect=AssertionError("system config flow should not depend on ensure_tool_io_tables"),
        ).start()
        self.addCleanup(patch.stopall)
        repo.get_config.return_value = "true"
        repo.list_configs.return_value = [{"config_key": "mpl_enabled", "config_value": "true"}]

        result = update_system_config(
            "mpl_enabled",
            {"config_value": "YES", "description": "toggle"},
            current_user={"display_name": "Admin"},
        )

        self.assertEqual(result, {"success": True, "data": {"config_key": "mpl_enabled", "config_value": "true"}})
        repo.set_config.assert_called_once_with(
            "mpl_enabled",
            "true",
            updated_by="Admin",
            description="toggle",
        )
        self.assertEqual(ensure_mock.call_count, 2)
        unrelated_ensure.assert_not_called()

    def test_list_system_configs_raises_clear_error_when_system_config_bootstrap_fails(self):
        with patch(
            "backend.database.schema.schema_manager.ensure_system_config_table",
            return_value=False,
        ):
            with self.assertRaisesRegex(RuntimeError, "sys_system_config is not ready"):
                list_system_configs()


if __name__ == "__main__":
    unittest.main()
