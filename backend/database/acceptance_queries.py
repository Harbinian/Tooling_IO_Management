# -*- coding: utf-8 -*-
"""Acceptance workflow queries extracted from database.py."""

from __future__ import annotations

import database as legacy_db
from typing import Dict, List

def sync_applications_to_acceptance() -> Dict:
    """从申请单同步数据到验收管理表"""
    try:
        db = legacy_db.DatabaseManager()
        rework_apps = db.get_new_rework_applications()
        tooling_apps = db.get_new_tooling_applications()

        synced_count = 0
        for app in rework_apps + tooling_apps:
            dispatch_no = app.get('dispatch_no', '')
            if not dispatch_no:
                continue

            # 检查是否已存在
            existing = db.execute_query(
                "SELECT 派工号 FROM 工装验收管理_主表 WHERE 派工号 = ?",
                (dispatch_no,)
            )
            if existing:
                continue

            # 插入新记录
            try:
                sql = """
                    INSERT INTO 工装验收管理_主表 (
                        派工号, 序列号, 工装图号, 工装名称,
                        验收状态, 创建时间, 修改时间
                    ) VALUES (?, ?, ?, ?, '待检查', GETDATE(), GETDATE())
                """
                db.execute_query(sql, (
                    dispatch_no,
                    app.get('serial_no', ''),
                    app.get('drawing_no', ''),
                    app.get('tool_name', '')
                ), fetch=False)
                synced_count += 1
            except Exception as e:
                legacy_db.logger.warning(f"同步申请单失败: {dispatch_no}, {str(e)}")

        return {'success': True, 'synced': synced_count}
    except Exception as e:
        legacy_db.logger.error(f"同步申请单失败: {str(e)}")
        return {'success': False, 'error': str(e)}


def add_acceptance_record(dispatch_no: str, serial_no: str, drawing_no: str,
                          tool_name: str, **kwargs) -> Dict:
    """添加验收记录"""
    try:
        sql = """
            INSERT INTO 工装验收管理_主表 (
                派工号, 序列号, 工装图号, 工装名称,
                验收状态, 创建时间, 修改时间
            ) VALUES (?, ?, ?, ?, '待检查', GETDATE(), GETDATE())
        """
        db = legacy_db.DatabaseManager()
        db.execute_query(sql, (dispatch_no, serial_no, drawing_no, tool_name), fetch=False)
        return {'success': True}
    except Exception as e:
        legacy_db.logger.error(f"添加验收记录失败: {str(e)}")
        return {'success': False, 'error': str(e)}


def update_acceptance_status(dispatch_no: str, status: str, **kwargs) -> Dict:
    """更新验收状态"""
    try:
        sql = """
            UPDATE 工装验收管理_主表
            SET 验收状态 = ?, 修改时间 = GETDATE()
            WHERE 派工号 = ?
        """
        db = legacy_db.DatabaseManager()
        db.execute_query(sql, (status, dispatch_no), fetch=False)
        return {'success': True}
    except Exception as e:
        legacy_db.logger.error(f"更新验收状态失败: {str(e)}")
        return {'success': False, 'error': str(e)}


def save_acceptance_account(dispatch_no: str, table_no: str, serial_no: str,
                            drawing_no: str, tool_name: str, **kwargs) -> Dict:
    """保存验收账目"""
    try:
        sql = """
            IF EXISTS (SELECT 1 FROM 工装验收管理_主表 WHERE 派工号 = ?)
                UPDATE 工装验收管理_主表 SET
                    表编号 = ?, 序列号 = ?, 工装图号 = ?, 工装名称 = ?,
                    修改时间 = GETDATE()
                WHERE 派工号 = ?
            ELSE
                INSERT INTO 工装验收管理_主表 (
                    派工号, 表编号, 序列号, 工装图号, 工装名称,
                    验收状态, 创建时间, 修改时间
                ) VALUES (?, ?, ?, ?, ?, '待检查', GETDATE(), GETDATE())
        """
        db = legacy_db.DatabaseManager()
        if table_no:
            db.execute_query(sql, (dispatch_no, table_no, serial_no, drawing_no,
                                   tool_name, dispatch_no), fetch=False)
        else:
            db.execute_query(sql, (dispatch_no, dispatch_no, serial_no, drawing_no,
                                   tool_name, dispatch_no), fetch=False)
        return {'success': True}
    except Exception as e:
        legacy_db.logger.error(f"保存验收账目失败: {str(e)}")
        return {'success': False, 'error': str(e)}


