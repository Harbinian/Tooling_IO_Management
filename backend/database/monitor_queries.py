# -*- coding: utf-8 -*-
"""Monitoring and TPITR queries extracted from database.py."""

from __future__ import annotations

import database as legacy_db
from typing import Dict, Tuple

def calculate_alert_level(deadline_date) -> Tuple[str, str, str, str]:
    """计算预警等级"""
    if not deadline_date:
        return 'UNKNOWN', '未知', '#cccccc', '❓'

    today = datetime.now()
    remaining_days = (deadline_date - today).days

    if remaining_days <= 30:
        return 'CRITICAL', '紧急', '#ff0000', '🔴'
    elif remaining_days <= 90:
        return 'WARNING', '重要', '#ff9900', '🟡'
    elif remaining_days <= 180:
        return 'NOTICE', '提醒', '#ffcc00', '🟢'
    else:
        return 'NORMAL', '正常', '#00ff00', '⚪'


def get_tpitr_status_detail(tpitr: Dict) -> Dict:
    """精确识别TPITR的审批流程状态"""
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

    if valid_status == '已发布':
        return {'status': '已完成', 'bottleneck': '工装定检技术条件已发布',
                'current_step': '已完成', 'next_step': None}

    if not author or not author_date:
        return {'status': '待编制', 'bottleneck': '等待技术人员开始编制',
                'current_step': '编制', 'next_step': '编制'}

    if not checker or not check_date:
        bottleneck_msg = f'等待{checker}进行校对' if checker else '等待指派校对人员'
        return {'status': '待校对', 'bottleneck': bottleneck_msg,
                'current_step': '校对', 'next_step': '校对'}

    if not check_conclusion:
        bottleneck_msg = f'等待校对人员{checker}给出结论' if checker else '等待校对结论'
        return {'status': '待校对结论', 'bottleneck': bottleneck_msg,
                'current_step': '校对', 'next_step': '校对'}

    if check_conclusion == '不同意':
        return {'status': '校对不同意', 'bottleneck': f'{checker}不同意，需修改后重新提交',
                'current_step': '重新编制', 'next_step': '重新编制'}

    if not approver or not approve_date:
        bottleneck_msg = f'等待{approver}进行批准' if approver else '等待指派批准人员'
        return {'status': '待批准', 'bottleneck': bottleneck_msg,
                'current_step': '批准', 'next_step': '批准'}

    if not approve_conclusion:
        bottleneck_msg = f'等待批准人员{approver}给出结论' if approver else '等待批准结论'
        return {'status': '待批准结论', 'bottleneck': bottleneck_msg,
                'current_step': '批准', 'next_step': '批准'}

    if approve_conclusion == '不同意':
        return {'status': '批准不同意', 'bottleneck': f'{approver}不同意，需修改后重新提交',
                'current_step': '重新编制', 'next_step': '重新编制'}

    if not signer or not sign_date:
        bottleneck_msg = f'等待{signer}进行会签' if signer else '等待指派会签人员'
        return {'status': '待会签', 'bottleneck': bottleneck_msg,
                'current_step': '会签', 'next_step': '会签'}

    if sign_conclusion == '不同意':
        return {'status': '会签不同意', 'bottleneck': f'{signer}不同意，需修改后重新提交',
                'current_step': '重新编制', 'next_step': '重新编制'}

    if not sign_conclusion:
        return {'status': '待会签结论', 'bottleneck': f'等待{signer}给出会签结论',
                'current_step': '会签', 'next_step': '会签'}

    return {'status': '待发布', 'bottleneck': '所有审批环节已完成，等待正式发布',
            'current_step': '发布', 'next_step': '发布'}


# ========================================
# 监控统计数据（使用优化后的查询）
# ========================================

