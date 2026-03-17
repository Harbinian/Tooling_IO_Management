# -*- coding: utf-8 -*-
"""
Dispatch repository for dispatch info queries.
"""

import logging
from typing import List, Dict, Optional

from backend.database.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class DispatchRepository:
    """Repository for dispatch information operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def get_dispatch_info(self) -> List[Dict]:
        """
        Get all dispatch information.

        Returns:
            List of dispatch dictionaries
        """
        return self._db.get_dispatch_info()

    def get_dispatch_by_serial(self, serial_no: str) -> List[Dict]:
        """
        Get dispatch info by tool serial number.

        Args:
            serial_no: Tool serial number

        Returns:
            List of dispatch dictionaries
        """
        sql = """
            SELECT
                d.序列号,
                d.工装图号,
                d.派工号,
                d.申请工装定检日期,
                d.完成人,
                d.完成日期,
                d.申请人确认,
                d.TPITR,
                d.工装版次,
                d.涉及分体组件数量,
                m.日期Date as 派工日期
            FROM 工装定检派工_明细 d
            LEFT JOIN 工装定检派工_主表 m ON d.ExcelServerRCID = m.ExcelServerRCID AND d.ExcelServerWIID = m.ExcelServerWIID
            WHERE d.序列号 = ?
            ORDER BY m.日期Date DESC
        """
        return self._db.execute_query(sql, (serial_no,))

    def get_pending_dispatches(self) -> List[Dict]:
        """
        Get dispatches that are not completed.

        Returns:
            List of pending dispatch dictionaries
        """
        sql = """
            SELECT
                d.序列号,
                d.工装图号,
                d.派工号,
                d.申请工装定检日期,
                d.完成人,
                d.完成日期,
                d.申请人确认,
                d.TPITR,
                d.工装版次,
                m.日期Date as 派工日期
            FROM 工装定检派工_明细 d
            LEFT JOIN 工装定检派工_主表 m ON d.ExcelServerRCID = m.ExcelServerRCID AND d.ExcelServerWIID = m.ExcelServerWIID
            WHERE d.完成日期 IS NULL OR d.申请人确认 IS NULL
            ORDER BY m.日期Date DESC
        """
        return self._db.execute_query(sql)