def get_inspector_acceptance_tasks(inspector: str = None) -> List[Dict]:
    """获取检验员验收任务"""
    try:
        sql = """
            SELECT 派工号, 表编号, 序列号, 工装图号, 工装名称,
                   验收状态, 保管员, 计划员检查完成日期,
                   保管员组织验收日期, 质检验收日期, 工艺验收日期,
                   验收完成日期, 创建时间, 修改时间
            FROM 工装验收管理_主表
            WHERE 验收状态 IN ('待检查', '检查中', '待验收')
        """
        if inspector:
            sql += " AND 保管员 = ?"
            results = legacy_db.DatabaseManager().execute_query(sql, (inspector,))
        else:
            results = legacy_db.DatabaseManager().execute_query(sql)

        tasks = []
        for row in results:
            tasks.append({
                'dispatch_no': str(row.get('派工号', '')),
                'table_no': str(row.get('表编号', '')),
                'serial_no': str(row.get('序列号', '')),
                'drawing_no': str(row.get('工装图号', '')),
                'tool_name': str(row.get('工装名称', '')),
                'acceptance_status': str(row.get('验收状态', '')),
                'keeper': str(row.get('保管员', '')),
                'inspector_check_date': _normalize_date(row.get('计划员检查完成日期')),
                'keeper_org_date': _normalize_date(row.get('保管员组织验收日期')),
                'qc_acceptance_date': _normalize_date(row.get('质检验收日期')),
                'process_acceptance_date': _normalize_date(row.get('工艺验收日期')),
                'acceptance_complete_date': _normalize_date(row.get('验收完成日期')),
                'create_time': _normalize_date(row.get('创建时间')),
                'modify_time': _normalize_date(row.get('修改时间'))
            })
        return tasks
    except Exception as e:
        legacy_db.logger.error(f"获取检验员验收任务失败: {str(e)}")
        return []


def start_inspection(dispatch_no: str, inspector: str) -> Dict:
    """开始检验"""
    try:
        sql = """
            UPDATE 工装验收管理_主表
            SET 验收状态 = '检查中',
                计划员检查完成日期 = GETDATE(),
                修改时间 = GETDATE()
            WHERE 派工号 = ?
        """
        legacy_db.DatabaseManager().execute_query(sql, (dispatch_no,), fetch=False)
        return {'success': True}
    except Exception as e:
        legacy_db.logger.error(f"开始检验失败: {str(e)}")
        return {'success': False, 'error': str(e)}


def submit_inspection_result(dispatch_no: str, result: str, **kwargs) -> Dict:
    """提交检验结果"""
    try:
        sql = """
            UPDATE 工装验收管理_主表
            SET 验收状态 = ?, 修改时间 = GETDATE()
            WHERE 派工号 = ?
        """
        status = '验收通过' if result == '通过' else '需整改'
        legacy_db.DatabaseManager().execute_query(sql, (status, dispatch_no), fetch=False)
        return {'success': True}
    except Exception as e:
        legacy_db.logger.error(f"提交检验结果失败: {str(e)}")
        return {'success': False, 'error': str(e)}


# ========================================
# API 端点需要的函数
# ========================================

