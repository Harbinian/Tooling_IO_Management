"""Runtime-safe Tool IO queries for keeper workflow paths."""

from __future__ import annotations

import logging
from typing import Dict, List

from database import DatabaseManager, ToolIOAction

logger = logging.getLogger(__name__)


def add_runtime_log(log_data: Dict) -> bool:
    """Persist one log row without relying on legacy SQL fragments."""
    try:
        DatabaseManager().execute_query(
            """
            INSERT INTO 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織 (
                鍑哄叆搴撳崟鍙?,
                鏄庣粏ID,
                鎿嶄綔绫诲瀷,
                鎿嶄綔浜篒D,
                鎿嶄綔浜哄鍚?,
                鎿嶄綔浜鸿鑹?,
                鍙樻洿鍓嶇姸鎬?,
                鍙樻洿鍚庣姸鎬?,
                鎿嶄綔鍐呭,
                鎿嶄綔鏃堕棿
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """,
            (
                log_data.get("order_no"),
                log_data.get("item_id"),
                log_data.get("action_type"),
                log_data.get("operator_id"),
                log_data.get("operator_name"),
                log_data.get("operator_role"),
                log_data.get("before_status"),
                log_data.get("after_status"),
                log_data.get("content"),
            ),
            fetch=False,
        )
        return True
    except Exception as exc:
        logger.error("Failed to persist runtime log: %s", exc)
        return False


def list_pending_keeper_orders(keeper_id: str | None = None) -> List[Dict]:
    """Return orders waiting for keeper processing."""
    try:
        db = DatabaseManager()
        sql = """
        SELECT *
        FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃
        WHERE 鍗曟嵁鐘舵€? IN ('submitted', 'partially_confirmed')
          AND IS_DELETED = 0
        """
        params: List[str] = []
        if keeper_id:
            sql += " AND (淇濈鍛業D = ? OR 淇濈鍛業D IS NULL)"
            params.append(keeper_id)
        sql += " ORDER BY 鍒涘缓鏃堕棿 DESC"
        return db.execute_query(sql, tuple(params))
    except Exception as exc:
        logger.error("Failed to load keeper pending orders: %s", exc)
        return []


def get_order_detail_runtime(order_no: str) -> Dict:
    """Return one order with item and notification records."""
    try:
        db = DatabaseManager()
        order_rows = db.execute_query(
            """
            SELECT *
            FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃
            WHERE 鍑哄叆搴撳崟鍙?= ? AND IS_DELETED = 0
            """,
            (order_no,),
        )
        if not order_rows:
            return {}

        order = order_rows[0]
        order["items"] = db.execute_query(
            """
            SELECT *
            FROM 宸ヨ鍑哄叆搴撳崟_鏄庣粏
            WHERE 鍑哄叆搴撳崟鍙?= ?
            ORDER BY 鎺掑簭鍙? ASC, id ASC
            """,
            (order_no,),
        )
        order["notification_records"] = db.execute_query(
            """
            SELECT *
            FROM 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍
            WHERE 鍑哄叆搴撳崟鍙?= ?
            ORDER BY 鍒涘缓鏃堕棿 DESC, id DESC
            """,
            (order_no,),
        )
        return order
    except Exception as exc:
        logger.error("Failed to load order detail for %s: %s", order_no, exc)
        return {}


def get_order_logs_runtime(order_no: str) -> List[Dict]:
    """Return audit logs for one order."""
    try:
        db = DatabaseManager()
        return db.execute_query(
            """
            SELECT *
            FROM 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織
            WHERE 鍑哄叆搴撳崟鍙?= ?
            ORDER BY 鎿嶄綔鏃堕棿 DESC, id DESC
            """,
            (order_no,),
        )
    except Exception as exc:
        logger.error("Failed to load order logs for %s: %s", order_no, exc)
        return []


