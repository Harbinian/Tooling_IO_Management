# -*- coding: utf-8 -*-
"""
Acceptance repository for acceptance info queries.
"""

import logging
from typing import List, Dict, Optional

from backend.database.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AcceptanceRepository:
    """Repository for acceptance operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def get_acceptance_info(self) -> List[Dict]:
        """
        Get all acceptance information.

        Returns:
            List of acceptance dictionaries
        """
        return self._db.get_acceptance_info()

    def get_acceptance_by_dispatch(self, dispatch_no: str) -> Optional[Dict]:
        """
        Get acceptance by dispatch number.

        Args:
            dispatch_no: Dispatch number

        Returns:
            Acceptance dictionary or None
        """
        sql = """
            SELECT
                m.派工号,
                m.表编号,
                m.序列号,
                m.验收状态,
                m.计划员检查完成日期,
                m.保管员组织验收日期,
                m.质检验收日期,
                m.工艺验收日期,
                m.验收完成日期,
                m.保管员,
                m.联合验收说明,
                m.最新通知单号,
                m.备注,
                m.创建时间,
                m.修改时间
            FROM 工装验收管理_主表 m
            WHERE m.派工号 = ?
        """
        results = self._db.execute_query(sql, (dispatch_no,))
        return results[0] if results else None

    def get_nonconforming_notices(self) -> List[Dict]:
        """
        Get all non-conforming tool notices.

        Returns:
            List of notice dictionaries
        """
        return self._db.get_nonconforming_notices()

    def get_inspection_records(self) -> List[Dict]:
        """
        Get all inspection records.

        Returns:
            List of inspection record dictionaries
        """
        return self._db.get_inspection_records()

    def get_repair_records(self) -> List[Dict]:
        """
        Get all repair records.

        Returns:
            List of repair record dictionaries
        """
        return self._db.get_repair_records()

    def get_new_rework_applications(self) -> List[Dict]:
        """
        Get unsynced rework applications.

        Returns:
            List of rework application dictionaries
        """
        return self._db.get_new_rework_applications()

    def get_new_tooling_applications(self) -> List[Dict]:
        """
        Get unsynced new tooling applications.

        Returns:
            List of tooling application dictionaries
        """
        return self._db.get_new_tooling_applications()