def get_expiry_detail() -> List[Dict]:
    """获取定检到期预警详细数据"""
    try:
        tools = legacy_db.DatabaseManager().get_tool_basic_info()
        now = datetime.now()
        result = []
        for tool in tools:
            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            if not deadline:
                continue
            remaining = (deadline - now).days
            if remaining <= 180:
                result.append({
                    'serial_no': tool.get('serial_no', ''),
                    'drawing_no': tool.get('drawing_no', ''),
                    'tool_name': tool.get('tool_name', ''),
                    'deadline': tool.get('deadline', ''),
                    'remaining_days': remaining,
                    'dispatch_status': tool.get('dispatch_status', ''),
                    'attribute': tool.get('attribute', '')
                })
        return result
    except Exception as e:
        legacy_db.logger.error(f"获取定检到期详细数据失败: {str(e)}")
        return []


def get_dispatch_detail() -> List[Dict]:
    """获取派工进度详细数据"""
    try:
        dispatches = legacy_db.DatabaseManager().get_dispatch_info()
        return dispatches
    except Exception as e:
        legacy_db.logger.error(f"获取派工进度详细数据失败: {str(e)}")
        return []


def get_tpitr_status() -> Dict:
    """获取TPITR状态统计"""
    try:
        tpitrs = legacy_db.DatabaseManager().get_all_tpitr_info()
        stats = {
            'total': len(tpitrs),
            'published': 0,
            'pending': 0,
            'details': []
        }
        for tp in tpitrs:
            status = get_tpitr_status_detail(tp)
            if tp.get('valid_status') == '已发布':
                stats['published'] += 1
            else:
                stats['pending'] += 1
            stats['details'].append({
                'drawing_no': tp.get('drawing_no', ''),
                'version': tp.get('version', ''),
                'status': status['status'],
                'bottleneck': status['bottleneck']
            })
        return stats
    except Exception as e:
        legacy_db.logger.error(f"获取TPITR状态失败: {str(e)}")
        return {'total': 0, 'published': 0, 'pending': 0, 'details': []}


def get_acceptance_detail() -> List[Dict]:
    """获取验收状态明细"""
    try:
        return legacy_db.DatabaseManager().get_acceptance_info()
    except Exception as e:
        legacy_db.logger.error(f"获取验收状态明细失败: {str(e)}")
        return []


def get_tpitr_categories() -> Dict:
    """获取TPITR三分类数据"""
    try:
        db = legacy_db.DatabaseManager()
        tools = db.get_tool_basic_info()
        tpitrs = db.get_all_tpitr_info()

        tpitr_dict = {tp.get('drawing_no', ''): tp for tp in tpitrs if tp.get('drawing_no')}
        now = datetime.now()

        categories = {
            'has_tpitr': [],       # 有TPITR且已发布
            'in_use': [],          # 使用中但TPITR未发布
            'low_priority': []     # 封存或停用
        }

        seen = set()
        for tool in tools:
            drawing_no = tool.get('drawing_no', '')
            attribute = tool.get('attribute')
            app_history = tool.get('application_history', '')

            if attribute != '是' or not drawing_no or drawing_no in seen:
                continue
            seen.add(drawing_no)

            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            remaining = (deadline - now).days if deadline else None

            item = {
                'serial_no': tool.get('serial_no', ''),
                'drawing_no': drawing_no,
                'tool_name': tool.get('tool_name', ''),
                'deadline': tool.get('deadline', ''),
                'remaining_days': remaining,
                'application_history': app_history
            }

            if drawing_no in tpitr_dict:
                status = get_tpitr_status_detail(tpitr_dict[drawing_no])
                if status['status'] == '已完成':
                    categories['has_tpitr'].append(item)
                else:
                    if '封存' in app_history:
                        categories['low_priority'].append(item)
                    else:
                        categories['in_use'].append(item)
            else:
                if '封存' in app_history:
                    categories['low_priority'].append(item)
                else:
                    categories['in_use'].append(item)

        return {
            'has_tpitr_count': len(categories['has_tpitr']),
            'in_use_count': len(categories['in_use']),
            'low_priority_count': len(categories['low_priority']),
            'categories': categories
        }
    except Exception as e:
        legacy_db.logger.error(f"获取TPITR分类数据失败: {str(e)}")
        return {'has_tpitr_count': 0, 'in_use_count': 0, 'low_priority_count': 0, 'categories': {}}


