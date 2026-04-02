# -*- coding: utf-8 -*-
"""Repository for system configuration values."""

from __future__ import annotations

from typing import Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import SYSTEM_CONFIG_COLUMNS, TABLE_NAMES


class SystemConfigRepository:
    """Read and write system configuration entries."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def get_config(self, config_key: str) -> Optional[str]:
        rows = self._db.execute_query(
            f"""
            SELECT [{SYSTEM_CONFIG_COLUMNS['config_value']}] AS config_value
            FROM [{TABLE_NAMES['SYSTEM_CONFIG']}]
            WHERE [{SYSTEM_CONFIG_COLUMNS['config_key']}] = ?
            """,
            (str(config_key or "").strip(),),
        )
        if not rows:
            return None
        value = rows[0].get("config_value")
        return None if value is None else str(value)

    def set_config(self, config_key: str, config_value: str, updated_by: str, description: Optional[str] = None) -> bool:
        normalized_key = str(config_key or "").strip()
        if not normalized_key:
            return False
        self._db.execute_query(
            f"""
            MERGE [{TABLE_NAMES['SYSTEM_CONFIG']}] AS target
            USING (
                SELECT
                    ? AS [{SYSTEM_CONFIG_COLUMNS['config_key']}],
                    ? AS [{SYSTEM_CONFIG_COLUMNS['config_value']}],
                    ? AS [new_description],
                    ? AS [{SYSTEM_CONFIG_COLUMNS['updated_by']}]
            ) AS source
            ON target.[{SYSTEM_CONFIG_COLUMNS['config_key']}] = source.[{SYSTEM_CONFIG_COLUMNS['config_key']}]
            WHEN MATCHED THEN
                UPDATE SET
                    target.[{SYSTEM_CONFIG_COLUMNS['config_value']}] = source.[{SYSTEM_CONFIG_COLUMNS['config_value']}],
                    target.[{SYSTEM_CONFIG_COLUMNS['description']}] = COALESCE(source.[new_description], target.[{SYSTEM_CONFIG_COLUMNS['description']}]),
                    target.[{SYSTEM_CONFIG_COLUMNS['updated_by']}] = source.[{SYSTEM_CONFIG_COLUMNS['updated_by']}],
                    target.[{SYSTEM_CONFIG_COLUMNS['updated_at']}] = SYSDATETIME()
            WHEN NOT MATCHED THEN
                INSERT (
                    [{SYSTEM_CONFIG_COLUMNS['config_key']}],
                    [{SYSTEM_CONFIG_COLUMNS['config_value']}],
                    [{SYSTEM_CONFIG_COLUMNS['description']}],
                    [{SYSTEM_CONFIG_COLUMNS['updated_by']}],
                    [{SYSTEM_CONFIG_COLUMNS['updated_at']}]
                )
                VALUES (
                    source.[{SYSTEM_CONFIG_COLUMNS['config_key']}],
                    source.[{SYSTEM_CONFIG_COLUMNS['config_value']}],
                    source.[new_description],
                    source.[{SYSTEM_CONFIG_COLUMNS['updated_by']}],
                    SYSDATETIME()
                );
            """,
            (
                normalized_key,
                str(config_value or ""),
                None if description is None else str(description),
                str(updated_by or "").strip() or "system",
            ),
            fetch=False,
        )
        return True

    def list_configs(self) -> List[Dict]:
        return self._db.execute_query(
            f"""
            SELECT
                [{SYSTEM_CONFIG_COLUMNS['config_key']}] AS config_key,
                [{SYSTEM_CONFIG_COLUMNS['config_value']}] AS config_value,
                [{SYSTEM_CONFIG_COLUMNS['description']}] AS description,
                [{SYSTEM_CONFIG_COLUMNS['updated_by']}] AS updated_by,
                [{SYSTEM_CONFIG_COLUMNS['updated_at']}] AS updated_at
            FROM [{TABLE_NAMES['SYSTEM_CONFIG']}]
            ORDER BY [{SYSTEM_CONFIG_COLUMNS['config_key']}]
            """
        )
