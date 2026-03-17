# -*- coding: utf-8 -*-
"""
Database manager with connection pool.
"""

import os
import sys
import logging
import threading
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from contextlib import contextmanager

# Add project root to path
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Try to import unified config
try:
    from config.settings import settings
    _USE_UNIFIED_CONFIG = True
except ImportError:
    _USE_UNIFIED_CONFIG = False

from backend.database.core.connection_pool import ConnectionPool

logger = logging.getLogger(__name__)

ORDER_NO_SEQUENCE_TABLE = "tool_io_order_no_sequence"
ORDER_NO_RETRY_LIMIT = 3


class DatabaseManager:
    """Database manager with connection pool."""

    _instance = None
    _pool: Optional[ConnectionPool] = None
    _pool_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Load configuration
        if _USE_UNIFIED_CONFIG and getattr(settings, 'db', None) is not None:
            db_settings = settings.db
            self.db_config = {
                'server': getattr(db_settings, 'server', os.getenv('CESOFT_DB_SERVER', '192.168.19.220,1433')),
                'database': getattr(db_settings, 'database', os.getenv('CESOFT_DB_DATABASE', 'CXSYSYS')),
                'username': getattr(db_settings, 'username', os.getenv('CESOFT_DB_USERNAME', 'sa')),
                'password': getattr(db_settings, 'password', os.getenv('CESOFT_DB_PASSWORD', '')),
                'driver': getattr(db_settings, 'driver', os.getenv('CESOFT_DB_DRIVER', '{SQL Server}')),
                'timeout': getattr(db_settings, 'timeout_seconds', int(os.getenv('CESOFT_DB_TIMEOUT', '30')))
            }
            pool_size = getattr(db_settings, 'pool_size', int(os.getenv('CESOFT_DB_POOL_SIZE', '5')))
        else:
            self.db_config = {
                'server': os.getenv('CESOFT_DB_SERVER', '192.168.19.220,1433'),
                'database': os.getenv('CESOFT_DB_DATABASE', 'CXSYSYS'),
                'username': os.getenv('CESOFT_DB_USERNAME', 'sa'),
                'password': os.getenv('CESOFT_DB_PASSWORD', ''),
                'driver': os.getenv('CESOFT_DB_DRIVER', '{SQL Server}'),
                'timeout': int(os.getenv('CESOFT_DB_TIMEOUT', '30'))
            }
            pool_size = int(os.getenv('CESOFT_DB_POOL_SIZE', '5'))

        # Build connection string
        self._connection_string = (
            f"DRIVER={self.db_config['driver']};"
            f"SERVER={self.db_config['server']};"
            f"DATABASE={self.db_config['database']};"
            f"UID={self.db_config['username']};"
            f"PWD={self.db_config['password']};"
            f"TrustServerCertificate=yes"
        )

        # Initialize connection pool
        self._init_pool(pool_size)
        self._initialized = True

        logger.info(f"DatabaseManager initialized, connection pool size: {pool_size}")

    def _init_pool(self, pool_size: int):
        """Initialize connection pool."""
        with self._pool_lock:
            if self._pool is not None:
                self._pool.close_all()
            self._pool = ConnectionPool(
                connection_string=self._connection_string,
                pool_size=pool_size,
                max_retries=3,
                timeout_seconds=self.db_config.get('timeout', 30)
            )

    def connect(self) -> Any:
        """Get a database connection (from pool)."""
        if self._pool is None:
            # Fallback to direct connection
            import pyodbc
            return pyodbc.connect(self._connection_string, timeout=30)
        return self._pool.get_connection()

    def close(self, conn: Any):
        """Close connection (return to pool)."""
        if self._pool is not None:
            self._pool.release_connection(conn)
        else:
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def get_connection(self):
        """Context manager for connection acquisition."""
        conn = self.connect()
        try:
            yield conn
        finally:
            self.close(conn)

    def test_connection(self) -> Tuple[bool, str]:
        """Test database connection."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            self.close(conn)
            logger.info("Database connection test successful")
            return True, "Connection successful"
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False, str(e)

    def execute_query(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        fetch: bool = True
    ) -> List[Dict]:
        """Execute query SQL."""
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            if not fetch:
                conn.commit()
                return []

            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Standardize datetime types
                    if isinstance(value, datetime):
                        value = value  # Keep datetime object
                    elif value is None:
                        value = None
                    row_dict[col] = value
                result.append(row_dict)

            logger.info(f"Query successful, returned {len(result)} records")
            return result

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"SQL: {sql}")
            raise
        finally:
            if conn:
                self.close(conn)

    # ========================================
    # Data query methods (from tool master)
    # ========================================

    def get_tool_basic_info(self) -> List[Dict]:
        """Get basic tool information from Tooling_ID_Main."""
        sql = """
            SELECT
                m.序列号,
                m.工装图号,
                m.工装名称,
                m.当前版次,
                m.制造版次,
                m.制造日期,
                m.定检周期,
                m.定检属性,
                m.定检有效截止,
                m.定检派工状态,
                m.定检有效期剩余天,
                m.应用历史
            FROM Tooling_ID_Main m
            WHERE m.定检有效截止 IS NOT NULL
              AND (m.定检属性 IS NULL OR m.定检属性 <> '否')
              AND (m.应用历史 IS NULL OR m.应用历史 NOT LIKE '%封存%')
        """

        results = self.execute_query(sql)

        tools = []
        now = datetime.now()

        from backend.database.utils.date_utils import normalize_date, format_date
        for row in results:
            deadline_date = normalize_date(row.get('定检有效截止'))

            remaining_days = row.get('定检有效期剩余天')
            if remaining_days is None and deadline_date:
                remaining_days = (deadline_date - now).days
            elif remaining_days is not None:
                try:
                    remaining_days = int(remaining_days)
                except (ValueError, TypeError):
                    remaining_days = None

            tool = {
                'serial_no': row.get('序列号', ''),
                'drawing_no': row.get('工装图号', ''),
                'tool_name': row.get('工装名称', ''),
                'version': row.get('当前版次', ''),
                'manufacture_version': row.get('制造版次', ''),
                'manufacture_date': format_date(row.get('制造日期')),
                'cycle': row.get('定检周期', ''),
                'attribute': row.get('定检属性', ''),
                'deadline': format_date(row.get('定检有效截止')),
                'deadline_date': deadline_date,
                'dispatch_status': row.get('定检派工状态', ''),
                'remaining_days': remaining_days,
                'application_history': row.get('应用历史', ''),
                'effective_deadline_date': deadline_date,
                'effective_remaining_days': remaining_days
            }
            tools.append(tool)

        return tools

    def get_dispatch_info(self) -> List[Dict]:
        """Get dispatch information."""
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
            ORDER BY m.日期Date DESC
        """
        results = self.execute_query(sql)

        from backend.database.utils.date_utils import normalize_date
        dispatches = []
        for row in results:
            dispatches.append({
                'serial_no': row.get('序列号', ''),
                'drawing_no': row.get('工装图号', ''),
                'dispatch_no': row.get('派工号', ''),
                'apply_date': normalize_date(row.get('申请工装定检日期')),
                'complete_person': row.get('完成人', ''),
                'complete_date': normalize_date(row.get('完成日期')),
                'applicant_confirm': row.get('申请人确认', ''),
                'tpitr': row.get('TPITR', ''),
                'tool_version': row.get('工装版次', ''),
                'component_count': row.get('涉及分体组件数量', ''),
                'dispatch_date': normalize_date(row.get('派工日期'))
            })
        return dispatches

    def get_all_tpitr_info(self) -> List[Dict]:
        """Get all TPITR information."""
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
        """
        results = self.execute_query(sql)

        from backend.database.utils.date_utils import normalize_date
        tpitrs = []
        for row in results:
            tpitrs.append({
                'drawing_no': row.get('工装图号', ''),
                'version': row.get('版次', ''),
                'author': row.get('编制', ''),
                'author_date': normalize_date(row.get('编制日期')),
                'checker': row.get('校对人', ''),
                'check_date': normalize_date(row.get('校对日期')),
                'check_conclusion': row.get('校对结论', ''),
                'approver': row.get('批准人', ''),
                'approve_date': normalize_date(row.get('批准日期')),
                'approve_conclusion': row.get('批准结论', ''),
                'signer': row.get('会签人', ''),
                'sign_date': normalize_date(row.get('质量会签日期')),
                'sign_conclusion': row.get('会签结论', ''),
                'valid_status': row.get('有效状态', ''),
                'tpitr_no': row.get('编号No', ''),
                'check_comment': row.get('校对意见', ''),
                'approve_comment': row.get('批准意见', ''),
                'sign_comment': row.get('会签意见', '')
            })
        return tpitrs

    def get_acceptance_info(self) -> List[Dict]:
        """Get acceptance information."""
        try:
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
                ORDER BY m.修改时间 DESC
            """
            results = self.execute_query(sql)
        except Exception as e:
            logger.warning(f"Failed to get acceptance info (table may not exist): {str(e)}")
            return []

        from backend.database.utils.date_utils import normalize_date
        acceptances = []
        for row in results:
            acceptances.append({
                'dispatch_no': str(row.get('派工号', '')) if row.get('派工号') else '',
                'table_no': str(row.get('表编号', '')) if row.get('表编号') else '',
                'serial_no': str(row.get('序列号', '')) if row.get('序列号') else '',
                'acceptance_status': str(row.get('验收状态', '')) if row.get('验收状态') else '待检查',
                'inspector_check_date': normalize_date(row.get('计划员检查完成日期')),
                'keeper_org_date': normalize_date(row.get('保管员组织验收日期')),
                'qc_acceptance_date': normalize_date(row.get('质检验收日期')),
                'process_acceptance_date': normalize_date(row.get('工艺验收日期')),
                'acceptance_complete_date': normalize_date(row.get('验收完成日期')),
                'keeper': str(row.get('保管员', '')) if row.get('保管员') else '',
                'acceptance_note': str(row.get('联合验收说明', '')) if row.get('联合验收说明') else '',
                'notice_no': str(row.get('最新通知单号', '')) if row.get('最新通知单号') else '',
                'remarks': str(row.get('备注', '')) if row.get('备注') else '',
                'create_time': normalize_date(row.get('创建时间')),
                'modify_time': normalize_date(row.get('修改时间'))
            })
        return acceptances

    def get_nonconforming_notices(self) -> List[Dict]:
        """Get non-conforming tool notices."""
        try:
            sql = """
                SELECT
                    m.通知单号, m.关联派工号, m.关联表编号, m.序列号,
                    m.检验员, m.编制人, m.编制日期, m.处理状态,
                    m.复检日期, m.复检结论, m.复检人,
                    m.关闭日期, m.关闭人, m.关闭说明, m.创建时间
                FROM 不合格工装通知单_主表 m
                ORDER BY m.创建时间 DESC
            """
            results = self.execute_query(sql)

            from backend.database.utils.date_utils import normalize_date
            notices = []
            for row in results:
                notices.append({
                    'notice_no': str(row.get('通知单号', '')),
                    'dispatch_no': str(row.get('关联派工号', '')),
                    'table_no': str(row.get('关联表编号', '')),
                    'serial_no': str(row.get('序列号', '')),
                    'inspector': str(row.get('检验员', '')),
                    'creator': str(row.get('编制人', '')),
                    'create_date': normalize_date(row.get('编制日期')),
                    'process_status': str(row.get('处理状态', '待处理')),
                    'recheck_date': normalize_date(row.get('复检日期')),
                    'recheck_conclusion': str(row.get('复检结论', '')),
                    'rechecker': str(row.get('复检人', '')),
                    'close_date': normalize_date(row.get('关闭日期')),
                    'closer': str(row.get('关闭人', '')),
                    'close_note': str(row.get('关闭说明', '')),
                    'create_time': normalize_date(row.get('创建时间'))
                })
            return notices
        except Exception as e:
            logger.warning(f"Failed to get nonconforming notices: {str(e)}")
            return []

    def get_inspection_records(self) -> List[Dict]:
        """Get tool inspection records."""
        try:
            sql = """
                SELECT 序列号, 工装名称, 工装图号, ExcelServerRCID, ExcelServerWIID
                FROM 工装定检记录_主表 ORDER BY 序号 DESC
            """
            results = self.execute_query(sql)
            return [{'serial_no': r.get('序列号', ''),
                     'tool_name': r.get('工装名称', ''),
                     'drawing_no': r.get('工装图号', ''),
                     'rcid': r.get('ExcelServerRCID', ''),
                     'wiid': r.get('ExcelServerWIID', '')} for r in results]
        except Exception as e:
            logger.warning(f"Failed to get inspection records: {str(e)}")
            return []

    def get_repair_records(self) -> List[Dict]:
        """Get tool repair records."""
        try:
            sql = """
                SELECT 序列号, 工装名称, 工装图号, ExcelServerRCID, ExcelServerWIID
                FROM 工装返修记录_主表 ORDER BY 序号 DESC
            """
            results = self.execute_query(sql)
            return [{'serial_no': r.get('序列号', ''),
                     'tool_name': r.get('工装名称', ''),
                     'drawing_no': r.get('工装图号', ''),
                     'rcid': r.get('ExcelServerRCID', ''),
                     'wiid': r.get('ExcelServerWIID', '')} for r in results]
        except Exception as e:
            logger.warning(f"Failed to get repair records: {str(e)}")
            return []

    def get_new_rework_applications(self) -> List[Dict]:
        """Get unsynced rework applications."""
        sql = """
            SELECT r.OA申请单编号, r.派工号, r.序列号, r.工装图号, r.工装名称,
                   r.返工类型, r.目标版次, r.返工内容, r.需求日期, r.转录人, r.转录日期,
                   r.验收日期, r.验收人员, r.工装计划员, r.计划确认日期, t.当前版次 as 身份卡版次
            FROM 工艺装备返工申请单_主表 r
            LEFT JOIN Tooling_ID_Main t ON r.序列号 = t.序列号
            WHERE r.OA申请单编号 IS NOT NULL
              AND r.派工号 NOT LIKE 'C%'
              AND NOT EXISTS (SELECT 1 FROM 工装验收管理_主表 m WHERE m.派工号 = r.派工号)
              AND (r.子项类型 = '外协返修' OR r.返工类型 = '升版返修')
            ORDER BY r.转录日期 DESC
        """
        results = self.execute_query(sql)
        return self._parse_application_results(results, '返工')

    def get_new_tooling_applications(self) -> List[Dict]:
        """Get unsynced new tooling applications."""
        sql = """
            SELECT n.编号, n.派工号, n.工装序列号, n.工装图号, n.工装名称,
                   n.项目代号, n.版次, n.工作包, n.制造依据, n.技术要求,
                   n.转录人员, n.转录日期, n.预计使用时间, n.目标版次
            FROM 工艺装备申请单_主表 n
            WHERE n.编号 IS NOT NULL
              AND n.操作类型 IN ('新建', '效率复制')
              AND n.派工号 NOT LIKE 'C%'
              AND NOT EXISTS (SELECT 1 FROM 工装验收管理_主表 m WHERE m.派工号 = n.派工号)
              AND NOT EXISTS (
                  SELECT 1 FROM 工艺装备返工申请单_主表 r
                  WHERE r.派工号 = n.派工号
                    AND (r.子项类型 = '外协返修' OR r.返工类型 = '升版返修')
              )
            ORDER BY n.转录日期 DESC
        """
        results = self.execute_query(sql)
        return self._parse_application_results(results, '新制')

    def _parse_application_results(self, results: List[Dict], app_type: str) -> List[Dict]:
        """Parse application results."""
        from backend.database.utils.date_utils import normalize_date
        apps = []
        for row in results:
            apps.append({
                'oa_no': row.get('OA申请单编号', ''),
                'apply_no': row.get('编号', ''),
                'dispatch_no': row.get('派工号', ''),
                'serial_no': row.get('序列号') or row.get('工装序列号', ''),
                'drawing_no': row.get('工装图号', ''),
                'tool_name': row.get('工装名称', ''),
                'rework_type': row.get('返工类型', ''),
                'target_version': row.get('目标版次', ''),
                'rework_content': row.get('返工内容', ''),
                'required_date': normalize_date(row.get('需求日期')),
                'transcriber': row.get('转录人') or row.get('转录人员', ''),
                'transcribe_date': normalize_date(row.get('转录日期')),
                'acceptance_date': normalize_date(row.get('验收日期')),
                'acceptor': row.get('验收人员', ''),
                'planner': row.get('工装计划员', ''),
                'confirm_date': normalize_date(row.get('计划确认日期')),
                'card_version': row.get('身份卡版次', ''),
                'version': row.get('版次', ''),
                'project_code': row.get('项目代号', ''),
                'work_package': row.get('工作包', ''),
                'manufacture_basis': row.get('制造依据', ''),
                'tech_requirement': row.get('技术要求', ''),
                'expected_use_date': normalize_date(row.get('预计使用时间')),
                'application_type': app_type
            })
        return apps


# Global database manager instance
db_manager = DatabaseManager()