def get_expired_tpitr_status() -> Dict:
    """获取超期工装TPITR状态"""
    try:
        db = legacy_db.DatabaseManager()
        tools = db.get_tool_basic_info()
        tpitrs = db.get_all_tpitr_info()

        tpitr_dict = {tp.get('drawing_no', ''): tp for tp in tpitrs if tp.get('drawing_no')}
        now = datetime.now()

        stats = {
            'total_expired': 0,
            'has_tpitr': 0,
            'missing_tpitr': 0,
            'expired_tools': []
        }

        for tool in tools:
            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            if not deadline:
                continue

            remaining = (deadline - now).days
            if remaining >= 0:
                continue

            stats['total_expired'] += 1
            drawing_no = tool.get('drawing_no', '')

            item = {
                'serial_no': tool.get('serial_no', ''),
                'drawing_no': drawing_no,
                'tool_name': tool.get('tool_name', ''),
                'deadline': tool.get('deadline', ''),
                'expired_days': abs(remaining)
            }

            if drawing_no in tpitr_dict:
                status = get_tpitr_status_detail(tpitr_dict[drawing_no])
                item['tpitr_status'] = status['status']
                if status['status'] == '已完成':
                    stats['has_tpitr'] += 1
                else:
                    stats['missing_tpitr'] += 1
            else:
                item['tpitr_status'] = '无TPITR'
                stats['missing_tpitr'] += 1

            stats['expired_tools'].append(item)

        return stats
    except Exception as e:
        legacy_db.logger.error(f"获取超期工装TPITR状态失败: {str(e)}")
        return {'total_expired': 0, 'has_tpitr': 0, 'missing_tpitr': 0, 'expired_tools': []}


def get_overdue_dispatch_status() -> Dict:
    """获取超期未完成派工数据"""
    try:
        db = legacy_db.DatabaseManager()
        tools = db.get_tool_basic_info()
        dispatches = db.get_dispatch_info()

        now = datetime.now()
        dispatch_map = {d['dispatch_no']: d for d in dispatches if d.get('dispatch_no')}

        stats = {
            'total_overdue': 0,
            'no_dispatch': 0,
            'dispatched': 0,
            'overdue_tools': []
        }

        for tool in tools:
            deadline = tool.get('effective_deadline_date') or tool.get('deadline_date')
            if not deadline:
                continue

            remaining = (deadline - now).days
            app_history = tool.get('application_history', '')
            status = tool.get('dispatch_status', '')

            if '使用中' not in app_history or remaining >= 0:
                continue

            stats['total_overdue'] += 1

            item = {
                'serial_no': tool.get('serial_no', ''),
                'drawing_no': tool.get('drawing_no', ''),
                'tool_name': tool.get('tool_name', ''),
                'deadline': tool.get('deadline', ''),
                'expired_days': abs(remaining),
                'dispatch_status': status
            }

            if '未派工' in status:
                stats['no_dispatch'] += 1
            elif '派工' in status:
                stats['dispatched'] += 1
                dispatch_no = None
                for d in dispatches:
                    if d.get('serial_no') == tool.get('serial_no'):
                        dispatch_no = d.get('dispatch_no')
                        break
                if dispatch_no and dispatch_no in dispatch_map:
                    item['dispatch_info'] = dispatch_map[dispatch_no]

            stats['overdue_tools'].append(item)

        return stats
    except Exception as e:
        legacy_db.logger.error(f"获取超期派工状态失败: {str(e)}")
        return {'total_overdue': 0, 'no_dispatch': 0, 'dispatched': 0, 'overdue_tools': []}


# ========================================
# 工装出入库管理模块 (Tool IO Management)
# ========================================

# 状态枚举