def get_monitor_stats() -> Dict:
    """获取所有监控模块的汇总统计"""
    try:
        db = legacy_db.DatabaseManager()
        tools = db.get_tool_basic_info()
        tpitrs = db.get_all_tpitr_info()
        acceptances = db.get_acceptance_info()

        now = datetime.now()
        tpitr_dict = {tp.get('drawing_no', ''): tp for tp in tpitrs if tp.get('drawing_no')}

        # 统计
        expired_alerts = []
        upcoming_alerts = []
        for tool in tools:
            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            if not deadline:
                continue

            remaining = (deadline - now).days
            if remaining < 0:
                expired_alerts.append(tool)
            elif remaining <= 180:
                upcoming_alerts.append(tool)

        # 派工状态
        dispatch_alerts = []
        for tool in tools:
            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            if not deadline:
                continue
            remaining = (deadline - now).days
            status = tool.get('dispatch_status', '')
            if '未派工' in status:
                dispatch_alerts.append(tool)
            elif '派工' in status and remaining < 30:
                dispatch_alerts.append(tool)

        # TPITR完整性
        tpitr_alerts = []
        for tpitr in tpitrs:
            if tpitr.get('valid_status') != '已发布':
                check = tpitr.get('check_conclusion', '')
                approve = tpitr.get('approve_conclusion', '')
                sign = tpitr.get('sign_conclusion', '')
                if not check or check == '不同意' or not approve or approve == '不同意' or not sign or sign == '不同意':
                    tpitr_alerts.append(tpitr)

        # TPITR三分类
        tpitr_has = []
        tpitr_in_use = []
        tpitr_low = []
        seen = set()
        for tool in tools:
            drawing_no = tool.get('drawing_no', '')
            attribute = tool.get('attribute')
            app_history = tool.get('application_history', '')
            if attribute != '是' or not drawing_no or drawing_no in seen:
                continue
            seen.add(drawing_no)
            if drawing_no in tpitr_dict:
                status = get_tpitr_status_detail(tpitr_dict[drawing_no])
                if status['status'] == '已完成':
                    tpitr_has.append(tool)
                else:
                    if '封存' in app_history:
                        tpitr_low.append(tool)
                    else:
                        tpitr_in_use.append(tool)
            else:
                if '封存' in app_history:
                    tpitr_low.append(tool)
                else:
                    tpitr_in_use.append(tool)

        # 超期工装TPITR
        expired_tpitr_total = expired_tpitr_has = expired_tpitr_missing = 0
        for tool in tools:
            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            if not deadline:
                continue
            remaining = (deadline - now).days
            if remaining >= 0:
                continue
            expired_tpitr_total += 1
            drawing_no = tool.get('drawing_no', '')
            if drawing_no in tpitr_dict:
                status = get_tpitr_status_detail(tpitr_dict[drawing_no])
                if status['status'] == '已完成':
                    expired_tpitr_has += 1
                else:
                    expired_tpitr_missing += 1
            else:
                expired_tpitr_missing += 1

        # 超期派工状态
        overdue_dispatch_total = overdue_dispatch_no_dispatch = overdue_dispatch_dispatched = 0
        for tool in tools:
            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            if not deadline:
                continue
            remaining = (deadline - now).days
            app_history = tool.get('application_history', '')
            status = tool.get('dispatch_status', '')
            if '使用中' not in app_history or remaining >= 0:
                continue
            overdue_dispatch_total += 1
            if '未派工' in status:
                overdue_dispatch_no_dispatch += 1
            elif '派工' in status:
                overdue_dispatch_dispatched += 1

        return {
            'expiry': len(expired_alerts),
            'expiry_expired': len(expired_alerts),
            'expiry_upcoming': len(upcoming_alerts),
            'dispatch': len(dispatch_alerts),
            'tpitr': len(tpitr_alerts),
            'acceptance': len(acceptances),
            'tpitr_has': len(tpitr_has),
            'tpitr_in_use': len(tpitr_in_use),
            'tpitr_low': len(tpitr_low),
            'expired_tpitr_total': expired_tpitr_total,
            'expired_tpitr_has': expired_tpitr_has,
            'expired_tpitr_missing': expired_tpitr_missing,
            'overdue_dispatch_total': overdue_dispatch_total,
            'overdue_dispatch_no_dispatch': overdue_dispatch_no_dispatch,
            'overdue_dispatch_dispatched': overdue_dispatch_dispatched,
            'total': (len(expired_alerts) + len(dispatch_alerts) +
                     len(tpitr_alerts) + len(acceptances) + len(tpitr_has) +
                     len(tpitr_in_use) + len(tpitr_low))
        }
    except Exception as e:
        legacy_db.logger.error(f"获取监控统计失败: {str(e)}")
        return {'expiry': 0, 'expiry_expired': 0, 'expiry_upcoming': 0, 'total': 0}


# ========================================
# 便捷函数
# ========================================
