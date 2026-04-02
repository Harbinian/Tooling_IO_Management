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
from backend.database.schema.column_names import TOOL_MASTER_COLUMNS, TOOL_MASTER_TABLE

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
        fetch: bool = True,
        conn: Any = None,
    ) -> List[Dict]:
        """Execute query SQL."""
        active_conn = conn
        owns_connection = active_conn is None
        cursor = None
        try:
            if active_conn is None:
                active_conn = self.connect()
            cursor = active_conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            if not fetch:
                if owns_connection:
                    active_conn.commit()
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
            if owns_connection and active_conn is not None:
                try:
                    active_conn.rollback()
                except Exception:
                    logger.warning("Rollback failed after query error", exc_info=True)
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"SQL: {sql}")
            raise
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    logger.warning("Failed to close cursor cleanly", exc_info=True)
            if owns_connection and active_conn is not None:
                self.close(active_conn)

    def execute_with_transaction(self, callback):
        """Execute a callback within a database transaction."""
        conn = None
        try:
            conn = self.connect()
            result = callback(conn)
            conn.commit()
            return result
        except Exception:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    logger.warning("Transaction rollback failed", exc_info=True)
            raise
        finally:
            if conn is not None:
                self.close(conn)

    # ========================================
    # Data query methods (from tool master)
    # ========================================

    def get_tool_basic_info(self) -> List[Dict]:
        """Get basic tool information from Tooling_ID_Main."""
        sql = f"""
            SELECT
                m.[{TOOL_MASTER_COLUMNS['tool_code']}] AS serial_no,
                m.[{TOOL_MASTER_COLUMNS['drawing_no']}] AS drawing_no,
                m.[{TOOL_MASTER_COLUMNS['tool_name']}] AS tool_name,
                m.[{TOOL_MASTER_COLUMNS['current_version']}] AS current_version,
                m.[{TOOL_MASTER_COLUMNS['manufacturing_version']}] AS manufacturing_version,
                m.[{TOOL_MASTER_COLUMNS['manufacturing_date']}] AS manufacturing_date,
                m.[{TOOL_MASTER_COLUMNS['inspection_cycle']}] AS inspection_cycle,
                m.[{TOOL_MASTER_COLUMNS['inspection_category']}] AS inspection_category,
                m.[{TOOL_MASTER_COLUMNS['inspection_expiry_date']}] AS inspection_expiry_date,
                m.[{TOOL_MASTER_COLUMNS['inspection_dispatch_status']}] AS inspection_dispatch_status,
                m.[{TOOL_MASTER_COLUMNS['inspection_remaining_days']}] AS inspection_remaining_days,
                m.[{TOOL_MASTER_COLUMNS['application_history']}] AS application_history
            FROM [{TOOL_MASTER_TABLE}] m
            WHERE m.[{TOOL_MASTER_COLUMNS['inspection_expiry_date']}] IS NOT NULL
              AND (m.[{TOOL_MASTER_COLUMNS['inspection_category']}] IS NULL OR m.[{TOOL_MASTER_COLUMNS['inspection_category']}] <> '否')
              AND (m.[{TOOL_MASTER_COLUMNS['application_history']}] IS NULL OR m.[{TOOL_MASTER_COLUMNS['application_history']}] NOT LIKE '%封存%')
        """

        results = self.execute_query(sql)

        tools = []
        now = datetime.now()

        from backend.database.utils.date_utils import normalize_date, format_date
        for row in results:
            deadline_date = normalize_date(row.get('inspection_expiry_date'))

            remaining_days = row.get('inspection_remaining_days')
            if remaining_days is None and deadline_date:
                remaining_days = (deadline_date - now).days
            elif remaining_days is not None:
                try:
                    remaining_days = int(remaining_days)
                except (ValueError, TypeError):
                    remaining_days = None

            tool = {
                'serial_no': row.get('serial_no', ''),
                'drawing_no': row.get('drawing_no', ''),
                'tool_name': row.get('tool_name', ''),
                'version': row.get('current_version', ''),
                'manufacture_version': row.get('manufacturing_version', ''),
                'manufacture_date': format_date(row.get('manufacturing_date')),
                'cycle': row.get('inspection_cycle', ''),
                'attribute': row.get('inspection_category', ''),
                'deadline': format_date(row.get('inspection_expiry_date')),
                'deadline_date': deadline_date,
                'dispatch_status': row.get('inspection_dispatch_status', ''),
                'remaining_days': remaining_days,
                'application_history': row.get('application_history', ''),
                'effective_deadline_date': deadline_date,
                'effective_remaining_days': remaining_days
            }
            tools.append(tool)

        return tools

    def get_dispatch_info(self) -> List[Dict]:
        """Get dispatch information."""
        sql = """
            SELECT
                d.序列号 AS serial_no,
                d.工装图号 AS drawing_no,
                d.派工号 AS dispatch_no,
                d.申请工装定检日期 AS apply_date,
                d.完成人 AS complete_person,
                d.完成日期 AS complete_date,
                d.申请人确认 AS applicant_confirm,
                d.TPITR AS tpitr,
                d.工装版次 AS tool_version,
                d.涉及分体组件数量 AS component_count,
                m.日期Date AS dispatch_date
            FROM 工装定检派工_明细 d
            LEFT JOIN 工装定检派工_主表 m ON d.ExcelServerRCID = m.ExcelServerRCID AND d.ExcelServerWIID = m.ExcelServerWIID
            ORDER BY m.日期Date DESC
        """
        results = self.execute_query(sql)

        from backend.database.utils.date_utils import normalize_date
        dispatches = []
        for row in results:
            dispatches.append({
                'serial_no': row.get('serial_no', ''),
                'drawing_no': row.get('drawing_no', ''),
                'dispatch_no': row.get('dispatch_no', ''),
                'apply_date': normalize_date(row.get('apply_date')),
                'complete_person': row.get('complete_person', ''),
                'complete_date': normalize_date(row.get('complete_date')),
                'applicant_confirm': row.get('applicant_confirm', ''),
                'tpitr': row.get('tpitr', ''),
                'tool_version': row.get('tool_version', ''),
                'component_count': row.get('component_count', ''),
                'dispatch_date': normalize_date(row.get('dispatch_date'))
            })
        return dispatches

    def get_all_tpitr_info(self) -> List[Dict]:
        """Get all TPITR information."""
        sql = """
            SELECT
                工装图号 AS drawing_no,
                版次 AS version,
                编制 AS author,
                编制日期 AS author_date,
                校对人 AS checker,
                校对日期 AS check_date,
                校对结论 AS check_conclusion,
                批准人 AS approver,
                批准日期 AS approve_date,
                批准结论 AS approve_conclusion,
                会签人 AS signer,
                质量会签日期 AS sign_date,
                会签结论 AS sign_conclusion,
                有效状态 AS valid_status,
                编号No AS tpitr_no,
                校对意见 AS check_comment,
                批准意见 AS approve_comment,
                会签意见 AS sign_comment
            FROM TPITR_主表_V11
        """
        results = self.execute_query(sql)

        from backend.database.utils.date_utils import normalize_date
        tpitrs = []
        for row in results:
            tpitrs.append({
                'drawing_no': row.get('drawing_no', ''),
                'version': row.get('version', ''),
                'author': row.get('author', ''),
                'author_date': normalize_date(row.get('author_date')),
                'checker': row.get('checker', ''),
                'check_date': normalize_date(row.get('check_date')),
                'check_conclusion': row.get('check_conclusion', ''),
                'approver': row.get('approver', ''),
                'approve_date': normalize_date(row.get('approve_date')),
                'approve_conclusion': row.get('approve_conclusion', ''),
                'signer': row.get('signer', ''),
                'sign_date': normalize_date(row.get('sign_date')),
                'sign_conclusion': row.get('sign_conclusion', ''),
                'valid_status': row.get('valid_status', ''),
                'tpitr_no': row.get('tpitr_no', ''),
                'check_comment': row.get('check_comment', ''),
                'approve_comment': row.get('approve_comment', ''),
                'sign_comment': row.get('sign_comment', '')
            })
        return tpitrs

    def get_acceptance_info(self) -> List[Dict]:
        """Get acceptance information."""
        try:
            sql = """
                SELECT
                    m.派工号 AS dispatch_no,
                    m.表编号 AS table_no,
                    m.序列号 AS serial_no,
                    m.验收状态 AS acceptance_status,
                    m.计划员检查完成日期 AS inspector_check_date,
                    m.保管员组织验收日期 AS keeper_org_date,
                    m.质检验收日期 AS qc_acceptance_date,
                    m.工艺验收日期 AS process_acceptance_date,
                    m.验收完成日期 AS acceptance_complete_date,
                    m.保管员 AS keeper,
                    m.联合验收说明 AS acceptance_note,
                    m.最新通知单号 AS notice_no,
                    m.备注 AS remarks,
                    m.创建时间 AS create_time,
                    m.修改时间 AS modify_time
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
                'dispatch_no': str(row.get('dispatch_no', '')) if row.get('dispatch_no') else '',
                'table_no': str(row.get('table_no', '')) if row.get('table_no') else '',
                'serial_no': str(row.get('serial_no', '')) if row.get('serial_no') else '',
                'acceptance_status': str(row.get('acceptance_status', '')) if row.get('acceptance_status') else '待检查',
                'inspector_check_date': normalize_date(row.get('inspector_check_date')),
                'keeper_org_date': normalize_date(row.get('keeper_org_date')),
                'qc_acceptance_date': normalize_date(row.get('qc_acceptance_date')),
                'process_acceptance_date': normalize_date(row.get('process_acceptance_date')),
                'acceptance_complete_date': normalize_date(row.get('acceptance_complete_date')),
                'keeper': str(row.get('keeper', '')) if row.get('keeper') else '',
                'acceptance_note': str(row.get('acceptance_note', '')) if row.get('acceptance_note') else '',
                'notice_no': str(row.get('notice_no', '')) if row.get('notice_no') else '',
                'remarks': str(row.get('remarks', '')) if row.get('remarks') else '',
                'create_time': normalize_date(row.get('create_time')),
                'modify_time': normalize_date(row.get('modify_time'))
            })
        return acceptances

    def get_nonconforming_notices(self) -> List[Dict]:
        """Get non-conforming tool notices."""
        try:
            sql = """
                SELECT
                    m.通知单号 AS notice_no,
                    m.关联派工号 AS dispatch_no,
                    m.关联表编号 AS table_no,
                    m.序列号 AS serial_no,
                    m.检验员 AS inspector,
                    m.编制人 AS creator,
                    m.编制日期 AS create_date_raw,
                    m.处理状态 AS process_status,
                    m.复检日期 AS recheck_date_raw,
                    m.复检结论 AS recheck_conclusion,
                    m.复检人 AS rechecker,
                    m.关闭日期 AS close_date_raw,
                    m.关闭人 AS closer,
                    m.关闭说明 AS close_note,
                    m.创建时间 AS create_time_raw
                FROM 不合格工装通知单_主表 m
                ORDER BY m.创建时间 DESC
            """
            results = self.execute_query(sql)

            from backend.database.utils.date_utils import normalize_date
            notices = []
            for row in results:
                notices.append({
                    'notice_no': str(row.get('notice_no', '')),
                    'dispatch_no': str(row.get('dispatch_no', '')),
                    'table_no': str(row.get('table_no', '')),
                    'serial_no': str(row.get('serial_no', '')),
                    'inspector': str(row.get('inspector', '')),
                    'creator': str(row.get('creator', '')),
                    'create_date': normalize_date(row.get('create_date_raw')),
                    'process_status': str(row.get('process_status', '待处理')),
                    'recheck_date': normalize_date(row.get('recheck_date_raw')),
                    'recheck_conclusion': str(row.get('recheck_conclusion', '')),
                    'rechecker': str(row.get('rechecker', '')),
                    'close_date': normalize_date(row.get('close_date_raw')),
                    'closer': str(row.get('closer', '')),
                    'close_note': str(row.get('close_note', '')),
                    'create_time': normalize_date(row.get('create_time_raw'))
                })
            return notices
        except Exception as e:
            logger.warning(f"Failed to get nonconforming notices: {str(e)}")
            return []

    def get_inspection_records(self) -> List[Dict]:
        """Get tool inspection records."""
        try:
            sql = """
                SELECT
                    序列号 AS serial_no,
                    工装名称 AS tool_name,
                    工装图号 AS drawing_no,
                    ExcelServerRCID AS rcid,
                    ExcelServerWIID AS wiid
                FROM 工装定检记录_主表
                ORDER BY 序号 DESC
            """
            results = self.execute_query(sql)
            return [{'serial_no': r.get('serial_no', ''),
                     'tool_name': r.get('tool_name', ''),
                     'drawing_no': r.get('drawing_no', ''),
                     'rcid': r.get('rcid', ''),
                     'wiid': r.get('wiid', '')} for r in results]
        except Exception as e:
            logger.warning(f"Failed to get inspection records: {str(e)}")
            return []

    def get_repair_records(self) -> List[Dict]:
        """Get tool repair records."""
        try:
            sql = """
                SELECT
                    序列号 AS serial_no,
                    工装名称 AS tool_name,
                    工装图号 AS drawing_no,
                    ExcelServerRCID AS rcid,
                    ExcelServerWIID AS wiid
                FROM 工装返修记录_主表
                ORDER BY 序号 DESC
            """
            results = self.execute_query(sql)
            return [{'serial_no': r.get('serial_no', ''),
                     'tool_name': r.get('tool_name', ''),
                     'drawing_no': r.get('drawing_no', ''),
                     'rcid': r.get('rcid', ''),
                     'wiid': r.get('wiid', '')} for r in results]
        except Exception as e:
            logger.warning(f"Failed to get repair records: {str(e)}")
            return []

    def get_new_rework_applications(self) -> List[Dict]:
        """Get unsynced rework applications."""
        sql = f"""
            SELECT
                r.OA申请单编号 AS oa_no,
                r.派工号 AS dispatch_no,
                r.序列号 AS serial_no,
                r.工装图号 AS drawing_no,
                r.工装名称 AS tool_name,
                r.返工类型 AS rework_type,
                r.目标版次 AS target_version,
                r.返工内容 AS rework_content,
                r.需求日期 AS required_date_raw,
                r.转录人 AS transcriber,
                r.转录日期 AS transcribe_date_raw,
                r.验收日期 AS acceptance_date_raw,
                r.验收人员 AS acceptor,
                r.工装计划员 AS planner,
                r.计划确认日期 AS confirm_date_raw,
                t.[{TOOL_MASTER_COLUMNS['current_version']}] AS card_version
            FROM 工艺装备返工申请单_主表 r
            LEFT JOIN [{TOOL_MASTER_TABLE}] t ON r.序列号 = t.[{TOOL_MASTER_COLUMNS['tool_code']}]
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
            SELECT
                n.编号 AS apply_no,
                n.派工号 AS dispatch_no,
                n.工装序列号 AS serial_no,
                n.工装图号 AS drawing_no,
                n.工装名称 AS tool_name,
                n.项目代号 AS project_code,
                n.版次 AS version,
                n.工作包 AS work_package,
                n.制造依据 AS manufacture_basis,
                n.技术要求 AS tech_requirement,
                n.转录人员 AS transcriber,
                n.转录日期 AS transcribe_date_raw,
                n.预计使用时间 AS expected_use_date_raw,
                n.目标版次 AS target_version
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
                'oa_no': row.get('oa_no', ''),
                'apply_no': row.get('apply_no', ''),
                'dispatch_no': row.get('dispatch_no', ''),
                'serial_no': row.get('serial_no', ''),
                'drawing_no': row.get('drawing_no', ''),
                'tool_name': row.get('tool_name', ''),
                'rework_type': row.get('rework_type', ''),
                'target_version': row.get('target_version', ''),
                'rework_content': row.get('rework_content', ''),
                'required_date': normalize_date(row.get('required_date_raw')),
                'transcriber': row.get('transcriber', ''),
                'transcribe_date': normalize_date(row.get('transcribe_date_raw')),
                'acceptance_date': normalize_date(row.get('acceptance_date_raw')),
                'acceptor': row.get('acceptor', ''),
                'planner': row.get('planner', ''),
                'confirm_date': normalize_date(row.get('confirm_date_raw')),
                'card_version': row.get('card_version', ''),
                'version': row.get('version', ''),
                'project_code': row.get('project_code', ''),
                'work_package': row.get('work_package', ''),
                'manufacture_basis': row.get('manufacture_basis', ''),
                'tech_requirement': row.get('tech_requirement', ''),
                'expected_use_date': normalize_date(row.get('expected_use_date_raw')),
                'application_type': app_type
            })
        return apps


# Global database manager instance
db_manager = DatabaseManager()
