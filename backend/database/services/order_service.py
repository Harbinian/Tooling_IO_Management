# -*- coding: utf-8 -*-
"""
Order service for Tool IO order business logic.
"""

import logging
from typing import Optional, Dict
from datetime import datetime

from backend.database.core.database_manager import DatabaseManager, ORDER_NO_SEQUENCE_TABLE, ORDER_NO_RETRY_LIMIT
from backend.database.utils.sql_utils import is_duplicate_key_error

logger = logging.getLogger(__name__)


def generate_order_no_atomic(order_type: str) -> str:
    """
    Allocate an order number with a database-backed counter.

    Args:
        order_type: Order type ('outbound' or 'inbound')

    Returns:
        Generated order number

    Raises:
        RuntimeError: If fails to allocate order number
    """
    prefix = "TO-OUT" if order_type == "outbound" else "TO-IN"
    date_str = datetime.now().strftime("%Y%m%d")
    sequence_key = f"{prefix}-{date_str}"
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

    raise RuntimeError("failed to allocate order number")


class OrderService:
    """Service for order business operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def create_order(self, order_data: dict) -> dict:
        """
        Create a new order.

        Args:
            order_data: Order data

        Returns:
            Result dictionary
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.create_order(order_data)

    def submit_order(self, order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
        """
        Submit an order.

        Args:
            order_no: Order number
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.submit_order(order_no, operator_id, operator_name, operator_role)

    def get_order(self, order_no: str) -> Dict:
        """
        Get order details.

        Args:
            order_no: Order number

        Returns:
            Order dictionary
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.get_order(order_no)

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
        Get orders with filters.

        Args:
            order_type: Order type filter
            order_status: Order status filter
            initiator_id: Initiator ID filter
            keeper_id: Keeper ID filter
            keyword: Search keyword
            date_from: Start date
            date_to: End date
            page_no: Page number
            page_size: Page size

        Returns:
            Result dictionary
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.get_orders(
            order_type=order_type,
            order_status=order_status,
            initiator_id=initiator_id,
            keeper_id=keeper_id,
            keyword=keyword,
            date_from=date_from,
            date_to=date_to,
            page_no=page_no,
            page_size=page_size
        )

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
        Keeper confirmation.

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
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.keeper_confirm(
            order_no, keeper_id, keeper_name, confirm_data,
            operator_id, operator_name, operator_role
        )

    def final_confirm(
        self,
        order_no: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Final confirmation.

        Args:
            order_no: Order number
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.final_confirm(order_no, operator_id, operator_name, operator_role)

    def reject_order(
        self,
        order_no: str,
        reject_reason: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Reject order.

        Args:
            order_no: Order number
            reject_reason: Rejection reason
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.reject_order(
            order_no, reject_reason, operator_id, operator_name, operator_role
        )

    def cancel_order(
        self,
        order_no: str,
        operator_id: str,
        operator_name: str,
        operator_role: str
    ) -> dict:
        """
        Cancel order.

        Args:
            order_no: Order number
            operator_id: Operator ID
            operator_name: Operator name
            operator_role: Operator role

        Returns:
            Result dictionary
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.cancel_order(order_no, operator_id, operator_name, operator_role)

    def get_order_logs(self, order_no: str) -> list:
        """
        Get order logs.

        Args:
            order_no: Order number

        Returns:
            List of log dictionaries
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.get_tool_io_logs(order_no)

    def get_pending_keeper_orders(self, keeper_id: str = None) -> list:
        """
        Get orders pending keeper confirmation.

        Args:
            keeper_id: Keeper ID filter

        Returns:
            List of order dictionaries
        """
        from backend.database.repositories.order_repository import OrderRepository
        repo = OrderRepository(self._db)
        return repo.get_pending_keeper_orders(keeper_id)

    def search_tools(
        self,
        keyword: str = None,
        status: str = None,
        location_id: int = None,
        page_no: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        Search tools.

        Args:
            keyword: Search keyword
            status: Status filter
            location_id: Location ID filter
            page_no: Page number
            page_size: Page size

        Returns:
            Result dictionary
        """
        from backend.database.repositories.tool_repository import ToolRepository
        repo = ToolRepository(self._db)
        return repo.search_tools(keyword, status, location_id, page_no, page_size)

    def check_tools_available(
        self,
        tool_codes: list,
        exclude_order_no: str = None
    ) -> dict:
        """
        Check if tools are available.

        Args:
            tool_codes: List of tool codes
            exclude_order_no: Order to exclude

        Returns:
            Result dictionary
        """
        from backend.database.repositories.tool_repository import ToolRepository
        repo = ToolRepository(self._db)
        return repo.check_tools_available(tool_codes, exclude_order_no)
