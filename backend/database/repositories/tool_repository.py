# -*- coding: utf-8 -*-
"""
Tool repository for tool master data queries.
"""

import logging
from typing import List, Dict, Optional

from backend.database.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ToolRepository:
    """Repository for tool master data operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def get_tool_basic_info(self) -> List[Dict]:
        """
        Get basic tool information from 工装身份卡_主表.

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
        sql = """
            SELECT
                m.序列号,
                m.工装图号,
                m.工装名称,
                m.当前版次,
                m.制造版次,
                m.制造日期,
                m.定检周期,
                m.定检属性,
                m.定检有效截止,
                m.定检派工状态,
                m.定检有效期剩余天,
                m.应用历史,
                m.库位,
                m.出入库状态,
                m.可用状态,
                m.工装有效状态
            FROM 工装身份卡_主表 m
            WHERE m.序列号 = ?
        """
        results = self._db.execute_query(sql, (serial_no,))
        return results[0] if results else None

    def search_tools(
        self,
        keyword: str = None,
        status: str = None,
        location_id: int = None,
        page_no: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Search tools with filters.

        Args:
            keyword: Search keyword
            status: Filter by status
            location_id: Filter by location
            page_no: Page number
            page_size: Page size

        Returns:
            Dictionary with data, total, page info
        """
        # Determine column names based on schema
        serial_column = '[序列号]'
        spec_model_column = '[机型]'

        probe_sql = """
        SELECT
            CASE WHEN COL_LENGTH(N'工装身份卡_主表', N'序列号') IS NOT NULL THEN 1 ELSE 0 END AS has_serial,
            CASE WHEN COL_LENGTH(N'工装身份卡_主表', N'机型') IS NOT NULL THEN 1 ELSE 0 END AS has_spec_model
        """
        probe = self._db.execute_query(probe_sql)
        if probe:
            if not probe[0].get('has_serial'):
                serial_column = '[序号]'
            if probe[0].get('has_spec_model'):
                spec_model_column = '[机型]'

        conditions = [f"{serial_column} IS NOT NULL", f"LTRIM(RTRIM({serial_column})) <> ''"]
        params = []

        if keyword:
            keyword_like = f"%{keyword.strip()}%"
            conditions.append(
                f"""
                (
                    {serial_column} LIKE ?
                    OR [工装图号] LIKE ?
                    OR [工装名称] LIKE ?
                    OR {spec_model_column} LIKE ?
                    OR [库位] LIKE ?
                    OR [定检派工状态] LIKE ?
                    OR [应用历史] LIKE ?
                )
                """
            )
            params.extend([keyword_like] * 7)

        if status:
            status_like = f"%{status.strip()}%"
            conditions.append(
                """
                (
                    [定检派工状态] LIKE ?
                    OR [出入库状态] LIKE ?
                    OR [可用状态] LIKE ?
                )
                """
            )
            params.extend([status_like, status_like, status_like])

        if location_id not in (None, ''):
            location_like = f"%{str(location_id).strip()}%"
            conditions.append(
                """
                (
                    [库位] LIKE ?
                    OR [位置ID] LIKE ?
                )
                """
            )
            params.extend([location_like, location_like])

        where_clause = ' AND '.join(conditions)
        count_sql = f"SELECT COUNT(*) AS total FROM [工装身份卡_主表] WHERE {where_clause}"
        count_result = self._db.execute_query(count_sql, tuple(params))
        total = int(count_result[0].get('total', 0)) if count_result else 0

        offset = max(page_no - 1, 0) * page_size
        list_sql = f"""
        SELECT
            {serial_column} AS tool_code,
            {serial_column} AS tool_id,
            [工装图号] AS drawing_no,
            [工装名称] AS tool_name,
            {spec_model_column} AS spec_model,
            [当前版次] AS current_version,
            [库位] AS current_location_text,
            [应用历史] AS application_history,
            [可用状态] AS available_status,
            [工装有效状态] AS valid_status,
            [出入库状态] AS io_status,
            [定检周期] AS inspection_cycle,
            [定检有效截止] AS inspection_expiry_date,
            COALESCE([出入库状态], [可用状态], [工装有效状态], '') AS status_text
        FROM [工装身份卡_主表]
        WHERE {where_clause}
        ORDER BY {serial_column}
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
            detail.[序列号] AS tool_code,
            detail.[工装名称] AS tool_name,
            main.[出入库单号] AS order_no,
            main.[单据类型] AS order_type,
            main.[单据状态] AS order_status,
            main.[发起人姓名] AS initiator_name,
            main.[创建时间] AS created_at
        FROM [工装出入库单_明细] AS detail
        INNER JOIN [工装出入库单_主表] AS main
            ON main.[出入库单号] = detail.[出入库单号]
        WHERE detail.[序列号] IN ({code_placeholders})
          AND main.[IS_DELETED] = 0
          AND main.[单据状态] IN ({status_placeholders})
        """
        params = list(cleaned_codes) + list(TOOL_LOCKED_ORDER_STATUSES)

        normalized_exclude_order_no = str(exclude_order_no or "").strip()
        if normalized_exclude_order_no:
            sql += " AND main.[出入库单号] <> ?"
            params.append(normalized_exclude_order_no)

        sql += " ORDER BY main.[创建时间] DESC, main.[出入库单号] DESC"
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

    def load_tool_master_map(self, tool_codes: List[str]) -> Dict[str, Dict]:
        """
        Load tool master rows from 工装身份卡_主表 keyed by 序列号.

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
            [序列号] AS tool_code,
            [工装名称] AS tool_name,
            [工装图号] AS drawing_no,
            [机型] AS spec_model,
            [库位] AS current_location_text,
            [当前版次] AS current_version,
            COALESCE([出入库状态], [可用状态], [工装有效状态], '') AS status_text
        FROM [工装身份卡_主表]
        WHERE [序列号] IN ({placeholders})
        """
        rows = self._db.execute_query(sql, tuple(cleaned_codes))
        return {str(row.get("tool_code", "")).strip(): row for row in rows}
