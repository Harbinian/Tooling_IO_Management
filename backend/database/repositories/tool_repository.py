# -*- coding: utf-8 -*-
"""
Tool repository for tool master data queries.
"""

import logging
from typing import List, Dict, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import TOOL_MASTER_COLUMNS, ORDER_COLUMNS, ITEM_COLUMNS, TABLE_NAMES

logger = logging.getLogger(__name__)

TOOL_STATUS_HISTORY_TABLE = "tool_status_change_history"
ALLOWED_TOOL_STATUSES = {"in_storage", "outbounded", "maintain", "scrapped"}

TOOL_MASTER_TABLE = "Tooling_ID_Main"


class ToolRepository:
    """Repository for tool master data operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def get_tool_basic_info(self) -> List[Dict]:
        """
        Get basic tool information from tool master table.

        Returns:
            List of tool dictionaries
        """
        return self._db.get_tool_basic_info()

    def get_tool_by_serial(self, serial_no: str) -> Optional[Dict]:
        """
        Get tool by serial number.

        Args:
            serial_no: Tool serial number

        Returns:
            Tool dictionary or None
        """
        sql = f"""
            SELECT
                m.{TOOL_MASTER_COLUMNS['tool_code']},
                m.{TOOL_MASTER_COLUMNS['drawing_no']},
                m.{TOOL_MASTER_COLUMNS['tool_name']},
                m.{TOOL_MASTER_COLUMNS['current_version']},
                m.{TOOL_MASTER_COLUMNS['inspection_category']},
                m.{TOOL_MASTER_COLUMNS['inspection_expiry_date']},
                m.{TOOL_MASTER_COLUMNS['spec_model']},
                m.{TOOL_MASTER_COLUMNS['io_status']},
                m.{TOOL_MASTER_COLUMNS['available_status']},
                m.{TOOL_MASTER_COLUMNS['tool_valid_status']}
            FROM {TOOL_MASTER_TABLE} m
            WHERE m.{TOOL_MASTER_COLUMNS['tool_code']} = ?
        """
        results = self._db.execute_query(sql, (serial_no,))
        return results[0] if results else None

    def search_tools(
        self,
        keyword: str = None,
        status: str = None,
        location_keyword: str = None,
        page_no: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Search tools with filters.

        Args:
            keyword: Search keyword
            status: Filter by status
            location_keyword: Filter by location (supports LIKE wildcard matching)
            page_no: Page number
            page_size: Page size

        Returns:
            Dictionary with data, total, page info
        """
        tool_code_col = f"[{TOOL_MASTER_COLUMNS['tool_code']}]"
        spec_model_col = f"[{TOOL_MASTER_COLUMNS['spec_model']}]"
        tool_name_col = f"[{TOOL_MASTER_COLUMNS['tool_name']}]"
        drawing_no_col = f"[{TOOL_MASTER_COLUMNS['drawing_no']}]"
        location_col = f"[{TOOL_MASTER_COLUMNS['storage_location']}]"
        category_col = f"[{TOOL_MASTER_COLUMNS['inspection_category']}]"
        io_status_col = f"[{TOOL_MASTER_COLUMNS['io_status']}]"
        available_status_col = f"[{TOOL_MASTER_COLUMNS['available_status']}]"
        valid_status_col = f"[{TOOL_MASTER_COLUMNS['tool_valid_status']}]"
        version_col = f"[{TOOL_MASTER_COLUMNS['current_version']}]"
        application_history_col = f"[{TOOL_MASTER_COLUMNS['application_history']}]"
        inspection_expiry_date_col = f"[{TOOL_MASTER_COLUMNS['inspection_expiry_date']}]"
        inspection_dispatch_status_col = f"[{TOOL_MASTER_COLUMNS['inspection_dispatch_status']}]"

        probe_sql = f"""
        SELECT
            CASE WHEN COL_LENGTH(N'{TOOL_MASTER_TABLE}', N'{TOOL_MASTER_COLUMNS['tool_code']}') IS NOT NULL THEN 1 ELSE 0 END AS has_serial,
            CASE WHEN COL_LENGTH(N'{TOOL_MASTER_TABLE}', N'{TOOL_MASTER_COLUMNS['spec_model']}') IS NOT NULL THEN 1 ELSE 0 END AS has_spec_model
        """
        probe = self._db.execute_query(probe_sql)
        if probe:
            if not probe[0].get('has_serial'):
                tool_code_col = f"[{TOOL_MASTER_COLUMNS['tool_code']}]"
            if probe[0].get('has_spec_model'):
                spec_model_col = f"[{TOOL_MASTER_COLUMNS['spec_model']}]"

        conditions = []
        params = []

        if keyword:
            keyword_like = f"%{keyword.strip()}%"
            conditions.append(
                f"""
                (
                    {tool_code_col} LIKE ?
                    OR {drawing_no_col} LIKE ?
                    OR {tool_name_col} LIKE ?
                    OR {spec_model_col} LIKE ?
                    OR {location_col} LIKE ?
                    OR {category_col} LIKE ?
                    OR {application_history_col} LIKE ?
                )
                """
            )
            params.extend([keyword_like] * 7)

        if status:
            status_like = f"%{status.strip()}%"
            conditions.append(
                f"""
                (
                    {category_col} LIKE ?
                    OR {io_status_col} LIKE ?
                    OR {available_status_col} LIKE ?
                )
                """
            )
            params.extend([status_like, status_like, status_like])

        if location_keyword not in (None, ''):
            location_like = f"%{location_keyword.strip()}%"
            conditions.append(f"{location_col} LIKE ?")
            params.append(location_like)

        where_clause = ' AND '.join(conditions) if conditions else "1=1"
        count_sql = f"SELECT COUNT(*) AS total FROM [{TOOL_MASTER_TABLE}] WHERE {where_clause}"
        count_result = self._db.execute_query(count_sql, tuple(params))
        total = int(count_result[0].get('total', 0)) if count_result else 0

        offset = max(page_no - 1, 0) * page_size
        list_sql = f"""
        SELECT
            m.{tool_code_col} AS tool_code,
            m.{tool_code_col} AS tool_id,
            m.{drawing_no_col} AS drawing_no,
            m.{tool_name_col} AS tool_name,
            m.{spec_model_col} AS spec_model,
            m.{version_col} AS current_version,
            m.{location_col} AS current_location_text,
            m.{application_history_col} AS application_history,
            m.{available_status_col} AS available_status,
            m.{valid_status_col} AS valid_status,
            m.{io_status_col} AS io_status,
            m.{category_col} AS inspection_cycle,
            CASE
                WHEN validity.disabled_reason = N'工装处于返修状态，不可使用' THEN N'返修中'
                WHEN validity.disabled_reason = N'工装处于封存状态，不可使用' THEN N'封存中'
                WHEN validity.disabled_reason = N'定检超期，工装不具备使用条件' THEN N'定检超期'
                WHEN validity.disabled_reason = N'工装正在定检中，不可使用' THEN N'定检中'
                WHEN validity.disabled_reason = N'工装无合格证，不具备验收条件' THEN N'无合格证'
                ELSE COALESCE(m.{io_status_col}, m.{available_status_col}, m.{valid_status_col}, '')
            END AS status_text,
            CASE WHEN validity.disabled_reason IS NULL THEN CAST(0 AS BIT) ELSE CAST(1 AS BIT) END AS disabled,
            validity.disabled_reason AS disabled_reason
        FROM [{TOOL_MASTER_TABLE}] AS m
        CROSS APPLY (
            SELECT
                CASE
                    WHEN m.{tool_code_col} IS NULL OR LTRIM(RTRIM(CAST(m.{tool_code_col} AS NVARCHAR(255)))) = '' THEN N'工装无合格证，不具备验收条件'
                    WHEN ISDATE(m.{inspection_expiry_date_col}) = 1
                         AND CAST(m.{inspection_expiry_date_col} AS DATE) < CAST(GETDATE() AS DATE) THEN N'定检超期，工装不具备使用条件'
                    WHEN LTRIM(RTRIM(COALESCE(CAST(m.{inspection_dispatch_status_col} AS NVARCHAR(100)), ''))) = N'定检中' THEN N'工装正在定检中，不可使用'
                    WHEN COALESCE(CAST(m.{application_history_col} AS NVARCHAR(MAX)), '') LIKE N'%返修%' THEN N'工装处于返修状态，不可使用'
                    WHEN COALESCE(CAST(m.{application_history_col} AS NVARCHAR(MAX)), '') LIKE N'%封存%' THEN N'工装处于封存状态，不可使用'
                    ELSE NULL
                END AS disabled_reason
        ) AS validity
        WHERE {where_clause}
        ORDER BY m.{tool_code_col}
        OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
        """
        rows = self._db.execute_query(list_sql, tuple(params))
        return {
            'success': True,
            'data': rows,
            'total': total,
            'page_no': page_no,
            'page_size': page_size,
        }

    def check_tools_available(
        self,
        tool_codes: List[str],
        exclude_order_no: Optional[str] = None
    ) -> Dict:
        """
        Check if tools are available (not locked by other orders).

        Args:
            tool_codes: List of tool serial numbers
            exclude_order_no: Order number to exclude from check

        Returns:
            Dictionary with availability info
        """
        cleaned_codes = []
        seen_codes = set()
        for code in tool_codes or []:
            normalized = str(code).strip()
            if not normalized or normalized in seen_codes:
                continue
            seen_codes.add(normalized)
            cleaned_codes.append(normalized)

        if not cleaned_codes:
            return {"success": True, "available": True, "occupied_tools": []}

        code_placeholders = ",".join(["?"] * len(cleaned_codes))
        TOOL_LOCKED_ORDER_STATUSES = (
            "submitted",
            "keeper_confirmed",
            "partially_confirmed",
            "transport_notified",
            "transport_in_progress",
            "transport_completed",
            "final_confirmation_pending",
        )
        status_placeholders = ",".join(["?"] * len(TOOL_LOCKED_ORDER_STATUSES))

        sql = f"""
        SELECT
            detail.[{ITEM_COLUMNS['tool_code']}] AS tool_code,
            detail.[{ITEM_COLUMNS['tool_name']}] AS tool_name,
            main.[{ORDER_COLUMNS['order_no']}] AS order_no,
            main.[{ORDER_COLUMNS['order_type']}] AS order_type,
            main.[{ORDER_COLUMNS['order_status']}] AS order_status,
            main.[{ORDER_COLUMNS['initiator_name']}] AS initiator_name,
            main.[{ORDER_COLUMNS['created_at']}] AS created_at
        FROM [{TABLE_NAMES['ORDER_ITEM']}] AS detail
        INNER JOIN [{TABLE_NAMES['ORDER']}] AS main
            ON main.[{ORDER_COLUMNS['order_no']}] = detail.[{ITEM_COLUMNS['order_no']}]
        WHERE detail.[{ITEM_COLUMNS['tool_code']}] IN ({code_placeholders})
          AND main.[{ORDER_COLUMNS['is_deleted']}] = 0
          AND main.[{ORDER_COLUMNS['order_status']}] IN ({status_placeholders})
        """
        params = list(cleaned_codes) + list(TOOL_LOCKED_ORDER_STATUSES)

        normalized_exclude_order_no = str(exclude_order_no or "").strip()
        if normalized_exclude_order_no:
            sql += f" AND main.[{ORDER_COLUMNS['order_no']}] <> ?"
            params.append(normalized_exclude_order_no)

        sql += f" ORDER BY main.[{ORDER_COLUMNS['created_at']}] DESC, main.[{ORDER_COLUMNS['order_no']}] DESC"
        rows = self._db.execute_query(sql, tuple(params))

        occupied_tools = [
            {
                "tool_code": str(row.get("tool_code", "")).strip(),
                "tool_name": row.get("tool_name", ""),
                "order_no": row.get("order_no", ""),
                "order_type": row.get("order_type", ""),
                "order_status": row.get("order_status", ""),
                "initiator_name": row.get("initiator_name", ""),
                "created_at": row.get("created_at"),
            }
            for row in rows
            if str(row.get("tool_code", "")).strip()
        ]

        return {
            "success": True,
            "available": not occupied_tools,
            "occupied_tools": occupied_tools,
        }

    def check_tools_in_draft_orders(self, tool_codes: List[str]) -> Dict:
        """
        Check whether tools already exist in other draft orders.

        Args:
            tool_codes: List of tool serial numbers.

        Returns:
            Dictionary with draft order conflict details.
        """
        cleaned_codes = []
        seen_codes = set()
        for code in tool_codes or []:
            normalized = str(code).strip()
            if not normalized or normalized in seen_codes:
                continue
            seen_codes.add(normalized)
            cleaned_codes.append(normalized)

        if not cleaned_codes:
            return {"success": True, "draft_tools": []}

        code_placeholders = ",".join(["?"] * len(cleaned_codes))
        sql = f"""
        SELECT
            detail.[{ITEM_COLUMNS['tool_code']}] AS tool_code,
            detail.[{ITEM_COLUMNS['tool_name']}] AS tool_name,
            main.[{ORDER_COLUMNS['order_no']}] AS order_no,
            main.[{ORDER_COLUMNS['initiator_name']}] AS initiator_name,
            main.[{ORDER_COLUMNS['created_at']}] AS created_at
        FROM [{TABLE_NAMES['ORDER_ITEM']}] AS detail
        INNER JOIN [{TABLE_NAMES['ORDER']}] AS main
            ON main.[{ORDER_COLUMNS['order_no']}] = detail.[{ITEM_COLUMNS['order_no']}]
        WHERE detail.[{ITEM_COLUMNS['tool_code']}] IN ({code_placeholders})
          AND main.[{ORDER_COLUMNS['is_deleted']}] = 0
          AND main.[{ORDER_COLUMNS['order_status']}] = 'draft'
        ORDER BY main.[{ORDER_COLUMNS['created_at']}] DESC, main.[{ORDER_COLUMNS['order_no']}] DESC
        """
        rows = self._db.execute_query(sql, tuple(cleaned_codes))

        draft_tools = []
        seen_pairs = set()
        for row in rows:
            tool_code = str(row.get("tool_code", "")).strip()
            order_no = str(row.get("order_no", "")).strip()
            if not tool_code or not order_no:
                continue
            pair = (tool_code, order_no)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            draft_tools.append(
                {
                    "tool_code": tool_code,
                    "tool_name": row.get("tool_name", ""),
                    "order_no": order_no,
                    "initiator_name": row.get("initiator_name", ""),
                    "created_at": row.get("created_at"),
                }
            )

        return {"success": True, "draft_tools": draft_tools}

    def load_tool_master_map(self, tool_codes: List[str]) -> Dict[str, Dict]:
        """
        Load tool master rows from tool master table keyed by tool_code.

        Args:
            tool_codes: List of tool serial numbers

        Returns:
            Dictionary mapping tool_code to tool row
        """
        cleaned_codes = [str(code).strip() for code in tool_codes if str(code).strip()]
        if not cleaned_codes:
            return {}

        placeholders = ",".join(["?"] * len(cleaned_codes))
        sql = f"""
        SELECT
            [{TOOL_MASTER_COLUMNS['tool_code']}] AS tool_code,
            [{TOOL_MASTER_COLUMNS['tool_name']}] AS tool_name,
            [{TOOL_MASTER_COLUMNS['drawing_no']}] AS drawing_no,
            [{TOOL_MASTER_COLUMNS['spec_model']}] AS spec_model,
            [{TOOL_MASTER_COLUMNS['storage_location']}] AS current_location_text,
            [{TOOL_MASTER_COLUMNS['current_version']}] AS current_version,
            COALESCE([{TOOL_MASTER_COLUMNS['io_status']}], [{TOOL_MASTER_COLUMNS['available_status']}], [{TOOL_MASTER_COLUMNS['tool_valid_status']}], '') AS status_text
        FROM [{TOOL_MASTER_TABLE}]
        WHERE [{TOOL_MASTER_COLUMNS['tool_code']}] IN ({placeholders})
        """
        rows = self._db.execute_query(sql, tuple(cleaned_codes))
        return {str(row.get("tool_code", "")).strip(): row for row in rows}

    def _ensure_tool_status_history_table(self) -> None:
        """Create or align tool status change history table."""
        self._db.execute_query(
            f"""
            IF OBJECT_ID(N'{TOOL_STATUS_HISTORY_TABLE}', N'U') IS NULL
            BEGIN
                CREATE TABLE [{TOOL_STATUS_HISTORY_TABLE}] (
                    [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
                    [tool_code] NVARCHAR(100) NOT NULL,
                    [old_status] NVARCHAR(50) NOT NULL,
                    [new_status] NVARCHAR(50) NOT NULL,
                    [remark] NVARCHAR(500) NULL,
                    [operator_id] NVARCHAR(64) NOT NULL,
                    [operator_name] NVARCHAR(100) NOT NULL,
                    [change_time] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                    [client_ip] NVARCHAR(64) NULL
                )
            END
            """,
            fetch=False,
        )
        self._db.execute_query(
            f"""
            IF NOT EXISTS (
                SELECT 1 FROM sys.indexes
                WHERE name = N'IX_{TOOL_STATUS_HISTORY_TABLE}_tool_code_time'
                  AND object_id = OBJECT_ID(N'{TOOL_STATUS_HISTORY_TABLE}')
            )
            BEGIN
                CREATE INDEX [IX_{TOOL_STATUS_HISTORY_TABLE}_tool_code_time]
                ON [{TOOL_STATUS_HISTORY_TABLE}]([tool_code], [change_time] DESC)
            END
            """,
            fetch=False,
        )

    def update_tool_status_batch(
        self,
        tool_codes: List[str],
        new_status: str,
        operator: Dict,
        remark: str = None,
        client_ip: str = None,
    ) -> Dict:
        """
        Batch update tool status and persist status history.
        """
        normalized_status = str(new_status or "").strip().lower()
        if normalized_status not in ALLOWED_TOOL_STATUSES:
            return {"success": False, "error": "invalid new_status"}

        cleaned_codes: List[str] = []
        seen_codes = set()
        for code in tool_codes or []:
            normalized_code = str(code).strip()
            if not normalized_code or normalized_code in seen_codes:
                continue
            seen_codes.add(normalized_code)
            cleaned_codes.append(normalized_code)

        if not cleaned_codes:
            return {"success": False, "error": "tool_codes must contain at least one code"}

        self._ensure_tool_status_history_table()
        tool_map = self.load_tool_master_map(cleaned_codes)

        conn = None
        cursor = None
        records: List[Dict] = []
        missing_tool_codes = [code for code in cleaned_codes if code not in tool_map]
        operator_id = str((operator or {}).get("user_id", "")).strip()
        operator_name = str((operator or {}).get("display_name", "")).strip()

        try:
            conn = self._db.connect()
            cursor = conn.cursor()

            history_sql = f"""
            INSERT INTO [{TOOL_STATUS_HISTORY_TABLE}]
            ([tool_code], [old_status], [new_status], [remark], [operator_id], [operator_name], [client_ip])
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            update_sql_candidates = (
                f"UPDATE [{TOOL_MASTER_TABLE}] SET [{TOOL_MASTER_COLUMNS['io_status']}] = ? WHERE [{TOOL_MASTER_COLUMNS['tool_code']}] = ?",
            )

            for code in cleaned_codes:
                row = tool_map.get(code)
                if not row:
                    continue
                old_status = str(row.get("status_text", "") or "")
                updated = False
                for update_sql in update_sql_candidates:
                    try:
                        cursor.execute(update_sql, (normalized_status, code))
                        updated = cursor.rowcount > 0
                        break
                    except Exception:
                        continue
                if not updated:
                    continue
                cursor.execute(
                    history_sql,
                    (
                        code,
                        old_status,
                        normalized_status,
                        str(remark or "").strip() or None,
                        operator_id,
                        operator_name,
                        str(client_ip or "").strip() or None,
                    ),
                )
                records.append(
                    {
                        "tool_code": code,
                        "old_status": old_status,
                        "new_status": normalized_status,
                    }
                )

            conn.commit()
        except Exception:
            if conn is not None:
                conn.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._db.close(conn)

        return {
            "success": True,
            "updated_count": len(records),
            "records": records,
            "missing_tool_codes": missing_tool_codes,
        }

    def get_tool_status_history(
        self,
        tool_code: str,
        page_no: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """
        Query one tool status change history with pagination.
        """
        normalized_code = str(tool_code or "").strip()
        if not normalized_code:
            return {"success": False, "error": "tool_code is required"}

        page_no = max(int(page_no or 1), 1)
        page_size = max(int(page_size or 20), 1)
        offset = (page_no - 1) * page_size

        self._ensure_tool_status_history_table()
        total_rows = self._db.execute_query(
            f"SELECT COUNT(1) AS total FROM [{TOOL_STATUS_HISTORY_TABLE}] WHERE [tool_code] = ?",
            (normalized_code,),
        )
        total = int((total_rows[0] if total_rows else {}).get("total", 0))
        rows = self._db.execute_query(
            f"""
            SELECT
                [old_status] AS old_status,
                [new_status] AS new_status,
                [remark] AS remark,
                [operator_id] AS operator_id,
                [operator_name] AS operator_name,
                [change_time] AS change_time,
                [client_ip] AS client_ip
            FROM [{TOOL_STATUS_HISTORY_TABLE}]
            WHERE [tool_code] = ?
            ORDER BY [change_time] DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """,
            (normalized_code, offset, page_size),
        )
        return {
            "success": True,
            "data": rows,
            "total": total,
            "page_no": page_no,
            "page_size": page_size,
        }
