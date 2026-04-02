# -*- coding: utf-8 -*-
"""Tool IO query compatibility wrappers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from database import (
    check_tools_available,
    create_tool_io_order,
    ensure_tool_io_tables,
    submit_tool_io_order,
)

__all__ = [
    "check_tools_available",
    "create_tool_io_order",
    "ensure_tool_io_tables",
    "submit_tool_io_order",
]


def get_tool_lock_conflicts(serial_nos: List[str], exclude_order_no: Optional[str] = None) -> Dict[str, Any]:
    """Backward-compatible alias for tool occupancy checks."""
    return check_tools_available(serial_nos, exclude_order_no=exclude_order_no)
