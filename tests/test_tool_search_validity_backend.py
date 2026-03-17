# -*- coding: utf-8 -*-
import sys
import types
from unittest.mock import patch

sys.modules.setdefault("pyodbc", types.SimpleNamespace(Connection=object, connect=lambda *args, **kwargs: None))
sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))

from backend.services.tool_io_service import search_tool_inventory


def test_search_tool_inventory_normalizes_disabled_fields():
    raw_result = {
        "success": True,
        "data": [
            {"tool_code": "T001", "disabled": 0, "disabled_reason": None},
            {"tool_code": "T002", "disabled": "1", "disabled_reason": "工装处于返修状态，不可使用"},
            {"tool_code": "T003", "disabled": False, "disabled_reason": "  定检超期，工装不具备使用条件  "},
            {"tool_code": "T004", "disabled": "false", "disabled_reason": "   "},
        ],
        "total": 4,
        "page_no": 1,
        "page_size": 20,
    }
    with patch("backend.services.tool_io_service.search_tools", return_value=raw_result):
        result = search_tool_inventory({"keyword": "", "page_no": 1, "page_size": 20})

    assert result["success"] is True
    assert [row["disabled"] for row in result["data"]] == [False, True, True, False]
    assert [row["disabled_reason"] for row in result["data"]] == [
        None,
        "工装处于返修状态，不可使用",
        "定检超期，工装不具备使用条件",
        None,
    ]
