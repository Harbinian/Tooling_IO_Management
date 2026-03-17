# -*- coding: utf-8 -*-
"""
Order repository for Tool IO order operations.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from backend.database.core.database_manager import DatabaseManager
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

            tool_codes = [str(item.get("tool_code", "")).strip() for item in items if str(item.get("tool_code", "")).strip()]
            if len(tool_codes) != len(items):
                return {"success": False, "error": "每条明细都必须包含序列号"}
            if len(set(tool_codes)) != len(tool_codes):
                return {"success": False, "error": "同一张单据内不能重复选择相同序列号"}

            # Check tool availability
            tool_repo = ToolRepository(self._db)
            try:
                tool_master_map = tool_repo.load_tool_master_map(tool_codes)
            except Exception as exc:
                logger.warning("加载工装主表失败，创建单据时回退到请求快照: %s", exc)
                tool_master_map = {}

            missing_codes = [code for code in tool_codes if code not in tool_master_map]
            for item in items:
                tool_code = str(item.get("tool_code", "")).strip()
                if tool_code in missing_codes:
                    tool_master_map[tool_code] = {
                        "tool_code": tool_code,
                        "tool_name": item.get("tool_name", ""),
                        "drawing_no": item.get("drawing_no", ""),
                        "spec_model": item.get("spec_model", ""),
                        "current_location_text": item.get("current_location_text", ""),
                        "status_text": item.get("status_text", ""),
                    }

            missing_codes = [code for code in tool_codes if code not in tool_master_map]
            if missing_codes:
                return {"success": False, "error": f"以下工装不存在：{', '.join(missing_codes)}"}

            occupied = tool_repo.check_tools_available(tool_codes)
            if not occupied.get("available", True):
                return {"success": False, "error": self._build_tool_occupied_error(occupied.get("occupied_tools", [])), "occupied_tools": occupied.get("occupied_tools", [])}

            order_no = generate_order_no_atomic(order_type)

            # Insert order header
            insert_order_sql = """
            INSERT INTO [工装出入库单_主表] (
                [出入库单号], [单据类型], [单据状态], [发起人ID], [发起人姓名], [发起人角色],
                [部门], [项目代号], [用途], [计划使用时间], [计划归还时间],
                [目标位置ID], [目标位置文本], [备注], [工装数量], [已确认数量], [org_id],
                [创建时间], [修改时间], [创建人], [修改人], [IS_DELETED]
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
            )

            # Insert order items
            insert_item_sql = """
            INSERT INTO [工装出入库单_明细] (
                [出入库单号], [工装ID], [序列号], [工装名称], [工装图号], [机型],
                [申请数量], [确认数量], [明细状态], [工装快照状态], [工装快照位置文本],
                [排序号], [创建时间], [修改时间]
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending_check', ?, ?, ?, GETDATE(), GETDATE())
            """
            for idx, item in enumerate(items, start=1):
                tool_code = str(item.get("tool_code", "")).strip()
                tool_row = tool_master_map[tool_code]
                self._db.execute_query(
                    insert_item_sql,
                    (
                        order_no,
                        safe_bigint(item.get("tool_id")),
                        tool_code,
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
                )

            # Log the creation
            self.add_tool_io_log({
                "order_no": order_no,
                "action_type": ToolIOAction.CREATE,
                "operator_id": order_data.get("initiator_id"),
                "operator_name": order_data.get("initiator_name"),
                "operator_role": order_data.get("initiator_role"),
                "before_status": "",
                "after_status": "draft",
                "content": f"创建出入库单，单号：{order_no}",
            })

            return {"success": True, "order_no": order_no}

        except Exception as e:
            logger.error(f"创建出入库单失败: {e}")
            return {"success": False, "error": str(e)}

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

            check_sql = """
            SELECT [单据状态]
            FROM [工装出入库单_主表]
            WHERE [出入库单号] = ? AND [IS_DELETED] = 0
            """
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {"success": False, "error": "单据不存在"}

            current_status = result[0].get("单据状态")
            if current_status != "draft":
                return {"success": False, "error": f"当前状态不允许提交：{current_status}"}

            # Check items exist
            detail_rows = self._db.execute_query(
                "SELECT [序列号] AS tool_code FROM [工装出入库单_明细] WHERE [出入库单号] = ?",
                (order_no,),
            )
            if not detail_rows:
                return {"success": False, "error": "单据没有工装明细"}

            tool_codes = [str(row.get("tool_code", "")).strip() for row in detail_rows if str(row.get("tool_code", "")).strip()]

            # Check tool availability
            tool_repo = ToolRepository(self._db)
            occupied = tool_repo.check_tools_available(tool_codes, exclude_order_no=order_no)
            if not occupied.get("available", True):
                return {"success": False, "error": self._build_tool_occupied_error(occupied.get("occupied_tools", [])), "occupied_tools": occupied.get("occupied_tools", [])}

            # Update status
            update_sql = """
            UPDATE [工装出入库单_主表]
            SET [单据状态] = 'submitted',
                [修改时间] = GETDATE(),
                [修改人] = ?
            WHERE [出入库单号] = ?
            """
            self._db.execute_query(update_sql, (operator_name, order_no), fetch=False)

            # Log
            self.add_tool_io_log({
                "order_no": order_no,
                "action_type": ToolIOAction.SUBMIT,
                "operator_id": operator_id,
                "operator_name": operator_name,
                "operator_role": operator_role,
                "before_status": "draft",
                "after_status": "submitted",
                "content": "提交单据，等待保管员确认",
            })

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
            sql = "SELECT * FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
            result = self._db.execute_query(sql, (order_no,))
            if not result:
                return {}

            order = result[0]

            # Get items
            items_sql = "SELECT * FROM 工装出入库单_明细 WHERE 出入库单号 = ? ORDER BY 排序号"
            items = self._db.execute_query(items_sql, (order_no,))
            order['items'] = items

            return order

        except Exception as e:
            logger.error(f"获取出入库单详情失败: {e}")
            return {}

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
            conditions = ["IS_DELETED = 0"]
            params = []

            if order_type:
                conditions.append("单据类型 = ?")
                params.append(order_type)

            if order_status:
                conditions.append("单据状态 = ?")
                params.append(order_status)

            if initiator_id:
                conditions.append("发起人ID = ?")
                params.append(initiator_id)

            if keeper_id:
                conditions.append("保管员ID = ?")
                params.append(keeper_id)

            if keyword:
                conditions.append("(出入库单号 LIKE ? OR 发起人姓名 LIKE ? OR 备注 LIKE ?)")
                keyword_like = f"%{keyword}%"
                params.extend([keyword_like, keyword_like, keyword_like])

            if date_from:
                conditions.append("创建时间 >= ?")
                params.append(date_from)

            if date_to:
                conditions.append("创建时间 <= ?")
                params.append(date_to)

            where_clause = " AND ".join(conditions)

            # Count
            count_sql = f"SELECT COUNT(*) AS total FROM [工装出入库单_主表] WHERE {where_clause}"
            count_result = self._db.execute_query(count_sql, tuple(params))
            total = count_result[0].get('total', 0) if count_result else 0

            # Query
            offset = max(page_no - 1, 0) * page_size
            sql = f"""
            SELECT * FROM [工装出入库单_主表]
            WHERE {where_clause}
            ORDER BY 创建时间 DESC
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

            # Check order status
            check_sql = "SELECT [单据类型], [单据状态] FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('单据状态')
            if current_status not in ['submitted', 'partially_confirmed']:
                return {'success': False, 'error': f'当前状态不允许确认，当前状态：{current_status}'}

            # Update items
            approved_count = 0
            for item in items:
                item_sql = """
                UPDATE 工装出入库单_明细 SET
                    确认人ID = ?,
                    确认人姓名 = ?,
                    确认时间 = GETDATE(),
                    确认数量 = ?,
                    明细状态 = ?,
                    驳回原因 = ?,
                    修改时间 = GETDATE()
                WHERE 出入库单号 = ? AND 序列号 = ?
                """
                status = item.get('status', 'approved')
                if status == 'approved':
                    approved_count += 1
                reject_reason = ''
                if status != 'approved':
                    reject_reason = str(item.get('reject_reason') or item.get('check_remark') or '').strip()

                self._db.execute_query(item_sql, (
                    item.get('location_id'),
                    item.get('location_text'),
                    item.get('approved_qty', 1),
                    status,
                    reject_reason or None,
                    order_no,
                    item.get('tool_code')
                ), fetch=False)

            # Update order status
            new_status = 'keeper_confirmed' if approved_count == len(items) else 'partially_confirmed'
            update_sql = """
            UPDATE 工装出入库单_主表 SET
                单据状态 = ?,
                保管员ID = ?,
                保管员姓名 = ?,
                运输类型 = ?,
                运输AssigneeID = ?,
                运输AssigneeName = ?,
                保管员确认时间 = GETDATE(),
                已确认数量 = ?,
                修改时间 = GETDATE()
            WHERE 出入库单号 = ?
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
            ), fetch=False)

            # Log
            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.KEEPER_CONFIRM,
                'operator_id': operator_id,
                'operator_name': operator_name,
                'operator_role': operator_role,
                'before_status': current_status,
                'after_status': new_status,
                'content': f'保管员确认，通过 {approved_count}/{len(items)} 项'
            })

            return {'success': True, 'status': new_status, 'approved_count': approved_count}

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
            check_sql = "SELECT [单据类型], [单据状态] FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            order_type = result[0].get('单据类型')
            current_status = result[0].get('单据状态')

            if current_status not in ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'final_confirmation_pending']:
                return {'success': False, 'error': f'当前状态不允许最终确认，当前状态：{current_status}'}

            # Update order status
            sql = """
            UPDATE 工装出入库单_主表 SET
                单据状态 = 'completed',
                最终确认人 = ?,
                最终确认时间 = GETDATE(),
                修改时间 = GETDATE()
            WHERE 出入库单号 = ?
            """
            self._db.execute_query(sql, (operator_name, order_no), fetch=False)

            # Update items
            update_items_sql = """
            UPDATE 工装出入库单_明细 SET
                明细状态 = 'completed',
                出入库完成时间 = GETDATE(),
                修改时间 = GETDATE()
            WHERE 出入库单号 = ? AND 明细状态 = 'approved'
            """
            self._db.execute_query(update_items_sql, (order_no,), fetch=False)

            # Log
            self.add_tool_io_log({
                'order_no': order_no,
                'action_type': ToolIOAction.COMPLETE,
                'operator_id': operator_id,
                'operator_name': operator_name,
                'operator_role': operator_role,
                'before_status': current_status,
                'after_status': 'completed',
                'content': f'出入库完成，类型：{order_type}'
            })

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
            check_sql = "SELECT [单据状态] FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('单据状态')
            if current_status not in ['submitted', 'keeper_confirmed', 'partially_confirmed']:
                return {'success': False, 'error': f'当前状态不允许驳回，当前状态：{current_status}'}

            # Update status
            sql = """
            UPDATE 工装出入库单_主表 SET
                单据状态 = 'rejected',
                驳回原因 = ?,
                修改时间 = GETDATE()
            WHERE 出入库单号 = ?
            """
            self._db.execute_query(sql, (reject_reason, order_no), fetch=False)

            # Update items
            update_items_sql = """
            UPDATE 工装出入库单_明细 SET
                明细状态 = 'rejected',
                修改时间 = GETDATE()
            WHERE 出入库单号 = ?
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

    def cancel_order(
        self,
        order_no: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
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
            check_sql = "SELECT [单据状态] FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
            result = self._db.execute_query(check_sql, (order_no,))
            if not result:
                return {'success': False, 'error': '单据不存在'}

            current_status = result[0].get('单据状态')
            if current_status in ['completed', 'rejected', 'cancelled']:
                return {'success': False, 'error': f'当前状态不允许取消，当前状态：{current_status}'}

            # Update status
            sql = """
            UPDATE 工装出入库单_主表 SET
                单据状态 = 'cancelled',
                修改时间 = GETDATE()
            WHERE 出入库单号 = ?
            """
            self._db.execute_query(sql, (order_no,), fetch=False)

            # Update items
            update_items_sql = """
            UPDATE 工装出入库单_明细 SET
                明细状态 = 'rejected',
                修改时间 = GETDATE()
            WHERE 出入库单号 = ?
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
                'content': '单据已取消'
            })

            return {'success': True}

        except Exception as e:
            logger.error(f"取消单据失败: {e}")
            return {'success': False, 'error': str(e)}

    def add_tool_io_log(self, log_data: dict) -> bool:
        """
        Add operation log.

        Args:
            log_data: Log data dictionary

        Returns:
            True if successful
        """
        try:
            sql = """
            INSERT INTO 工装出入库单_操作日志 (
                出入库单号, 明细ID, 操作类型, 操作人ID, 操作人姓名, 操作人角色,
                变更前状态, 变更后状态, 操作内容, 操作时间
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
            ), fetch=False)
            return True
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")
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
            sql = """
            SELECT * FROM 工装出入库单_操作日志
            WHERE 出入库单号 = ?
            ORDER BY 操作时间 DESC
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
            sql = """
            INSERT INTO 工装出入库单_通知记录 (
                出入库单号, 通知类型, 通知渠道, 接收人, 通知标题,
                通知内容, 复制文本, 发送状态, 创建时间
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
            sql = """
            UPDATE 工装出入库单_通知记录 SET
                发送状态 = ?,
                发送时间 = GETDATE(),
                发送结果 = ?
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
            sql = """
            SELECT * FROM 工装出入库单_主表
            WHERE 单据状态 IN ('submitted', 'partially_confirmed')
            AND IS_DELETED = 0
            """
            params = []
            if keeper_id:
                sql += " AND (保管员ID = ? OR 保管员ID IS NULL)"
                params.append(keeper_id)
            sql += " ORDER BY 创建时间 DESC"

            return self._db.execute_query(sql, tuple(params))
        except Exception as e:
            logger.error(f"获取待确认单据失败: {e}")
            return []

    def _build_tool_occupied_error(self, occupied_tools: List[Dict[str, Any]]) -> str:
        """Build user-facing occupied tool message."""
        if not occupied_tools:
            return ""

        summary_parts = []
        seen_pairs = set()
        for item in occupied_tools:
            tool_code = str(item.get("tool_code", "")).strip()
            order_no = str(item.get("order_no", "")).strip()
            if not tool_code or not order_no:
                continue
            key = (tool_code, order_no)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            summary_parts.append(f"{tool_code}（单号：{order_no}，状态：{item.get('order_status', '-') or '-'}）")

        if not summary_parts:
            return "所选工装已被其他进行中的单据占用"
        return "以下工装已被其他进行中的单据占用：" + "；".join(summary_parts)
