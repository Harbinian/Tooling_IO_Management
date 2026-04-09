# -*- coding: utf-8 -*-
"""
Shared utility functions with no Service-layer dependencies.
Can be imported by any module in the services layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional


def _build_actor_context(
    payload: Dict,
    *,
    actor_id_key: str = "operator_id",
    actor_name_key: str = "operator_name",
    actor_role_key: str = "operator_role",
) -> Dict:
    return {
        "user_id": payload.get(actor_id_key, ""),
        "user_name": payload.get(actor_name_key, ""),
        "user_role": payload.get(actor_role_key, ""),
    }


def _normalize_bool_text(value: Optional[str], default: str = "false") -> str:
    normalized = str(value if value is not None else default).strip().lower()
    return "true" if normalized in {"1", "true", "yes", "on"} else "false"


def _pick_value(record: Dict, keys: List[str], default: Optional[str] = ""):
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default


def _to_iso8601(value) -> Optional[str]:
    if value in (None, ""):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _format_order_datetime(value) -> str:
    if value is None:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)
