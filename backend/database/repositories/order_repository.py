# -*- coding: utf-8 -*-
"""
Order repository for Tool IO order operations.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import (
    ORDER_COLUMNS,
    ITEM_COLUMNS,
    LOG_COLUMNS,
    NOTIFY_COLUMNS,
    TABLE_NAMES,
    TOOL_MASTER_COLUMNS,
    TOOL_MASTER_TABLE,
)
from backend.database.utils.sql_utils import safe_bigint

logger = logging.getLogger(__name__)


# Tool action types
class ToolIOAction:
    CREATE = "create"
    SUBMIT = "submit"
    KEEPER_CONFIRM = "keeper_confirm"
    FINAL_CONFIRM = "final_confirm"
    COMPLETE = "complete"
    REJECT = "reject"
    CANCEL = "cancel"
    DELETE = "delete"
    EDIT = "edit"


def _get_serial_no(item: Dict[str, Any]) -> str:
    """Read serial number from new or legacy payload fields."""
    return str(item.get("serial_no") or item.get("tool_code") or "").strip()


class OrderRepository:
    """Repository for Tool IO order operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def create_order(self, order_data: dict) -> dict:
        """
        Create a new tool IO order.

        Args:
            order_data: Order data dictionary

        Returns:
            Result dictionary with success status
        """
        try:
            from backend.database.services.order_service import generate_order_no_atomic
            from backend.database.repositories.tool_repository import ToolRepository

            items = order_data.get("items")
            if not isinstance(items, list) or not items:
                return {"success": False, "error": "请至少选择一项工装"}

            order_type = order_data.get("order_type")
            if order_type not in {"outbound", "inbound"}:
                return {"success": False, "error": "单据类型不正确"}

            serial_nos = [_get_serial_no(item) for item in items if _get_serial_no(item)]
            if len(serial_nos) != len(items):
                return {"success": False, "error": "每条明细都必须包含序列号"}
            if len(set(serial_nos)) != len(serial_nos):
                return {"success": False, "error": "同一张单据内不能重复选择相同序列号"}

            # Check tool availability
            tool_repo = ToolRepository(self._db)
            try:
                tool_master_map = tool_repo.load_tool_master_map(serial_nos)
            except Exception as exc:
                logger.warning("加载工装主表失败，创建单据时回退到请求快照: %s", exc)
                tool_master_map = {}

            missing_codes = [code for code in serial_nos if code not in tool_master_map]
            for item in items:
                serial_no = _get_serial_no(item)
                if serial_no in missing_codes:
                    tool_master_map[serial_no] = {
                        "serial_no": serial_no,
                        "tool_name": item.get("tool_name", ""),
                        "drawing_no": item.get("drawing_no", ""),
                        "spec_model": item.get("spec_model", ""),
                        "current_location_text": item.get("current_location_text", ""),
                        "status_text": item.get("status_text", ""),
                    }

            missing_codes = [code for code in serial_nos if code not in tool_master_map]
            if missing_codes:
                return {"success": False, "error": f"以下工装不存在：{', '.join(missing_codes)}"}

            occupied = tool_repo.check_tools_available(serial_nos)
            if not occupied.get("available", True):
                return {"success": False, "error": self._build_tool_occupied_error(occupied.get("occupied_tools", [])), "occupied_tools": occupied.get("occupied_tools", [])}
            draft_conflicts = tool_repo.check_tools_in_draft_orders(serial_nos)
            warning_message = self._build_tool_draft_warning(draft_conflicts.get("draft_tools", []))

            order_no = generate_order_no_atomic(order_type)

            def _create_order_tx(conn: Any) -> None:
                insert_order_sql = f"""
                INSERT INTO [tool_io_order] (
                    [order_no], [order_type], [order_status], [initiator_id], [initiator_name], [initiator_role],
                    [department], [project_code], [usage_purpose], [planned_use_time], [planned_return_time],
                    [target_location_id], [target_location_text], [remark], [tool_quantity], [confirmed_count], [org_id],
                    [{ORDER_COLUMNS['created_at']}], [{ORDER_COLUMNS['updated_at']}], [{ORDER_COLUMNS['created_by']}], [{ORDER_COLUMNS['updated_by']}], [{ORDER_COLUMNS['is_deleted']}]
                ) VALUES (?, ?, 'draft', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), ?, ?, 0)
                """
                self._db.execute_query(
                    insert_order_sql,
                    (
                        order_no,
                        order_type,
                        order_data.get("initiator_id"),
                        order_data.get("initiator_name"),
                        order_data.get("initiator_role"),
                        order_data.get("department"),
                        order_data.get("project_code"),
                        order_data.get("usage_purpose"),
                        order_data.get("planned_use_time"),
                        order_data.get("planned_return_time"),
                        order_data.get("target_location_id"),
                        order_data.get("target_location_text"),
                        order_data.get("remark"),
                        len(items),
                        0,
                        order_data.get("org_id"),
                        order_data.get("initiator_name"),
                        order_data.get("initiator_name"),
                    ),
                    fetch=False,
                    conn=conn,
                )

                insert_item_sql = """
                INSERT INTO [tool_io_order_item] (
                    [order_no], [tool_id], [serial_no], [tool_name], [drawing_no], [spec_model],
                    [apply_qty], [confirmed_qty], [item_status], [tool_snapshot_status], [tool_snapshot_location_text],
                    [sort_order], [created_at], [updated_at]
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending_check', ?, ?, ?, GETDATE(), GETDATE())
                """
                for idx, item in enumerate(items, start=1):
                    serial_no = _get_serial_no(item)
                    tool_row = tool_master_map[serial_no]
                    self._db.execute_query(
                        insert_item_sql,
                        (
                            order_no,
                            safe_bigint(item.get("tool_id")),
                            serial_no,
                            item.get("tool_name") or tool_row.get("tool_name"),
                            item.get("drawing_no") or tool_row.get("drawing_no"),
                            item.get("spec_model") or tool_row.get("spec_model"),
                            item.get("apply_qty") or 1,
                            0,
                            tool_row.get("status_text"),
                            tool_row.get("current_location_text"),
                            idx,
                        ),
                        fetch=False,
                        conn=conn,
                    )

                self.add_tool_io_log({
                    "order_no": order_no,
                    "action_type": ToolIOAction.CREATE,
                    "operator_id": order_data.get("initiator_id"),
                    "operator_name": order_data.get("initiator_name"),
                    "operator_role": order_data.get("initiator_role"),
                    "before_status": "",
                    "after_status": "draft",
                    "content": f"创建出入库单，单号：{order_no}",
                }, conn=conn)

            self._db.execute_with_transaction(_create_order_tx)

            result = {"success": True, "order_no": order_no}
            if warning_message:
                result["warning"] = warning_message
            return result

        except Exception as e:
            logger.error(f"创建出入库单失败: {e}")
            return {"success": False, "error": str(e)}

    def update_order(
        self,
        order_no: str,
        payload: Dict,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Update order content (items, remark) when order is in draft status.

        Args:
            order_no: Order number
            payload: Update payload with items (list) and/or remark
            operator_id: Operator ID (must be the order initiator)
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            # Check order exists and is in draft status
            check_sql = f"""
            SELECT [{ORDER_COLUMNS['order_status']}], [{ORDER_COLUMNS['initiator_id']}]
            FROM [{TABLE_NAMES['ORDER']}]
            WHERE [{ORDER_COLUMNS['order_no']}] = ? AND [{ORDER_COLUMNS['is_deleted']}] = 0
            """
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('order_status')
            if current_status != 'draft':
                return {'success': False, 'error': f'只有草稿状态的订单可以编辑，当前状态：{current_status}'}

            items = payload.get('items')
            header_keys = {
                'order_type',
                'department',
                'project_code',
                'usage_purpose',
                'planned_use_time',
                'planned_return_time',
                'target_location_id',
                'target_location_text',
                'remark',
            }
            has_header_updates = any(key in payload for key in header_keys)

            # Update order header fields if provided
            if has_header_updates:
                next_tool_quantity = len(items) if items is not None else None
                update_header_sql = f"""
                UPDATE [{TABLE_NAMES['ORDER']}] SET
                    [{ORDER_COLUMNS['order_type']}] = COALESCE(?, [{ORDER_COLUMNS['order_type']}]),
                    [{ORDER_COLUMNS['department']}] = COALESCE(?, [{ORDER_COLUMNS['department']}]),
                    [{ORDER_COLUMNS['project_code']}] = COALESCE(?, [{ORDER_COLUMNS['project_code']}]),
                    [{ORDER_COLUMNS['usage_purpose']}] = COALESCE(?, [{ORDER_COLUMNS['usage_purpose']}]),
                    [{ORDER_COLUMNS['planned_use_time']}] = COALESCE(?, [{ORDER_COLUMNS['planned_use_time']}]),
                    [{ORDER_COLUMNS['planned_return_time']}] = COALESCE(?, [{ORDER_COLUMNS['planned_return_time']}]),
                    [{ORDER_COLUMNS['target_location_id']}] = COALESCE(?, [{ORDER_COLUMNS['target_location_id']}]),
                    [{ORDER_COLUMNS['target_location_text']}] = COALESCE(?, [{ORDER_COLUMNS['target_location_text']}]),
                    [{ORDER_COLUMNS['remark']}] = ?,
                    [{ORDER_COLUMNS['tool_quantity']}] = COALESCE(?, [{ORDER_COLUMNS['tool_quantity']}]),
                    [{ORDER_COLUMNS['updated_at']}] = GETDATE()
                WHERE [{ORDER_COLUMNS['order_no']}] = ?
                """
                self._db.execute_query(
                    update_header_sql,
                    (
                        payload.get('order_type'),
                        payload.get('department'),
                        payload.get('project_code'),
                        payload.get('usage_purpose'),
                        payload.get('planned_use_time'),
                        payload.get('planned_return_time'),
                        payload.get('target_location_id'),
                        payload.get('target_location_text'),
                        payload.get('remark'),
                        next_tool_quantity,
                        order_no,
                    ),
                    fetch=False,
                )

            # Update items if provided
            if items is not None:
                # Delete existing items
                delete_items_sql = f"DELETE FROM [{TABLE_NAMES['ITEM']}] WHERE [{ORDER_COLUMNS['order_no']}] = ?"
                self._db.execute_query(delete_items_sql, (order_no,), fetch=False)

                # Re-fetch tool master data for validation
                serial_nos = [_get_serial_no(item) for item in items if _get_serial_no(item)]
                if serial_nos:
                    from backend.database.repositories.tool_repository import ToolRepository
                    tool_repo = ToolRepository(self._db)
                    tool_master_map = tool_repo.load_tool_master_map(serial_nos)

                    # Insert new items
                    insert_item_sql = f"""
                    INSERT INTO [{TABLE_NAMES['ITEM']}] (
                        [{ITEM_COLUMNS['order_no']}], [{ITEM_COLUMNS['tool_id']}], [{ITEM_COLUMNS['serial_no']}],
                        [{ITEM_COLUMNS['tool_name']}], [{ITEM_COLUMNS['drawing_no']}], [{ITEM_COLUMNS['spec_model']}],
                        [{ITEM_COLUMNS['apply_qty']}], [{ITEM_COLUMNS['confirmed_qty']}], [{ITEM_COLUMNS['item_status']}],
                        [{ITEM_COLUMNS['tool_snapshot_status']}], [{ITEM_COLUMNS['tool_snapshot_location_text']}],
                        [{ITEM_COLUMNS['sort_order']}], [{ITEM_COLUMNS['created_at']}], [{ITEM_COLUMNS['updated_at']}]
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'pending_check', ?, ?, ?, GETDATE(), GETDATE())
                    """
                    for idx, item in enumerate(items, start=1):
                        serial_no = _get_serial_no(item)
                        tool_row = tool_master_map.get(serial_no, {})
                        self._db.execute_query(
                            insert_item_sql,
                            (
                                order_no,
                                safe_bigint(item.get("tool_id")),
                                serial_no,
                                item.get("tool_name") or tool_row.get("tool_name"),
                                item.get("drawing_no") or tool_row.get("drawing_no"),
                                item.get("spec_model") or tool_row.get("spec_model"),
                                item.get("apply_qty") or 1,
                                tool_row.get("status_text"),
                                tool_row.get("current_location_text"),
                                idx,
                            ),
                            fetch=False,
                        )

            # Log the update
            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.EDIT,
                'operator_id': operator_id,
                'operator_name': operator_name,
                'operator_role': operator_role,
                'before_status': current_status,
                'after_status': current_status,
                'content': '编辑订单内容'
            })

            return {'success': True, 'order_no': order_no}

        except Exception as e:
            logger.error(f"更新订单失败: {e}")
            return {'success': False, 'error': str(e)}

    def submit_order(self, order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
        """
        Submit a draft order.

        Args:
            order_no: Order number
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            from backend.database.repositories.tool_repository import ToolRepository

            status_rows = self._db.execute_query(
                """
                SELECT [order_status]
                FROM [tool_io_order]
                WHERE [order_no] = ? AND [IS_DELETED] = 0
                """,
                (order_no,),
            )
            if not status_rows:
                return {"success": False, "error": "订单不存在", "error_code": "ORDER_NOT_FOUND"}

            current_status = status_rows[0].get("order_status")
            if current_status == "submitted":
                return {
                    "success": True,
                    "order_no": order_no,
                    "status": "submitted",
                    "idempotent": True,
                }
            if current_status != "draft":
                return {
                    "success": False,
                    "error": f"当前状态不允许提交：{current_status}",
                    "error_code": "ORDER_STATUS_CONFLICT",
                    "current_status": current_status,
                }

            # Check items exist
            detail_rows = self._db.execute_query(
                "SELECT [serial_no] AS serial_no FROM [tool_io_order_item] WHERE [order_no] = ?",
                (order_no,),
            )
            if not detail_rows:
                return {"success": False, "error": "单据没有工装明细"}

            serial_nos = [str(row.get("serial_no", "")).strip() for row in detail_rows if str(row.get("serial_no", "")).strip()]

            # Check tool availability
            tool_repo = ToolRepository(self._db)
            occupied = tool_repo.check_tools_available(serial_nos, exclude_order_no=order_no)
            if not occupied.get("available", True):
                return {"success": False, "error": self._build_tool_occupied_error(occupied.get("occupied_tools", [])), "occupied_tools": occupied.get("occupied_tools", [])}

            def _submit_order_tx(conn: Any) -> None:
                check_sql = """
                SELECT [order_status]
                FROM [tool_io_order]
                WHERE [order_no] = ? AND [IS_DELETED] = 0
                """
                result = self._db.execute_query(check_sql, (order_no,), conn=conn)
                if not result:
                    raise ValueError("单据不存在")

                current_status = result[0].get("order_status")
                if current_status != "draft":
                    raise ValueError(f"当前状态不允许提交：{current_status}")

                update_sql = """
                UPDATE [tool_io_order]
                SET [order_status] = 'submitted',
                    [updated_at] = GETDATE(),
                    [updated_by] = ?
                WHERE [order_no] = ?
                """
                self._db.execute_query(update_sql, (operator_name, order_no), fetch=False, conn=conn)

                self.add_tool_io_log({
                    "order_no": order_no,
                    "action_type": ToolIOAction.SUBMIT,
                    "operator_id": operator_id,
                    "operator_name": operator_name,
                    "operator_role": operator_role,
                    "before_status": "draft",
                    "after_status": "submitted",
                    "content": "提交单据，等待保管员确认",
                }, conn=conn)

            self._db.execute_with_transaction(_submit_order_tx)

            return {"success": True, "order_no": order_no, "status": "submitted"}

        except Exception as e:
            logger.error(f"提交出入库单失败: {e}")
            return {"success": False, "error": str(e)}

    def get_order(self, order_no: str) -> Dict:
        """
        Get order details.

        Args:
            order_no: Order number

        Returns:
            Order dictionary
        """
        try:
            sql = f"SELECT * FROM [{TABLE_NAMES['ORDER']}] WHERE [{ORDER_COLUMNS['order_no']}] = ?"
            result = self._db.execute_query(sql, (order_no,))
            if not result:
                return {}

            order = result[0]

            # Get items
            items_sql = f"""
            SELECT
                i.*,
                m.[{TOOL_MASTER_COLUMNS['split_quantity']}] AS split_quantity
            FROM [{TABLE_NAMES['ORDER_ITEM']}] i
            LEFT JOIN [{TOOL_MASTER_TABLE}] m
                ON i.[{ITEM_COLUMNS['serial_no']}] = m.[{TOOL_MASTER_COLUMNS['tool_code']}]
            WHERE i.[{ITEM_COLUMNS['order_no']}] = ?
            ORDER BY i.[{ITEM_COLUMNS['sort_order']}]
            """
            items = self._db.execute_query(items_sql, (order_no,))
            order['items'] = items

            return order

        except Exception as e:
            logger.error(f"获取出入库单详情失败: {e}")
            return {}

    def get_order_by_no(self, order_no: str) -> Dict:
        """Alias for get_order for backward compatibility."""
        return self.get_order(order_no)

    def get_orders(
        self,
        order_type: str = None,
        order_status: str = None,
        initiator_id: str = None,
        keeper_id: str = None,
        keyword: str = None,
        date_from: str = None,
        date_to: str = None,
        page_no: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        Query orders with filters.

        Args:
            order_type: Filter by order type
            order_status: Filter by order status
            initiator_id: Filter by initiator
            keeper_id: Filter by keeper
            keyword: Search keyword
            date_from: Start date
            date_to: End date
            page_no: Page number
            page_size: Page size

        Returns:
            Dictionary with orders and total count
        """
        try:
            conditions = [f"{ORDER_COLUMNS['is_deleted']} = 0"]
            params = []

            if order_type:
                conditions.append(f"{ORDER_COLUMNS['order_type']} = ?")
                params.append(order_type)

            if order_status:
                conditions.append(f"{ORDER_COLUMNS['order_status']} = ?")
                params.append(order_status)

            if initiator_id:
                conditions.append(f"{ORDER_COLUMNS['initiator_id']} = ?")
                params.append(initiator_id)

            if keeper_id:
                conditions.append(f"{ORDER_COLUMNS['keeper_id']} = ?")
                params.append(keeper_id)

            if keyword:
                conditions.append(f"({ORDER_COLUMNS['order_no']} LIKE ? OR {ORDER_COLUMNS['initiator_name']} LIKE ? OR {ORDER_COLUMNS['remark']} LIKE ?)")
                keyword_like = f"%{keyword}%"
                params.extend([keyword_like, keyword_like, keyword_like])

            if date_from:
                conditions.append(f"{ORDER_COLUMNS['created_at']} >= ?")
                params.append(date_from)

            if date_to:
                conditions.append(f"{ORDER_COLUMNS['created_at']} <= ?")
                params.append(date_to)

            where_clause = " AND ".join(conditions)

            # Count
            count_sql = f"SELECT COUNT(*) AS total FROM [tool_io_order] WHERE {where_clause}"
            count_result = self._db.execute_query(count_sql, tuple(params))
            total = count_result[0].get('total', 0) if count_result else 0

            # Query - use explicit column names with English aliases
            offset = max(page_no - 1, 0) * page_size
            columns = [
                "[id]",
                "[order_no] AS [order_no]",
                "[order_type] AS [order_type]",
                "[order_status] AS [order_status]",
                "[initiator_id] AS [initiator_id]",
                "[initiator_name] AS [initiator_name]",
                "[initiator_role] AS [initiator_role]",
                "[department] AS [department]",
                "[project_code] AS [project_code]",
                "[usage_purpose] AS [usage_purpose]",
                "[planned_use_time] AS [planned_use_time]",
                "[planned_return_time] AS [planned_return_time]",
                "[target_location_id] AS [target_location_id]",
                "[target_location_text] AS [target_location_text]",
                "[keeper_id] AS [keeper_id]",
                "[keeper_name] AS [keeper_name]",
                "[transport_type] AS [transport_type]",
                "[transport_operator_id] AS [transport_operator_id]",
                "[transport_operator_name] AS [transport_operator_name]",
                "[keeper_confirm_time] AS [keeper_confirm_time]",
                "[final_confirm_time] AS [final_confirm_time]",
                "[tool_quantity] AS [tool_count]",
                "[confirmed_count] AS [approved_count]",
                "[reject_reason] AS [reject_reason]",
                "[remark] AS [remark]",
                "[created_at] AS [created_at]",
                "[updated_at] AS [updated_at]",
                "[created_by] AS [created_by]",
                "[updated_by] AS [updated_by]",
                "[is_deleted] AS [is_deleted]"
            ]
            sql = f"""
            SELECT {', '.join(columns)} FROM [{TABLE_NAMES['ORDER']}]
            WHERE {where_clause}
            ORDER BY [{ORDER_COLUMNS['created_at']}] DESC
            OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
            """
            rows = self._db.execute_query(sql, tuple(params))

            return {'success': True, 'data': rows, 'total': total, 'page_no': page_no, 'page_size': page_size}

        except Exception as e:
            logger.error(f"查询出入库单列表失败: {e}")
            return {'success': False, 'error': str(e), 'data': [], 'total': 0}

    def keeper_confirm(
        self,
        order_no: str,
        keeper_id: str,
        keeper_name: str,
        confirm_data: dict,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Keeper confirmation for an order.

        Args:
            order_no: Order number
            keeper_id: Keeper ID
            keeper_name: Keeper name
            confirm_data: Confirmation data
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            if not isinstance(confirm_data, dict):
                return {'success': False, 'error': 'confirm_data must be an object'}

            items = confirm_data.get('items')
            if not isinstance(items, list) or not items:
                return {'success': False, 'error': 'confirm_data.items must contain at least one item'}

            tx_result = {"approved_count": 0, "status": ""}

            def _keeper_confirm_tx(conn: Any) -> None:
                check_sql = f"SELECT [{ORDER_COLUMNS['order_type']}], [{ORDER_COLUMNS['order_status']}] FROM [{TABLE_NAMES['ORDER']}] WHERE [{ORDER_COLUMNS['order_no']}] = ?"
                result = self._db.execute_query(check_sql, (order_no,), conn=conn)
                if not result:
                    raise ValueError('单据不存在')

                current_status = result[0].get('order_status')
                if current_status not in ['submitted', 'partially_confirmed']:
                    raise ValueError(f'当前状态不允许确认，当前状态：{current_status}')

                approved_count = 0
                updated_items_count = 0
                for item in items:
                    item_id = item.get('item_id')
                    if not item_id:
                        logger.warning(f"keeper_confirm: item_id missing for order {order_no}, skipping item update")
                        continue

                    item_sql = f"""
                    UPDATE [{TABLE_NAMES['ORDER_ITEM']}] SET
                        [{ITEM_COLUMNS['confirm_by_id']}] = ?,
                        [{ITEM_COLUMNS['confirm_by_name']}] = ?,
                        [{ITEM_COLUMNS['confirm_time']}] = GETDATE(),
                        [{ITEM_COLUMNS['confirmed_qty']}] = ?,
                        [{ITEM_COLUMNS['item_status']}] = ?,
                        [{ITEM_COLUMNS['reject_reason']}] = ?,
                        [{ITEM_COLUMNS['updated_at']}] = GETDATE()
                    WHERE [{ITEM_COLUMNS['order_no']}] = ? AND id = ?
                    """
                    status = item.get('status', 'approved')
                    if status == 'approved':
                        approved_count += 1
                    reject_reason = ''
                    if status != 'approved':
                        reject_reason = str(item.get('reject_reason') or item.get('check_remark') or '').strip()

                    self._db.execute_query(item_sql, (
                        item.get('keeper_confirm_location_id') or item.get('location_id'),
                        keeper_name,
                        item.get('confirmed_qty', item.get('approved_qty', 1)),
                        status,
                        reject_reason or None,
                        order_no,
                        item_id
                    ), fetch=False, conn=conn)
                    updated_items_count += 1

                if updated_items_count == 0:
                    logger.error(f"keeper_confirm: no items were updated for order {order_no}")
                    raise ValueError('no items were updated - check item identifiers')

                new_status = 'keeper_confirmed' if approved_count == len(items) else 'partially_confirmed'
                update_sql = f"""
                UPDATE [{TABLE_NAMES['ORDER']}] SET
                    [{ORDER_COLUMNS['order_status']}] = ?,
                    [{ORDER_COLUMNS['keeper_id']}] = ?,
                    [{ORDER_COLUMNS['keeper_name']}] = ?,
                    [{ORDER_COLUMNS['transport_type']}] = ?,
                    [{ORDER_COLUMNS['transport_operator_id']}] = ?,
                    [{ORDER_COLUMNS['transport_operator_name']}] = ?,
                    [{ORDER_COLUMNS['keeper_confirm_time']}] = GETDATE(),
                    [{ORDER_COLUMNS['confirmed_count']}] = ?,
                    [{ORDER_COLUMNS['updated_at']}] = GETDATE()
                WHERE [{ORDER_COLUMNS['order_no']}] = ?
                """
                self._db.execute_query(update_sql, (
                    new_status,
                    keeper_id,
                    keeper_name,
                    confirm_data.get('transport_type'),
                    confirm_data.get('transport_assignee_id'),
                    confirm_data.get('transport_assignee_name'),
                    approved_count,
                    order_no
                ), fetch=False, conn=conn)

                self.add_tool_io_log({
                    'order_no': order_no,
                    'action_type': ToolIOAction.KEEPER_CONFIRM,
                    'operator_id': operator_id,
                    'operator_name': operator_name,
                    'operator_role': operator_role,
                    'before_status': current_status,
                    'after_status': new_status,
                    'content': f'保管员确认，通过 {approved_count}/{len(items)} 项'
                }, conn=conn)

                tx_result["approved_count"] = approved_count
                tx_result["status"] = new_status

            self._db.execute_with_transaction(_keeper_confirm_tx)

            return {'success': True, 'status': tx_result["status"], 'approved_count': tx_result["approved_count"]}

        except Exception as e:
            logger.error(f"保管员确认失败: {e}")
            return {'success': False, 'error': str(e)}

    def final_confirm(
        self,
        order_no: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Final confirmation for an order.

        Args:
            order_no: Order number
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            def _final_confirm_tx(conn: Any) -> None:
                check_sql = f"SELECT [{ORDER_COLUMNS['order_type']}], [{ORDER_COLUMNS['order_status']}] FROM [{TABLE_NAMES['ORDER']}] WHERE [{ORDER_COLUMNS['order_no']}] = ?"
                result = self._db.execute_query(check_sql, (order_no,), conn=conn)
                if not result:
                    raise ValueError('单据不存在')

                order_type = result[0].get('order_type')
                current_status = result[0].get('order_status')

                if current_status not in ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'transport_completed', 'final_confirmation_pending']:
                    raise ValueError(f'当前状态不允许最终确认，当前状态：{current_status}')

                sql = f"""
                UPDATE [{TABLE_NAMES['ORDER']}] SET
                    [{ORDER_COLUMNS['order_status']}] = 'completed',
                    [{ORDER_COLUMNS['final_confirm_by']}] = ?,
                    [{ORDER_COLUMNS['final_confirm_time']}] = GETDATE(),
                    [{ORDER_COLUMNS['updated_at']}] = GETDATE()
                WHERE [{ORDER_COLUMNS['order_no']}] = ?
                """
                self._db.execute_query(sql, (operator_name, order_no), fetch=False, conn=conn)

                update_items_sql = f"""
                UPDATE [{TABLE_NAMES['ORDER_ITEM']}] SET
                    [{ITEM_COLUMNS['item_status']}] = 'completed',
                    [{ITEM_COLUMNS['io_complete_time']}] = GETDATE(),
                    [{ITEM_COLUMNS['updated_at']}] = GETDATE()
                WHERE [{ITEM_COLUMNS['order_no']}] = ? AND [{ITEM_COLUMNS['item_status']}] = 'approved'
                """
                self._db.execute_query(update_items_sql, (order_no,), fetch=False, conn=conn)

                self.add_tool_io_log({
                    'order_no': order_no,
                    'action_type': ToolIOAction.COMPLETE,
                    'operator_id': operator_id,
                    'operator_name': operator_name,
                    'operator_role': operator_role,
                    'before_status': current_status,
                    'after_status': 'completed',
                    'content': f'出入库完成，类型：{order_type}'
                }, conn=conn)

            self._db.execute_with_transaction(_final_confirm_tx)

            return {'success': True}

        except Exception as e:
            logger.error(f"最终确认失败: {e}")
            return {'success': False, 'error': str(e)}

    def reject_order(
        self,
        order_no: str,
        reject_reason: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Reject an order.

        Args:
            order_no: Order number
            reject_reason: Rejection reason
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            check_sql = f"SELECT [{ORDER_COLUMNS['order_status']}] FROM [{TABLE_NAMES['ORDER']}] WHERE [{ORDER_COLUMNS['order_no']}] = ?"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('order_status')
            if current_status not in ['submitted', 'keeper_confirmed', 'partially_confirmed']:
                return {'success': False, 'error': f'当前状态不允许驳回，当前状态：{current_status}'}

            # Update status
            sql = f"""
            UPDATE [{TABLE_NAMES['ORDER']}] SET
                [{ORDER_COLUMNS['order_status']}] = 'rejected',
                [{ORDER_COLUMNS['reject_reason']}] = ?,
                [{ORDER_COLUMNS['updated_at']}] = GETDATE()
            WHERE [{ORDER_COLUMNS['order_no']}] = ?
            """
            self._db.execute_query(sql, (reject_reason, order_no), fetch=False)

            # Update items
            update_items_sql = f"""
            UPDATE [{TABLE_NAMES['ORDER_ITEM']}] SET
                [{ITEM_COLUMNS['item_status']}] = 'rejected',
                [{ITEM_COLUMNS['updated_at']}] = GETDATE()
            WHERE [{ITEM_COLUMNS['order_no']}] = ?
            """
            self._db.execute_query(update_items_sql, (order_no,), fetch=False)

            # Log
            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.REJECT,
                'operator_id': operator_id,
                'operator_name': operator_name,
                'operator_role': operator_role,
                'before_status': current_status,
                'after_status': 'rejected',
                'content': f'驳回原因：{reject_reason}'
            })

            return {'success': True}

        except Exception as e:
            logger.error(f"驳回单据失败: {e}")
            return {'success': False, 'error': str(e)}

    def reset_order_to_draft(
        self,
        order_no: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Reset a rejected order back to draft status.

        Args:
            order_no: Order number
            operator_id: Operator ID (must be the order initiator)
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            check_sql = f"SELECT [{ORDER_COLUMNS['order_status']}], [{ORDER_COLUMNS['initiator_id']}] FROM [{TABLE_NAMES['ORDER']}] WHERE [{ORDER_COLUMNS['order_no']}] = ?"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('order_status')
            initiator_id = result[0].get('initiator_id')

            if current_status not in {'rejected', 'cancelled'}:
                return {'success': False, 'error': f'只有被驳回或已取消的订单可以重置为草稿，当前状态：{current_status}'}

            if operator_id and initiator_id and operator_id != initiator_id:
                return {'success': False, 'error': '只有订单发起人可以重置为草稿'}

            # Clear rejection/cancellation reasons when resetting
            sql = f"""
            UPDATE [{TABLE_NAMES['ORDER']}] SET
                [{ORDER_COLUMNS['order_status']}] = 'draft',
                [{ORDER_COLUMNS['reject_reason']}] = NULL,
                [{ORDER_COLUMNS['cancel_reason']}] = NULL,
                [{ORDER_COLUMNS['updated_at']}] = GETDATE()
            WHERE [{ORDER_COLUMNS['order_no']}] = ?
            """
            self._db.execute_query(sql, (order_no,), fetch=False)

            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.EDIT,
                'operator_id': operator_id,
                'operator_name': operator_name,
                'operator_role': operator_role,
                'before_status': current_status,
                'after_status': 'draft',
                'content': '订单已重置为草稿'
            })

            return {'success': True, 'status': 'draft'}

        except Exception as e:
            logger.error(f"重置订单为草稿失败: {e}")
            return {'success': False, 'error': str(e)}

    def cancel_order(
        self,
        order_no: str,
        operator_id: str,
        operator_name: str,
        operator_role: str,
        cancel_reason: str = ""
    ) -> dict:
        """
        Cancel an order.

        Args:
            order_no: Order number
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            check_sql = f"SELECT [{ORDER_COLUMNS['order_status']}] FROM [{TABLE_NAMES['ORDER']}] WHERE [{ORDER_COLUMNS['order_no']}] = ?"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('order_status')
            if current_status in ['keeper_confirmed', 'partially_confirmed', 'transport_notified',
                                   'transport_in_progress', 'transport_completed',
                                   'final_confirmation_pending', 'completed', 'rejected', 'cancelled']:
                return {'success': False, 'error': f'当前状态不允许取消，当前状态：{current_status}'}

            normalized_reason = str(cancel_reason or "").strip()

            # Update status and persist cancellation reason for detail retrieval.
            sql = f"""
            UPDATE [{TABLE_NAMES['ORDER']}] SET
                [{ORDER_COLUMNS['order_status']}] = 'cancelled',
                [{ORDER_COLUMNS['reject_reason']}] = ?,
                [{ORDER_COLUMNS['cancel_reason']}] = ?,
                [{ORDER_COLUMNS['updated_at']}] = GETDATE()
            WHERE [{ORDER_COLUMNS['order_no']}] = ?
            """
            self._db.execute_query(sql, (normalized_reason or None, normalized_reason or None, order_no), fetch=False)

            # Update items
            update_items_sql = f"""
            UPDATE [{TABLE_NAMES['ORDER_ITEM']}] SET
                [{ITEM_COLUMNS['item_status']}] = 'rejected',
                [{ITEM_COLUMNS['updated_at']}] = GETDATE()
            WHERE [{ITEM_COLUMNS['order_no']}] = ?
            """
            self._db.execute_query(update_items_sql, (order_no,), fetch=False)

            # Log
            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.CANCEL,
                'operator_id': operator_id,
                'operator_name': operator_name,
                'operator_role': operator_role,
                'before_status': current_status,
                'after_status': 'cancelled',
                'content': f'单据已取消；原因：{normalized_reason}' if normalized_reason else '单据已取消'
            })

            return {'success': True}

        except Exception as e:
            logger.error(f"取消单据失败: {e}")
            return {'success': False, 'error': str(e)}

    def delete_order(
        self,
        order_no: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Delete an order with admin cascade cleanup.

        Args:
            order_no: Order number
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        try:
            check_sql = f"SELECT [{ORDER_COLUMNS['order_status']}], [{ORDER_COLUMNS['initiator_id']}] FROM [{TABLE_NAMES['ORDER']}] WHERE [{ORDER_COLUMNS['order_no']}] = ? AND [{ORDER_COLUMNS['is_deleted']}] = 0"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('order_status')
            initiator_id = result[0].get('initiator_id')

            # Business rule: team_leader can only delete their own draft orders
            if operator_role == 'team_leader':
                if current_status != 'draft':
                    return {'success': False, 'error': '只有草稿状态的单据可以被删除'}
                if initiator_id != operator_id:
                    return {'success': False, 'error': '只能删除自己创建的单据'}

            self._db.execute_query(
                f"""
                DELETE FROM [{TABLE_NAMES['ORDER_ITEM']}]
                WHERE [{ITEM_COLUMNS['order_no']}] = ?
                """,
                (order_no,),
                fetch=False,
            )
            self._db.execute_query(
                f"""
                DELETE FROM [{TABLE_NAMES['ORDER_LOG']}]
                WHERE [{LOG_COLUMNS['order_no']}] = ?
                """,
                (order_no,),
                fetch=False,
            )
            self._db.execute_query(
                f"""
                DELETE FROM [{TABLE_NAMES['ORDER_NOTIFICATION']}]
                WHERE [{NOTIFY_COLUMNS['order_no']}] = ?
                """,
                (order_no,),
                fetch=False,
            )
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['ORDER']}] SET
                    [{ORDER_COLUMNS['tool_quantity']}] = 0,
                    [{ORDER_COLUMNS['confirmed_count']}] = 0,
                    [{ORDER_COLUMNS['keeper_confirm_time']}] = NULL,
                    [{ORDER_COLUMNS['final_confirm_time']}] = NULL,
                    [{ORDER_COLUMNS['is_deleted']}] = 1,
                    [{ORDER_COLUMNS['updated_at']}] = GETDATE(),
                    [{ORDER_COLUMNS['updated_by']}] = ?
                WHERE [{ORDER_COLUMNS['order_no']}] = ?
                """,
                (operator_name, order_no),
                fetch=False,
            )

            # Log
            log_content = '管理员执行单据删除并完成级联清理' if operator_role == 'sys_admin' else '班组长删除自己创建的草稿单据'
            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.DELETE,
                'operator_id': operator_id,
                'operator_name': operator_name,
                'operator_role': operator_role,
                'before_status': current_status,
                'after_status': 'deleted',
                'content': log_content
            })

            return {'success': True}

        except Exception as e:
            logger.error(f"删除单据失败: {e}")
            return {'success': False, 'error': str(e)}

    def add_tool_io_log(self, log_data: dict, conn: Any = None) -> bool:
        """
        Add operation log.

        Args:
            log_data: Log data dictionary
            conn: Optional database connection for transactional context.
                  When provided inside a transaction, failures raise exceptions to trigger rollback.
                  When None (non-transactional), failures return False without raising.

        Returns:
            True if successful

        Raises:
            Exception: When conn is provided and log insertion fails (triggers transaction rollback)
        """
        try:
            sql = f"""
            INSERT INTO [{TABLE_NAMES['ORDER_LOG']}] (
                [{LOG_COLUMNS['order_no']}], [{LOG_COLUMNS['item_id']}], [{LOG_COLUMNS['operation_type']}],
                [{LOG_COLUMNS['operator_id']}], [{LOG_COLUMNS['operator_name']}], [{LOG_COLUMNS['operator_role']}],
                [{LOG_COLUMNS['from_status']}], [{LOG_COLUMNS['to_status']}], [{LOG_COLUMNS['operation_content']}], [{LOG_COLUMNS['operation_time']}]
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            self._db.execute_query(sql, (
                log_data.get('order_no'),
                log_data.get('item_id'),
                log_data.get('action_type'),
                log_data.get('operator_id'),
                log_data.get('operator_name'),
                log_data.get('operator_role'),
                log_data.get('before_status'),
                log_data.get('after_status'),
                log_data.get('content')
            ), fetch=False, conn=conn)
            return True
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")
            if conn is not None:
                # Inside transaction: raise to trigger rollback
                raise
            # Outside transaction: return False for graceful handling
            return False

    def get_tool_io_logs(self, order_no: str) -> list:
        """
        Get operation logs for an order.

        Args:
            order_no: Order number

        Returns:
            List of log dictionaries
        """
        try:
            sql = f"""
            SELECT * FROM [{TABLE_NAMES['ORDER_LOG']}]
            WHERE [{LOG_COLUMNS['order_no']}] = ?
            ORDER BY [{LOG_COLUMNS['operation_time']}] DESC
            """
            return self._db.execute_query(sql, (order_no,))
        except Exception as e:
            logger.error(f"获取操作日志失败: {e}")
            return []

    def add_notification(self, notify_data: dict) -> int:
        """
        Add notification record.

        Args:
            notify_data: Notification data

        Returns:
            Notification ID or 0 on failure
        """
        conn = None
        cursor = None
        try:
            conn = self._db.connect()
            cursor = conn.cursor()
            sql = f"""
            INSERT INTO [{TABLE_NAMES['ORDER_NOTIFICATION']}] (
                [{NOTIFY_COLUMNS['order_no']}], [{NOTIFY_COLUMNS['notify_type']}], [{NOTIFY_COLUMNS['notify_channel']}],
                [{NOTIFY_COLUMNS['receiver']}], [{NOTIFY_COLUMNS['notify_title']}],
                [{NOTIFY_COLUMNS['notify_content']}], [{NOTIFY_COLUMNS['copy_text']}], [{NOTIFY_COLUMNS['send_status']}], [{NOTIFY_COLUMNS['created_at']}]
            )
            OUTPUT INSERTED.id AS id
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', GETDATE())
            """
            cursor.execute(sql, (
                notify_data.get('order_no'),
                notify_data.get('notify_type'),
                notify_data.get('notify_channel'),
                notify_data.get('receiver'),
                notify_data.get('title'),
                notify_data.get('content'),
                notify_data.get('copy_text')
            ))
            row = cursor.fetchone()
            conn.commit()
            return int(row[0]) if row else 0
        except Exception as e:
            if conn is not None:
                conn.rollback()
            logger.error(f"add_tool_io_notification failed: {e}")
            return 0
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._db.close(conn)

    def update_notification_status(
        self,
        notify_id: int,
        status: str,
        send_result: str = None
    ) -> bool:
        """
        Update notification status.

        Args:
            notify_id: Notification ID
            status: New status
            send_result: Send result message

        Returns:
            True if successful
        """
        try:
            sql = f"""
            UPDATE [{TABLE_NAMES['ORDER_NOTIFICATION']}] SET
                [{NOTIFY_COLUMNS['send_status']}] = ?,
                [{NOTIFY_COLUMNS['send_time']}] = GETDATE(),
                [{NOTIFY_COLUMNS['send_result']}] = ?
            WHERE id = ?
            """
            self._db.execute_query(sql, (status, send_result, notify_id), fetch=False)
            return True
        except Exception as e:
            logger.error(f"更新通知状态失败: {e}")
            return False

    def get_pending_keeper_orders(self, keeper_id: str = None) -> list:
        """
        Get orders pending keeper confirmation.

        Args:
            keeper_id: Filter by keeper ID

        Returns:
            List of order dictionaries
        """
        try:
            sql = f"""
            SELECT * FROM [{TABLE_NAMES['ORDER']}]
            WHERE {ORDER_COLUMNS['order_status']} IN ('submitted', 'partially_confirmed')
            AND {ORDER_COLUMNS['is_deleted']} = 0
            """
            params = []
            if keeper_id:
                # Keep submitted orders visible to all keepers (cross-org auto-assignment),
                # and only narrow non-submitted records by keeper binding.
                sql += f" AND ({ORDER_COLUMNS['order_status']} = 'submitted' OR {ORDER_COLUMNS['keeper_id']} = ? OR {ORDER_COLUMNS['keeper_id']} IS NULL)"
                params.append(keeper_id)
            sql += f" ORDER BY {ORDER_COLUMNS['created_at']} DESC"

            return self._db.execute_query(sql, tuple(params))
        except Exception as e:
            logger.error(f"获取待确认单据失败: {e}")
            return []

    def get_pre_transport_orders(
        self,
        user_id: str,
        org_ids: Optional[List[str]] = None,
        all_access: bool = False,
    ) -> list:
        """
        Get pre-transport visibility orders for production prep users.

        Includes submitted/keeper_confirmed/transport_notified orders and applies
        organization-level data isolation unless all-access is enabled.

        Args:
            user_id: Current user id (reserved for audit and future narrowing)
            org_ids: Organization ids visible to current user
            all_access: Whether user has ALL scope (e.g., sys_admin)

        Returns:
            List of pre-transport order rows
        """
        try:
            _ = user_id  # reserved for future fine-grained filters
            org_ids = [str(org_id).strip() for org_id in (org_ids or []) if str(org_id).strip()]
            if not all_access and not org_ids:
                return []

            status_text_case = """
            CASE main.[{status_col}]
                WHEN 'submitted' THEN N'已提交'
                WHEN 'keeper_confirmed' THEN N'保管员已确认'
                WHEN 'transport_notified' THEN N'运输已通知'
                ELSE main.[{status_col}]
            END
            """.format(status_col=ORDER_COLUMNS["order_status"])

            sql = f"""
            SELECT
                main.[{ORDER_COLUMNS['order_no']}] AS [order_no],
                main.[{ORDER_COLUMNS['order_type']}] AS [order_type],
                main.[{ORDER_COLUMNS['target_location_text']}] AS [destination],
                main.[{ORDER_COLUMNS['order_status']}] AS [status],
                {status_text_case} AS [status_text],
                main.[{ORDER_COLUMNS['tool_quantity']}] AS [expected_tools],
                main.[{ORDER_COLUMNS['created_at']}] AS [submit_time],
                main.[{ORDER_COLUMNS['initiator_name']}] AS [submitter_name],
                main.[{ORDER_COLUMNS['planned_use_time']}] AS [estimated_transport_time],
                main.[{ORDER_COLUMNS['keeper_confirm_time']}] AS [keeper_confirmed_time]
            FROM [tool_io_order] AS main
            WHERE main.[{ORDER_COLUMNS['is_deleted']}] = 0
              AND main.[{ORDER_COLUMNS['order_status']}] IN ('submitted', 'keeper_confirmed', 'transport_notified')
            """

            params: List[Any] = []
            if not all_access:
                placeholders = ", ".join(["?"] * len(org_ids))
                # Allow transport assignee to see orders assigned to them even if from different org
                sql += f" AND (main.[{ORDER_COLUMNS['org_id']}] IN ({placeholders}) OR main.[{ORDER_COLUMNS['transport_assignee_id']}] = ?)"
                params.extend(org_ids)
                params.append(user_id)

            sql += f" ORDER BY main.[{ORDER_COLUMNS['created_at']}] DESC"
            return self._db.execute_query(sql, tuple(params))
        except Exception as e:
            logger.error(f"获取准备工预知列表失败: {e}")
            return []

    def _build_tool_occupied_error(self, occupied_tools: List[Dict[str, Any]]) -> str:
        """Build user-facing occupied tool message."""
        if not occupied_tools:
            return ""

        summary_parts = []
        seen_pairs = set()
        for item in occupied_tools:
            serial_no = str(item.get("serial_no", "")).strip()
            order_no = str(item.get("order_no", "")).strip()
            if not serial_no or not order_no:
                continue
            key = (serial_no, order_no)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            summary_parts.append(f"{serial_no}（单号：{order_no}，状态：{item.get('order_status', '-') or '-'}）")

        if not summary_parts:
            return "所选工装已被其他进行中的单据占用"
        return "以下工装已被其他进行中的单据占用：" + "；".join(summary_parts)

    def _build_tool_draft_warning(self, draft_tools: List[Dict[str, Any]]) -> str:
        """Build warning text for tools that already exist in draft orders."""
        if not draft_tools:
            return ""

        summary_parts = []
        seen_pairs = set()
        for item in draft_tools:
            serial_no = str(item.get("serial_no", "")).strip()
            order_no = str(item.get("order_no", "")).strip()
            if not serial_no or not order_no:
                continue
            key = (serial_no, order_no)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            summary_parts.append(f"{serial_no}（草稿单：{order_no}）")

        if not summary_parts:
            return ""
        return "以下工装已存在于其他草稿单中：" + "；".join(summary_parts)
