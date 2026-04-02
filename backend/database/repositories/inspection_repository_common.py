# -*- coding: utf-8 -*-
"""Shared helpers for inspection repositories."""

from __future__ import annotations

import base64
from datetime import datetime
from typing import Optional

from backend.database.core.database_manager import DatabaseManager, ORDER_NO_RETRY_LIMIT, ORDER_NO_SEQUENCE_TABLE
from backend.database.utils.sql_utils import is_duplicate_key_error

INSPECTION_MAX_ATTACHMENT_BYTES = 2 * 1024 * 1024


def generate_inspection_no_atomic(prefix: str) -> str:
    """Allocate a database-backed inspection document number."""
    normalized_prefix = str(prefix or "").strip().upper()
    if normalized_prefix not in {"DJP", "DJT", "RPT"}:
        raise ValueError("unsupported inspection prefix")

    date_str = datetime.now().strftime("%Y%m%d")
    sequence_key = f"{normalized_prefix}-{date_str}"
    db = DatabaseManager()

    update_sql = f"""
    UPDATE {ORDER_NO_SEQUENCE_TABLE} WITH (UPDLOCK, HOLDLOCK)
    SET current_value = current_value + 1,
        updated_at = GETDATE()
    OUTPUT INSERTED.current_value AS current_value
    WHERE sequence_key = ?
    """

    insert_sql = f"""
    INSERT INTO {ORDER_NO_SEQUENCE_TABLE} (sequence_key, current_value, updated_at)
    VALUES (?, 1, GETDATE())
    """

    for _ in range(ORDER_NO_RETRY_LIMIT):
        rows = db.execute_query(update_sql, (sequence_key,))
        if rows:
            seq = int(rows[0].get("current_value", 1))
            return f"{sequence_key}-{seq:03d}"

        try:
            db.execute_query(insert_sql, (sequence_key,), fetch=False)
            return f"{sequence_key}-001"
        except Exception as exc:
            if not is_duplicate_key_error(exc):
                raise

    raise RuntimeError("failed to allocate inspection number")


def decode_base64_payload(payload: Optional[str]) -> bytes:
    """Decode a base64 payload and enforce the 2MB attachment limit."""
    normalized_payload = str(payload or "").strip()
    if not normalized_payload:
        return b""
    if "," in normalized_payload and normalized_payload.lower().startswith("data:"):
        normalized_payload = normalized_payload.split(",", 1)[1]
    decoded = base64.b64decode(normalized_payload, validate=True)
    if len(decoded) > INSPECTION_MAX_ATTACHMENT_BYTES:
        raise ValueError("attachment size exceeds 2MB limit")
    return decoded
