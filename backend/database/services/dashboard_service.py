# -*- coding: utf-8 -*-
"""
Dashboard service for stats and monitoring.
"""

import logging
from typing import Dict, List
from datetime import datetime

from backend.database.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


def calculate_alert_level(deadline_date) -> tuple:
    """
    Calculate alert level based on deadline.

    Args:
        deadline_date: Deadline date

    Returns:
        Tuple of (level, label, color, icon)
    """
    if not deadline_date:
        return ('UNKNOWN', '未知', '#cccccc', '?')

    today = datetime.now()
    remaining_days = (deadline_date - today).days

    if remaining_days <= 30:
        return ('CRITICAL', '紧急', '#ff0000', '!')
    elif remaining_days <= 90:
        return ('WARNING', '重要', '#ff9900', '!')
    elif remaining_days <= 180:
        return ('NOTICE', '提醒', '#ffcc00', 'i')
    else:
        return ('NORMAL', '正常', '#00ff00', 'v')


def get_monitor_stats() -> Dict:
    """
    Return lightweight dashboard counts.

    Returns:
        Dictionary with stats
    """
    try:
        db = DatabaseManager()
        tools = db.get_tool_basic_info()
        tpitrs = db.get_all_tpitr_info()
        acceptances = db.get_acceptance_info()
        return {
            'expiry': 0,
            'expiry_expired': 0,
            'expiry_upcoming': 0,
            'dispatch': len(db.get_dispatch_info()),
            'tpitr': len(tpitrs),
            'acceptance': len(acceptances),
            'tpitr_has': 0,
            'tpitr_in_use': 0,
            'tpitr_low': 0,
            'expired_tpitr_total': 0,
            'expired_tpitr_has': 0,
            'expired_tpitr_missing': 0,
            'overdue_dispatch_total': 0,
            'overdue_dispatch_no_dispatch': 0,
            'overdue_dispatch_dispatched': 0,
            'total': len(tools),
        }
    except Exception as e:
        logger.error(f"Error getting monitor stats: %s", str(e))
        return {'expiry': 0, 'expiry_expired': 0, 'expiry_upcoming': 0, 'total': 0}


def get_tpitr_status() -> Dict:
    """
    Return lightweight TPITR status stats.

    Returns:
        Dictionary with TPITR status
    """
    try:
        from backend.database.repositories.tpitr_repository import TPITRRepository

        repo = TPITRRepository()
        tpitrs = repo.get_all_tpitr_info()
        details = []
        published = 0

        for tp in tpitrs:
            status = repo.get_tpitr_status_detail(tp)
            if status['status'] == '已发布':
                published += 1
            details.append({
                'drawing_no': tp.get('drawing_no', ''),
                'version': tp.get('version', ''),
                'status': status['status'],
                'bottleneck': status['bottleneck'],
            })

        return {'total': len(tpitrs), 'published': published, 'pending': len(tpitrs) - published, 'details': details}

    except Exception:
        return {'total': 0, 'published': 0, 'pending': 0, 'details': []}


def get_expiry_detail() -> List[Dict]:
    """Return expiry detail from basic tool info when available."""
    try:
        return DatabaseManager().get_tool_basic_info()
    except Exception:
        return []


def get_dispatch_detail() -> List[Dict]:
    """Return dispatch detail from the database manager when available."""
    try:
        return DatabaseManager().get_dispatch_info()
    except Exception:
        return []


def get_acceptance_detail() -> List[Dict]:
    """Return acceptance detail when available."""
    try:
        return DatabaseManager().get_acceptance_info()
    except Exception:
        return []


class DashboardService:
    """Service for dashboard and statistics operations."""

    def __init__(self, db_manager: DatabaseManager = None):
        self._db = db_manager or DatabaseManager()

    def get_stats(self) -> Dict:
        """
        Get overall statistics.

        Returns:
            Stats dictionary
        """
        return get_monitor_stats()

    def get_tpitr_status(self) -> Dict:
        """
        Get TPITR status.

        Returns:
            TPITR status dictionary
        """
        return get_tpitr_status()

    def get_tool_stats(self) -> Dict:
        """
        Get tool statistics.

        Returns:
            Tool stats dictionary
        """
        try:
            tools = self._db.get_tool_basic_info()
            return {
                'total': len(tools),
                'tools': tools
            }
        except Exception as e:
            logger.error(f"Error getting tool stats: {e}")
            return {'total': 0, 'tools': []}

    def get_dispatch_stats(self) -> Dict:
        """
        Get dispatch statistics.

        Returns:
            Dispatch stats dictionary
        """
        try:
            dispatches = self._db.get_dispatch_info()
            return {
                'total': len(dispatches),
                'dispatches': dispatches
            }
        except Exception as e:
            logger.error(f"Error getting dispatch stats: {e}")
            return {'total': 0, 'dispatches': []}

    def get_acceptance_stats(self) -> Dict:
        """
        Get acceptance statistics.

        Returns:
            Acceptance stats dictionary
        """
        try:
            acceptances = self._db.get_acceptance_info()
            return {
                'total': len(acceptances),
                'acceptances': acceptances
            }
        except Exception as e:
            logger.error(f"Error getting acceptance stats: {e}")
            return {'total': 0, 'acceptances': []}