def keeper_confirm_runtime(
    order_no: str,
    keeper_id: str,
    keeper_name: str,
    confirm_data: Dict,
    operator_id: str,
    operator_name: str,
    operator_role: str,
) -> Dict:
    """Persist keeper confirmation with schema-aware validation."""
    try:
        db = DatabaseManager()
        items = confirm_data.get("items")
        if not isinstance(items, list) or not items:
            return {"success": False, "error": "items must contain at least one item"}

        order_rows = db.execute_query(
            """
            SELECT 鍗曟嵁鐘舵€?
            FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃
            WHERE 鍑哄叆搴撳崟鍙?= ? AND IS_DELETED = 0
            """,
            (order_no,),
        )
        if not order_rows:
            return {"success": False, "error": "鍗曟嵁涓嶅瓨鍦?"}

        current_status = order_rows[0].get("鍗曟嵁鐘舵€?")
        if current_status not in {"submitted", "partially_confirmed"}:
            return {
                "success": False,
                "error": f"褰撳墠鐘舵€佷笉鍏佽纭锛屽綋鍓嶇姸鎬侊細{current_status}",
            }

        existing_rows = db.execute_query(
            """
            SELECT id, 宸ヨ缂栫爜
            FROM 宸ヨ鍑哄叆搴撳崟_鏄庣粏
            WHERE 鍑哄叆搴撳崟鍙?= ?
            """,
            (order_no,),
        )
        existing_codes = {row.get("宸ヨ缂栫爜") for row in existing_rows if row.get("宸ヨ缂栫爜")}
        if not existing_codes:
            return {"success": False, "error": "鍗曟嵁娌℃湁鏄庣粏鏁版嵁"}

        approved_count = 0
        seen_codes = set()
        update_item_sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_鏄庣粏
        SET 淇濈鍛樼‘璁や綅缃甀D = ?,
            淇濈鍛樼‘璁や綅缃枃鏈?= ?,
            淇濈鍛樻鏌ョ粨鏋?= ?,
            淇濈鍛樻鏌ュ娉?= ?,
            纭鏁伴噺 = ?,
            鏄庣粏鐘舵€?= ?,
            纭鏃堕棿 = GETDATE(),
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ? AND 宸ヨ缂栫爜 = ?
        """

        for item in items:
            tool_code = str(item.get("tool_code") or "").strip()
            if not tool_code:
                return {"success": False, "error": "tool_code is required for each item"}
            if tool_code in seen_codes:
                return {"success": False, "error": f"duplicate tool_code: {tool_code}"}
            if tool_code not in existing_codes:
                return {"success": False, "error": f"tool_code does not belong to order: {tool_code}"}

            status = item.get("status", "approved")
            if status not in {"approved", "rejected"}:
                return {"success": False, "error": f"invalid item status: {status}"}

            approved_qty = item.get("approved_qty", 1 if status == "approved" else 0)
            try:
                approved_qty = float(approved_qty)
            except (TypeError, ValueError):
                return {"success": False, "error": f"invalid approved_qty for tool: {tool_code}"}
            if approved_qty < 0:
                return {"success": False, "error": f"approved_qty must be non-negative for tool: {tool_code}"}

            db.execute_query(
                update_item_sql,
                (
                    item.get("location_id"),
                    item.get("location_text"),
                    item.get("check_result") or status,
                    item.get("check_remark"),
                    approved_qty,
                    status,
                    order_no,
                    tool_code,
                ),
                fetch=False,
            )
            seen_codes.add(tool_code)
            if status == "approved":
                approved_count += 1

        new_status = "keeper_confirmed" if approved_count == len(items) else "partially_confirmed"
        db.execute_query(
            """
            UPDATE 宸ヨ鍑哄叆搴撳崟_涓昏〃
            SET 鍗曟嵁鐘舵€?= ?,
                淇濈鍛業D = ?,
                淇濈鍛樺鍚?= ?,
                杩愯緭绫诲瀷 = ?,
                杩愯緭浜篒D = ?,
                杩愯緭浜哄鍚?= ?,
                淇濈鍛樼‘璁ゆ椂闂?= GETDATE(),
                宸茬‘璁ゆ暟閲?= ?,
                淇敼鏃堕棿 = GETDATE()
            WHERE 鍑哄叆搴撳崟鍙?= ?
            """,
            (
                new_status,
                keeper_id,
                keeper_name,
                confirm_data.get("transport_type"),
                confirm_data.get("transport_assignee_id"),
                confirm_data.get("transport_assignee_name"),
                approved_count,
                order_no,
            ),
            fetch=False,
        )

        keeper_remark = str(confirm_data.get("keeper_remark") or "").strip()
        content = f"淇濈鍛樼‘璁わ紝閫氳繃 {approved_count}/{len(items)} 椤?"
        if keeper_remark:
            content = f"{content}锛屽娉細{keeper_remark}"
        add_runtime_log(
            {
                "order_no": order_no,
                "action_type": ToolIOAction.KEEPER_CONFIRM,
                "operator_id": operator_id,
                "operator_name": operator_name,
                "operator_role": operator_role,
                "before_status": current_status,
                "after_status": new_status,
                "content": content,
            }
        )
        return {"success": True, "status": new_status, "approved_count": approved_count}
    except Exception as exc:
        logger.error("Keeper confirmation failed for %s: %s", order_no, exc)
        return {"success": False, "error": str(exc)}
