# -*- coding: utf-8 -*-
"""
TPITR repository for technical requirements queries.
"""

import logging
from typing import List, Dict, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.utils.date_utils import normalize_date

logger = logging.getLogger(__name__)


class TPITRRepository:
    """Repository for TPITR (Technical Process Inspection Test Record) operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def get_all_tpitr_info(self) -> List[Dict]:
        """
        Get all TPITR information.

        Returns:
            List of TPITR dictionaries
        """
        return self._db.get_all_tpitr_info()

    def get_tpitr_by_drawing(self, drawing_no: str) -> List[Dict]:
        """
        Get TPITR by drawing number.

        Args:
            drawing_no: Tool drawing number

        Returns:
            List of TPITR dictionaries
        """
        sql = """
            SELECT
                工装图号,
                版次,
                编制,
                编制日期,
                校对人,
                校对日期,
                校对结论,
                批准人,
                批准日期,
                批准结论,
                会签人,
                质量会签日期,
                会签结论,
                有效状态,
                编号No,
                校对意见,
                批准意见,
                会签意见
            FROM TPITR_主表_V11
            WHERE 工装图号 = ?
        """
        return self._db.execute_query(sql, (drawing_no,))

    def get_tpitr_status_detail(self, tpitr: Dict) -> Dict:
        """
        Return a conservative TPITR workflow status summary.

        Args:
            tpitr: TPITR dictionary

        Returns:
            Status detail dictionary
        """
        author = tpitr.get('author')
        author_date = tpitr.get('author_date')
        checker = tpitr.get('checker')
        check_date = tpitr.get('check_date')
        check_conclusion = tpitr.get('check_conclusion')
        approver = tpitr.get('approver')
        approve_date = tpitr.get('approve_date')
        approve_conclusion = tpitr.get('approve_conclusion')
        signer = tpitr.get('signer')
        sign_date = tpitr.get('sign_date')
        sign_conclusion = tpitr.get('sign_conclusion')
        valid_status = tpitr.get('valid_status')

        if valid_status:
            status_text = str(valid_status)
            if '发布' in status_text or '发布' in status_text:
                return {
                    'status': '已发布',
                    'bottleneck': '技术条件已发布',
                    'current_step': '已完成',
                    'next_step': None,
                }

        if not author or not author_date:
            return {
                'status': '待编制',
                'bottleneck': '等待技术人员开始编制',
                'current_step': '编制',
                'next_step': '编制',
            }

        if not checker or not check_date:
            return {
                'status': '待校对',
                'bottleneck': f'等待{checker}进行校对' if checker else '等待指派校对人员',
                'current_step': '校对',
                'next_step': '校对',
            }

        if not check_conclusion:
            return {
                'status': '待校对结论',
                'bottleneck': f'等待{checker}给出校对结论' if checker else '等待校对结论',
                'current_step': '校对',
                'next_step': '校对',
            }

        if str(check_conclusion) in {'不同意', '不同意'}:
            return {
                'status': '校对不同意',
                'bottleneck': f'{checker}不同意，需要修改后重新提交',
                'current_step': '重新编制',
                'next_step': '重新编制',
            }

        if not approver or not approve_date:
            return {
                'status': '待批准',
                'bottleneck': f'等待{approver}进行批准' if approver else '等待指派批准人员',
                'current_step': '批准',
                'next_step': '批准',
            }

        if not approve_conclusion:
            return {
                'status': '待批准结论',
                'bottleneck': f'等待{approver}给出批准结论' if approver else '等待批准结论',
                'current_step': '批准',
                'next_step': '批准',
            }

        if str(approve_conclusion) in {'不同意', '不同意'}:
            return {
                'status': '批准不同意',
                'bottleneck': f'{approver}不同意，需要修改后重新提交',
                'current_step': '重新编制',
                'next_step': '重新编制',
            }

        if not signer or not sign_date:
            return {
                'status': '待会签',
                'bottleneck': f'等待{signer}进行会签' if signer else '等待指派会签人员',
                'current_step': '会签',
                'next_step': '会签',
            }

        if not sign_conclusion:
            return {
                'status': '待会签结论',
                'bottleneck': f'等待{signer}给出会签结论' if signer else '等待会签结论',
                'current_step': '会签',
                'next_step': '会签',
            }

        if str(sign_conclusion) in {'不同意', '不同意'}:
            return {
                'status': '会签不同意',
                'bottleneck': f'{signer}不同意，需要修改后重新提交',
                'current_step': '重新编制',
                'next_step': '重新编制',
            }

        return {
            'status': '待发布',
            'bottleneck': '所有审批环节已完成，等待正式发布',
            'current_step': '发布',
            'next_step': '发布',
        }
