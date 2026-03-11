# -*- coding: utf-8 -*-
"""
工装定检全流程监控系统 - 数据库连接模块
========================================
功能: 提供数据库连接和查询功能（含连接池）
版本: V4.0 (连接池 + 优化查询)
日期: 2025-01-23
========================================

支持:
- 环境变量配置 (CESOFT_ 前缀)
- 统一配置层 config.settings
- 数据库连接池
- 连接复用
- 日期类型标准化

环境变量配置:
  CESOFT_DB_SERVER     - 数据库服务器地址 (默认: 192.168.19.220,1433)
  CESOFT_DB_DATABASE   - 数据库名称 (默认: CXSYSYS)
  CESOFT_DB_USERNAME   - 用户名 (默认: sa)
  CESOFT_DB_PASSWORD   - 密码
  CESOFT_DB_DRIVER     - ODBC驱动 (默认: {SQL Server})
  CESOFT_DB_POOL_SIZE  - 连接池大小 (默认: 5)
  CESOFT_DB_POOL_TIMEOUT - 连接超时(秒) (默认: 30)
========================================
"""

import pyodbc
import os
import sys
import logging
import threading
import time
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from contextlib import contextmanager
from dataclasses import dataclass

# 添加项目根目录到路径
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# 尝试导入统一配置层
try:
    from config.settings import settings
    _USE_UNIFIED_CONFIG = True
except ImportError:
    _USE_UNIFIED_CONFIG = False

logger = logging.getLogger(__name__)

ORDER_NO_SEQUENCE_TABLE = "tool_io_order_no_sequence"
ORDER_NO_RETRY_LIMIT = 3
SCHEMA_ALIGNMENT_INDEXES = (
    ("工装出入库单_主表", "IX_工装出入库单_主表_单据类型", "单据类型"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_单据状态", "单据状态"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_发起人ID", "发起人ID"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_保管员ID", "保管员ID"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_创建时间", "创建时间"),
    ("工装出入库单_明细", "IX_工装出入库单_明细_出入库单号", "出入库单号"),
    ("工装出入库单_明细", "IX_工装出入库单_明细_工装编码", "工装编码"),
    ("工装出入库单_明细", "IX_工装出入库单_明细_明细状态", "明细状态"),
    ("工装出入库单_操作日志", "IX_工装出入库单_操作日志_出入库单号", "出入库单号"),
    ("工装出入库单_操作日志", "IX_工装出入库单_操作日志_操作时间", "操作时间"),
    ("工装出入库单_通知记录", "IX_工装出入库单_通知记录_出入库单号", "出入库单号"),
    ("工装出入库单_通知记录", "IX_工装出入库单_通知记录_发送状态", "发送状态"),
    ("工装出入库单_通知记录", "IX_工装出入库单_通知记录_通知渠道", "通知渠道"),
)


def _is_duplicate_key_error(error: Exception) -> bool:
    message = str(error).lower()
    return (
        "duplicate" in message
        or "unique" in message
        or "2601" in message
        or "2627" in message
    )


def _quote_sql_string(value: str) -> str:
    return value.replace("'", "''")


def _build_add_column_sql(table_name: str, column_name: str, definition: str) -> str:
    quoted_table = _quote_sql_string(table_name)
    quoted_column = _quote_sql_string(column_name)
    return f"""
    IF COL_LENGTH(N'{quoted_table}', N'{quoted_column}') IS NULL
    BEGIN
        ALTER TABLE [{table_name}] ADD [{column_name}] {definition}
    END
    """


def _build_create_index_sql(table_name: str, index_name: str, column_list: str) -> str:
    quoted_table = _quote_sql_string(table_name)
    quoted_index = _quote_sql_string(index_name)
    return f"""
    IF NOT EXISTS (
        SELECT 1
        FROM sys.indexes
        WHERE name = N'{quoted_index}'
          AND object_id = OBJECT_ID(N'{quoted_table}')
    )
    BEGIN
        CREATE INDEX [{index_name}] ON [{table_name}] ({column_list})
    END
    """


def _build_schema_alignment_sql() -> List[str]:
    sql_statements = [
        _build_add_column_sql("工装出入库单_主表", "工装数量", "INT NULL"),
        _build_add_column_sql("工装出入库单_主表", "已确认数量", "INT NULL"),
        _build_add_column_sql("工装出入库单_主表", "最终确认人", "VARCHAR(64) NULL"),
        _build_add_column_sql("工装出入库单_主表", "取消原因", "VARCHAR(500) NULL"),
        _build_add_column_sql("工装出入库单_明细", "确认时间", "DATETIME NULL"),
        _build_add_column_sql("工装出入库单_明细", "出入库完成时间", "DATETIME NULL"),
    ]

    for table_name, index_name, column_list in SCHEMA_ALIGNMENT_INDEXES:
        sql_statements.append(_build_create_index_sql(table_name, index_name, column_list))

    return sql_statements


# ========================================
# 连接池实现
# ========================================

class ConnectionPool:
    """
    数据库连接池

    特性:
    - 预创建指定数量的连接
    - 连接复用，减少创建开销
    - 线程安全
    - 连接健康检查
    """

    def __init__(
        self,
        connection_string: str,
        pool_size: int = 5,
        max_retries: int = 3,
        timeout_seconds: int = 30
    ):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

        self._pool: List[pyodbc.Connection] = []
        self._lock = threading.Lock()
        self._last_check = 0
        self._check_interval = 60  # 60秒检查一次连接健康

    def _create_connection(self) -> Optional[pyodbc.Connection]:
        """创建新连接"""
        for attempt in range(self.max_retries):
            try:
                conn = pyodbc.connect(self.connection_string, timeout=self.timeout_seconds)
                logger.debug(f"创建数据库连接 (尝试 {attempt + 1})")
                return conn
            except Exception as e:
                logger.warning(f"创建连接失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(1)
        return None

    def _is_connection_valid(self, conn: pyodbc.Connection) -> bool:
        """检查连接是否有效"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False

    def get_connection(self) -> pyodbc.Connection:
        """从池中获取连接"""
        with self._lock:
            # 检查并清理失效连接
            now = time.time()
            if now - self._last_check > self._check_interval:
                self._pool = [c for c in self._pool if self._is_connection_valid(c)]
                self._last_check = now

            # 复用现有连接
            if self._pool:
                return self._pool.pop()

        # 创建新连接
        conn = self._create_connection()
        if conn is None:
            raise ConnectionError("无法创建数据库连接")
        return conn

    def release_connection(self, conn: pyodbc.Connection):
        """将连接归还到池中"""
        with self._lock:
            if self._is_connection_valid(conn):
                if len(self._pool) < self.pool_size:
                    self._pool.append(conn)
                else:
                    try:
                        conn.close()
                    except Exception:
                        pass
            else:
                try:
                    conn.close()
                except Exception:
                    pass

    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._pool.clear()

    @property
    def size(self) -> int:
        """当前池中连接数"""
        with self._lock:
            return len(self._pool)


# ========================================
# 日期处理工具
# ========================================

def _normalize_date(value: Any) -> Optional[datetime]:
    """标准化日期值"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        value = value.strip()
        for fmt in [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d',
            '%Y%m%d'
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def _format_date(value: Any, fmt: str = '%Y-%m-%d') -> str:
    """格式化日期为字符串"""
    dt = _normalize_date(value)
    if dt is None:
        return ''
    return dt.strftime(fmt)


# ========================================
# 数据库管理器
# ========================================

class DatabaseManager:
    """数据库管理器（含连接池）"""

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

        # 加载配置
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

        # 构建连接字符串
        self._connection_string = (
            f"DRIVER={self.db_config['driver']};"
            f"SERVER={self.db_config['server']};"
            f"DATABASE={self.db_config['database']};"
            f"UID={self.db_config['username']};"
            f"PWD={self.db_config['password']};"
            f"TrustServerCertificate=yes"
        )

        # 初始化连接池
        self._init_pool(pool_size)
        self._initialized = True

        logger.info(f"DatabaseManager 初始化完成，连接池大小: {pool_size}")

    def _init_pool(self, pool_size: int):
        """初始化连接池"""
        with self._pool_lock:
            if self._pool is not None:
                self._pool.close_all()
            self._pool = ConnectionPool(
                connection_string=self._connection_string,
                pool_size=pool_size,
                max_retries=3,
                timeout_seconds=self.db_config.get('timeout', 30)
            )

    def connect(self) -> pyodbc.Connection:
        """获取数据库连接（从池中获取）"""
        if self._pool is None:
            # 降级为直接连接
            return pyodbc.connect(self._connection_string, timeout=30)
        return self._pool.get_connection()

    def close(self, conn: pyodbc.Connection):
        """关闭连接（归还到池中）"""
        if self._pool is not None:
            self._pool.release_connection(conn)
        else:
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def get_connection(self):
        """上下文管理器方式的连接获取"""
        conn = self.connect()
        try:
            yield conn
        finally:
            self.close(conn)

    def test_connection(self) -> Tuple[bool, str]:
        """测试数据库连接"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            self.close(conn)
            logger.info("数据库连接测试成功")
            return True, "连接成功"
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False, str(e)

    def execute_query(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        fetch: bool = True
    ) -> List[Dict]:
        """执行查询SQL"""
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

                    # 标准化日期类型
                    if isinstance(value, datetime):
                        value = value  # 保留 datetime 对象
                    elif value is None:
                        value = None

                    row_dict[col] = value
                result.append(row_dict)

            logger.info(f"查询成功，返回 {len(result)} 条记录")
            return result

        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            logger.error(f"SQL: {sql}")
            raise
        finally:
            if conn:
                self.close(conn)

    # ========================================
    # 优化后的数据采集方法
    # ========================================

    def get_tool_basic_info(self) -> List[Dict]:
        """
        获取工装基本信息（简化版 - 仅从工装身份卡_主表获取）

        从主表获取:
        - 工装基本信息
        - 定检周期、属性、有效期
        - 派工状态
        """
        sql = """
            SELECT
                -- 工装基本信息
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
            FROM 工装身份卡_主表 m
            WHERE m.定检有效截止 IS NOT NULL
              AND (m.定检属性 IS NULL OR m.定检属性 <> '否')
              AND (m.应用历史 IS NULL OR m.应用历史 NOT LIKE '%封存%')
        """

        results = self.execute_query(sql)

        tools = []
        now = datetime.now()

        for row in results:
            # 标准化日期
            deadline_date = _normalize_date(row.get('定检有效截止'))

            # 计算剩余天数
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
                'manufacture_date': _format_date(row.get('制造日期')),
                'cycle': row.get('定检周期', ''),
                'attribute': row.get('定检属性', ''),
                'deadline': _format_date(row.get('定检有效截止')),
                'deadline_date': deadline_date,
                'dispatch_status': row.get('定检派工状态', ''),
                'remaining_days': remaining_days,
                'application_history': row.get('应用历史', ''),
                # 使用主表的有效期作为实际截止日期
                'effective_deadline_date': deadline_date,
                'effective_remaining_days': remaining_days
            }
            tools.append(tool)

        return tools

    def get_dispatch_info(self) -> List[Dict]:
        """获取派工信息"""
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

        dispatches = []
        for row in results:
            dispatches.append({
                'serial_no': row.get('序列号', ''),
                'drawing_no': row.get('工装图号', ''),
                'dispatch_no': row.get('派工号', ''),
                'apply_date': _normalize_date(row.get('申请工装定检日期')),
                'complete_person': row.get('完成人', ''),
                'complete_date': _normalize_date(row.get('完成日期')),
                'applicant_confirm': row.get('申请人确认', ''),
                'tpitr': row.get('TPITR', ''),
                'tool_version': row.get('工装版次', ''),
                'component_count': row.get('涉及分体组件数量', ''),
                'dispatch_date': _normalize_date(row.get('派工日期'))
            })
        return dispatches

    def get_all_tpitr_info(self) -> List[Dict]:
        """获取所有技术要求信息"""
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

        tpitrs = []
        for row in results:
            tpitrs.append({
                'drawing_no': row.get('工装图号', ''),
                'version': row.get('版次', ''),
                'author': row.get('编制', ''),
                'author_date': _normalize_date(row.get('编制日期')),
                'checker': row.get('校对人', ''),
                'check_date': _normalize_date(row.get('校对日期')),
                'check_conclusion': row.get('校对结论', ''),
                'approver': row.get('批准人', ''),
                'approve_date': _normalize_date(row.get('批准日期')),
                'approve_conclusion': row.get('批准结论', ''),
                'signer': row.get('会签人', ''),
                'sign_date': _normalize_date(row.get('质量会签日期')),
                'sign_conclusion': row.get('会签结论', ''),
                'valid_status': row.get('有效状态', ''),
                'tpitr_no': row.get('编号No', ''),
                'check_comment': row.get('校对意见', ''),
                'approve_comment': row.get('批准意见', ''),
                'sign_comment': row.get('会签意见', '')
            })
        return tpitrs

    def get_acceptance_info(self) -> List[Dict]:
        """获取验收信息"""
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
            logger.warning(f"获取验收信息失败（表可能不存在）: {str(e)}")
            return []

        acceptances = []
        for row in results:
            acceptances.append({
                'dispatch_no': str(row.get('派工号', '')) if row.get('派工号') else '',
                'table_no': str(row.get('表编号', '')) if row.get('表编号') else '',
                'serial_no': str(row.get('序列号', '')) if row.get('序列号') else '',
                'acceptance_status': str(row.get('验收状态', '')) if row.get('验收状态') else '待检查',
                'inspector_check_date': _normalize_date(row.get('计划员检查完成日期')),
                'keeper_org_date': _normalize_date(row.get('保管员组织验收日期')),
                'qc_acceptance_date': _normalize_date(row.get('质检验收日期')),
                'process_acceptance_date': _normalize_date(row.get('工艺验收日期')),
                'acceptance_complete_date': _normalize_date(row.get('验收完成日期')),
                'keeper': str(row.get('保管员', '')) if row.get('保管员') else '',
                'acceptance_note': str(row.get('联合验收说明', '')) if row.get('联合验收说明') else '',
                'notice_no': str(row.get('最新通知单号', '')) if row.get('最新通知单号') else '',
                'remarks': str(row.get('备注', '')) if row.get('备注') else '',
                'create_time': _normalize_date(row.get('创建时间')),
                'modify_time': _normalize_date(row.get('修改时间'))
            })
        return acceptances

    def get_nonconforming_notices(self) -> List[Dict]:
        """获取不合格工装通知单"""
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

            notices = []
            for row in results:
                notices.append({
                    'notice_no': str(row.get('通知单号', '')),
                    'dispatch_no': str(row.get('关联派工号', '')),
                    'table_no': str(row.get('关联表编号', '')),
                    'serial_no': str(row.get('序列号', '')),
                    'inspector': str(row.get('检验员', '')),
                    'creator': str(row.get('编制人', '')),
                    'create_date': _normalize_date(row.get('编制日期')),
                    'process_status': str(row.get('处理状态', '待处理')),
                    'recheck_date': _normalize_date(row.get('复检日期')),
                    'recheck_conclusion': str(row.get('复检结论', '')),
                    'rechecker': str(row.get('复检人', '')),
                    'close_date': _normalize_date(row.get('关闭日期')),
                    'closer': str(row.get('关闭人', '')),
                    'close_note': str(row.get('关闭说明', '')),
                    'create_time': _normalize_date(row.get('创建时间'))
                })
            return notices
        except Exception as e:
            logger.warning(f"获取不合格通知单失败: {str(e)}")
            return []

    def get_inspection_records(self) -> List[Dict]:
        """获取工装定检记录"""
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
            logger.warning(f"获取工装定检记录失败: {str(e)}")
            return []

    def get_repair_records(self) -> List[Dict]:
        """获取工装返修记录"""
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
            logger.warning(f"获取工装返修记录失败: {str(e)}")
            return []

    def get_new_rework_applications(self) -> List[Dict]:
        """获取未同步的返工申请单"""
        sql = """
            SELECT r.OA申请单编号, r.派工号, r.序列号, r.工装图号, r.工装名称,
                   r.返工类型, r.目标版次, r.返工内容, r.需求日期, r.转录人, r.转录日期,
                   r.验收日期, r.验收人员, r.工装计划员, r.计划确认日期, t.当前版次 as 身份卡版次
            FROM 工艺装备返工申请单_主表 r
            LEFT JOIN 工装身份卡_主表 t ON r.序列号 = t.序列号
            WHERE r.OA申请单编号 IS NOT NULL
              AND r.派工号 NOT LIKE 'C%'
              AND NOT EXISTS (SELECT 1 FROM 工装验收管理_主表 m WHERE m.派工号 = r.派工号)
              AND (r.子项类型 = '外协返修' OR r.返工类型 = '升版返修')
            ORDER BY r.转录日期 DESC
        """
        results = self.execute_query(sql)
        return self._parse_application_results(results, '返工')

    def get_new_tooling_applications(self) -> List[Dict]:
        """获取未同步的新制申请单"""
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
        """解析申请单结果"""
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
                'required_date': _normalize_date(row.get('需求日期')),
                'transcriber': row.get('转录人') or row.get('转录人员', ''),
                'transcribe_date': _normalize_date(row.get('转录日期')),
                'acceptance_date': _normalize_date(row.get('验收日期')),
                'acceptor': row.get('验收人员', ''),
                'planner': row.get('工装计划员', ''),
                'confirm_date': _normalize_date(row.get('计划确认日期')),
                'card_version': row.get('身份卡版次', ''),
                'version': row.get('版次', ''),
                'project_code': row.get('项目代号', ''),
                'work_package': row.get('工作包', ''),
                'manufacture_basis': row.get('制造依据', ''),
                'tech_requirement': row.get('技术要求', ''),
                'expected_use_date': _normalize_date(row.get('预计使用时间')),
                'application_type': app_type
            })
        return apps


# ========================================
# 预警规则相关的数据处理
# ========================================

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
        db = DatabaseManager()
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
        logger.error(f"获取监控统计失败: {str(e)}")
        return {'expiry': 0, 'expiry_expired': 0, 'expiry_upcoming': 0, 'total': 0}


# ========================================
# 便捷函数
# ========================================

def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return DatabaseManager()


def test_db_connection() -> Tuple[bool, str]:
    """测试数据库连接"""
    return DatabaseManager().test_connection()


# 全局数据库管理器实例
db_manager = DatabaseManager()


# ========================================
# 验收管理相关函数
# ========================================

def sync_applications_to_acceptance() -> Dict:
    """从申请单同步数据到验收管理表"""
    try:
        db = DatabaseManager()
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
                logger.warning(f"同步申请单失败: {dispatch_no}, {str(e)}")

        return {'success': True, 'synced': synced_count}
    except Exception as e:
        logger.error(f"同步申请单失败: {str(e)}")
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
        db = DatabaseManager()
        db.execute_query(sql, (dispatch_no, serial_no, drawing_no, tool_name), fetch=False)
        return {'success': True}
    except Exception as e:
        logger.error(f"添加验收记录失败: {str(e)}")
        return {'success': False, 'error': str(e)}


def update_acceptance_status(dispatch_no: str, status: str, **kwargs) -> Dict:
    """更新验收状态"""
    try:
        sql = """
            UPDATE 工装验收管理_主表
            SET 验收状态 = ?, 修改时间 = GETDATE()
            WHERE 派工号 = ?
        """
        db = DatabaseManager()
        db.execute_query(sql, (status, dispatch_no), fetch=False)
        return {'success': True}
    except Exception as e:
        logger.error(f"更新验收状态失败: {str(e)}")
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
        db = DatabaseManager()
        if table_no:
            db.execute_query(sql, (dispatch_no, table_no, serial_no, drawing_no,
                                   tool_name, dispatch_no), fetch=False)
        else:
            db.execute_query(sql, (dispatch_no, dispatch_no, serial_no, drawing_no,
                                   tool_name, dispatch_no), fetch=False)
        return {'success': True}
    except Exception as e:
        logger.error(f"保存验收账目失败: {str(e)}")
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
            results = DatabaseManager().execute_query(sql, (inspector,))
        else:
            results = DatabaseManager().execute_query(sql)

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
        logger.error(f"获取检验员验收任务失败: {str(e)}")
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
        DatabaseManager().execute_query(sql, (dispatch_no,), fetch=False)
        return {'success': True}
    except Exception as e:
        logger.error(f"开始检验失败: {str(e)}")
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
        DatabaseManager().execute_query(sql, (status, dispatch_no), fetch=False)
        return {'success': True}
    except Exception as e:
        logger.error(f"提交检验结果失败: {str(e)}")
        return {'success': False, 'error': str(e)}


# ========================================
# API 端点需要的函数
# ========================================

def get_expiry_detail() -> List[Dict]:
    """获取定检到期预警详细数据"""
    try:
        tools = DatabaseManager().get_tool_basic_info()
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
        logger.error(f"获取定检到期详细数据失败: {str(e)}")
        return []


def get_dispatch_detail() -> List[Dict]:
    """获取派工进度详细数据"""
    try:
        dispatches = DatabaseManager().get_dispatch_info()
        return dispatches
    except Exception as e:
        logger.error(f"获取派工进度详细数据失败: {str(e)}")
        return []


def get_tpitr_status() -> Dict:
    """获取TPITR状态统计"""
    try:
        tpitrs = DatabaseManager().get_all_tpitr_info()
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
        logger.error(f"获取TPITR状态失败: {str(e)}")
        return {'total': 0, 'published': 0, 'pending': 0, 'details': []}


def get_acceptance_detail() -> List[Dict]:
    """获取验收状态明细"""
    try:
        return DatabaseManager().get_acceptance_info()
    except Exception as e:
        logger.error(f"获取验收状态明细失败: {str(e)}")
        return []


def get_tpitr_categories() -> Dict:
    """获取TPITR三分类数据"""
    try:
        db = DatabaseManager()
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
        logger.error(f"获取TPITR分类数据失败: {str(e)}")
        return {'has_tpitr_count': 0, 'in_use_count': 0, 'low_priority_count': 0, 'categories': {}}


def get_expired_tpitr_status() -> Dict:
    """获取超期工装TPITR状态"""
    try:
        db = DatabaseManager()
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
        logger.error(f"获取超期工装TPITR状态失败: {str(e)}")
        return {'total_expired': 0, 'has_tpitr': 0, 'missing_tpitr': 0, 'expired_tools': []}


def get_overdue_dispatch_status() -> Dict:
    """获取超期未完成派工数据"""
    try:
        db = DatabaseManager()
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
        logger.error(f"获取超期派工状态失败: {str(e)}")
        return {'total_overdue': 0, 'no_dispatch': 0, 'dispatched': 0, 'overdue_tools': []}


# ========================================
# 工装出入库管理模块 (Tool IO Management)
# ========================================

# 状态枚举
class ToolIOStatus:
    # 单据状态
    DRAFT = "draft"
    SUBMITTED = "submitted"
    KEEPER_CONFIRMED = "keeper_confirmed"
    PARTIALLY_CONFIRMED = "partially_confirmed"
    TRANSPORT_NOTIFIED = "transport_notified"
    FINAL_CONFIRMATION_PENDING = "final_confirmation_pending"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

    # 工装状态
    TOOL_PENDING = "pending_check"
    TOOL_APPROVED = "approved"
    TOOL_REJECTED = "rejected"
    TOOL_TRANSPORT_NOTIFIED = "transport_notified"
    TOOL_COMPLETED = "completed"

    # 工装实例状态
    TOOL_IN_STOCK = "in_stock"
    TOOL_RESERVED = "reserved"
    TOOL_OUTBOUND_PENDING = "outbound_pending"
    TOOL_IN_USE = "in_use"
    TOOL_INBOUND_PENDING = "inbound_pending"
    TOOL_REPAIR = "repair"
    TOOL_SCRAPPED = "scrapped"


# 操作类型
class ToolIOAction:
    CREATE = "创建"
    SUBMIT = "提交"
    CONFIRM = "确认"
    KEEPER_CONFIRM = "保管员确认"
    REJECT = "驳回"
    CANCEL = "取消"
    COMPLETE = "完成"
    NOTIFY = "通知"
    MODIFY = "修改"


def ensure_tool_io_tables():
    """确保出入库相关表存在（自动建表）"""
    db = DatabaseManager()

    # 出入库单主表
    create_order_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='工装出入库单_主表' AND xtype='U')
    CREATE TABLE 工装出入库单_主表 (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        出入库单号 VARCHAR(64) UNIQUE NOT NULL,
        单据类型 VARCHAR(16) NOT NULL,
        单据状态 VARCHAR(32) NOT NULL DEFAULT 'draft',
        发起人ID VARCHAR(64) NOT NULL,
        发起人姓名 VARCHAR(64) NOT NULL,
        发起人角色 VARCHAR(32) NOT NULL,
        部门 VARCHAR(64),
        项目代号 VARCHAR(64),
        用途 VARCHAR(255),
        计划使用时间 DATETIME,
        计划归还时间 DATETIME,
        目标位置ID BIGINT,
        目标位置文本 VARCHAR(255),
        保管员ID VARCHAR(64),
        保管员姓名 VARCHAR(64),
        运输类型 VARCHAR(32),
        运输人ID VARCHAR(64),
        运输人姓名 VARCHAR(64),
        保管员需求文本 TEXT,
        运输通知文本 TEXT,
        微信复制文本 TEXT,
        保管员确认时间 DATETIME,
        运输通知时间 DATETIME,
        最终确认时间 DATETIME,
        工装数量 INT,
        已确认数量 INT,
        最终确认人 VARCHAR(64),
        驳回原因 VARCHAR(500),
        取消原因 VARCHAR(500),
        备注 VARCHAR(500),
        创建时间 DATETIME DEFAULT GETDATE(),
        修改时间 DATETIME DEFAULT GETDATE(),
        创建人 VARCHAR(64),
        修改人 VARCHAR(64),
        IS_DELETED TINYINT DEFAULT 0
    )
    """

    # 出入库单明细表
    create_item_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='工装出入库单_明细' AND xtype='U')
    CREATE TABLE 工装出入库单_明细 (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        出入库单号 VARCHAR(64) NOT NULL,
        工装ID BIGINT,
        工装编码 VARCHAR(64) NOT NULL,
        工装名称 VARCHAR(128) NOT NULL,
        工装图号 VARCHAR(64),
        规格型号 VARCHAR(128),
        申请数量 DECIMAL(10,2) DEFAULT 1,
        确认数量 DECIMAL(10,2),
        明细状态 VARCHAR(32) NOT NULL DEFAULT 'pending_check',
        工装快照状态 VARCHAR(32),
        工装快照位置ID BIGINT,
        工装快照位置文本 VARCHAR(255),
        保管员确认位置ID BIGINT,
        保管员确认位置文本 VARCHAR(255),
        保管员检查结果 VARCHAR(32),
        保管员检查备注 VARCHAR(500),
        归还检查结果 VARCHAR(32),
        归还检查备注 VARCHAR(500),
        确认时间 DATETIME,
        出入库完成时间 DATETIME,
        排序号 INT,
        创建时间 DATETIME DEFAULT GETDATE(),
        修改时间 DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_明细_主表 FOREIGN KEY (出入库单号)
            REFERENCES 工装出入库单_主表(出入库单号)
    )
    """

    # 操作日志表
    create_log_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='工装出入库单_操作日志' AND xtype='U')
    CREATE TABLE 工装出入库单_操作日志 (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        出入库单号 VARCHAR(64) NOT NULL,
        明细ID BIGINT,
        操作类型 VARCHAR(64) NOT NULL,
        操作人ID VARCHAR(64) NOT NULL,
        操作人姓名 VARCHAR(64) NOT NULL,
        操作人角色 VARCHAR(32),
        变更前状态 VARCHAR(32),
        变更后状态 VARCHAR(32),
        操作内容 TEXT,
        操作时间 DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_日志_主表 FOREIGN KEY (出入库单号)
            REFERENCES 工装出入库单_主表(出入库单号)
    )
    """

    # 通知记录表
    create_notify_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='工装出入库单_通知记录' AND xtype='U')
    CREATE TABLE 工装出入库单_通知记录 (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        出入库单号 VARCHAR(64) NOT NULL,
        通知类型 VARCHAR(32) NOT NULL,
        通知渠道 VARCHAR(32) NOT NULL,
        接收人 VARCHAR(255),
        通知标题 VARCHAR(100),
        通知内容 TEXT NOT NULL,
        复制文本 TEXT,
        发送状态 VARCHAR(32) NOT NULL DEFAULT 'pending',
        发送时间 DATETIME,
        发送结果 TEXT,
        重试次数 INT DEFAULT 0,
        创建时间 DATETIME DEFAULT GETDATE(),
        CONSTRAINT FK_通知_主表 FOREIGN KEY (出入库单号)
            REFERENCES 工装出入库单_主表(出入库单号)
    )
    """

    # 位置表（如果不存在）
    create_location_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='工装位置表' AND xtype='U')
    CREATE TABLE 工装位置表 (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        位置编码 VARCHAR(64) UNIQUE NOT NULL,
        位置名称 VARCHAR(128) NOT NULL,
        仓库区域 VARCHAR(64),
        货架号 VARCHAR(64),
        槽位号 VARCHAR(64),
        完整路径 VARCHAR(255),
        备注 VARCHAR(500)
    )
    """

    create_order_no_sequence_table_sql = f"""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{ORDER_NO_SEQUENCE_TABLE}' AND xtype='U')
    CREATE TABLE {ORDER_NO_SEQUENCE_TABLE} (
        sequence_key VARCHAR(32) PRIMARY KEY,
        current_value INT NOT NULL,
        updated_at DATETIME NOT NULL DEFAULT GETDATE()
    )
    """

    try:
        for sql in [create_order_table_sql, create_item_table_sql,
                    create_log_table_sql, create_notify_table_sql, create_location_table_sql,
                    create_order_no_sequence_table_sql]:
            db.execute_query(sql, fetch=False)
        for sql in _build_schema_alignment_sql():
            db.execute_query(sql, fetch=False)
        logger.info("工装出入库相关表初始化完成")
        return True
    except Exception as e:
        logger.error(f"初始化出入库表失败: {e}")
        return False


def generate_order_no_atomic(order_type: str) -> str:
    """Allocate an order number with a database-backed counter."""
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
            if not _is_duplicate_key_error(exc):
                raise

    raise RuntimeError("failed to allocate order number")


def create_tool_io_order(order_data: dict) -> dict:
    """创建出入库单（草稿状态）"""
    try:
        db = DatabaseManager()
        order_no = generate_order_no_atomic(order_data.get('order_type', 'outbound'))

        sql = """
        INSERT INTO 工装出入库单_主表 (
            出入库单号, 单据类型, 单据状态,
            发起人ID, 发起人姓名, 发起人角色,
            部门, 项目代号, 用途, 计划使用时间, 计划归还时间,
            目标位置ID, 目标位置文本, 备注,
            创建时间, 修改时间
        ) VALUES (?, ?, 'draft', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
        """

        db.execute_query(sql, (
            order_no,
            order_data.get('order_type'),
            order_data.get('initiator_id'),
            order_data.get('initiator_name'),
            order_data.get('initiator_role'),
            order_data.get('department'),
            order_data.get('project_code'),
            order_data.get('usage_purpose'),
            order_data.get('planned_use_time'),
            order_data.get('planned_return_time'),
            order_data.get('target_location_id'),
            order_data.get('target_location_text'),
            order_data.get('remark')
        ), fetch=False)

        # 插入明细
        items = order_data.get('items', [])
        for idx, item in enumerate(items):
            item_sql = """
            INSERT INTO 工装出入库单_明细 (
                出入库单号, 工装ID, 工装编码, 工装名称, 工装图号, 规格型号,
                申请数量, 明细状态, 排序号, 创建时间, 修改时间
            ) VALUES (?, ?, ?, ?, ?, ?, 1, 'pending_check', ?, GETDATE(), GETDATE())
            """
            db.execute_query(item_sql, (
                order_no,
                item.get('tool_id'),
                item.get('tool_code'),
                item.get('tool_name'),
                item.get('drawing_no'),
                item.get('spec_model'),
                idx + 1
            ), fetch=False)

        # 更新主表工装数量
        update_sql = """
        UPDATE 工装出入库单_主表 SET 工装数量 = ? WHERE 出入库单号 = ?
        """
        db.execute_query(update_sql, (len(items), order_no), fetch=False)

        # 记录日志
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.CREATE,
            'operator_id': order_data.get('initiator_id'),
            'operator_name': order_data.get('initiator_name'),
            'operator_role': order_data.get('initiator_role'),
            'before_status': '',
            'after_status': 'draft',
            'content': f"创建出入库单，单号：{order_no}"
        })

        return {'success': True, 'order_no': order_no}
    except Exception as e:
        logger.error(f"创建出入库单失败: {e}")
        return {'success': False, 'error': str(e)}


def submit_tool_io_order(order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
    """提交出入库单"""
    try:
        db = DatabaseManager()

        # 检查单据状态
        check_sql = "SELECT 单据状态 FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '单据不存在'}

        current_status = result[0].get('单据状态')
        if current_status != 'draft':
            return {'success': False, 'error': f'当前状态不允许提交，当前状态：{current_status}'}

        # 更新状态为已提交
        sql = """
        UPDATE 工装出入库单_主表
        SET 单据状态 = 'submitted', 修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """
        db.execute_query(sql, (order_no,), fetch=False)

        # 记录日志
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.SUBMIT,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': 'draft',
            'after_status': 'submitted',
            'content': '提交单据，等待保管员确认'
        })

        return {'success': True}
    except Exception as e:
        logger.error(f"提交出入库单失败: {e}")
        return {'success': False, 'error': str(e)}


def _safe_bigint(value: Any) -> Optional[int]:
    """Return a BIGINT-safe integer value when possible."""
    if value in (None, ""):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _load_tool_master_map(tool_codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """Load tool master rows from 工装身份卡_主表 keyed by 序列号."""
    cleaned_codes = [str(code).strip() for code in tool_codes if str(code).strip()]
    if not cleaned_codes:
        return {}

    placeholders = ",".join(["?"] * len(cleaned_codes))
    sql = f"""
    SELECT
        [序列号] AS tool_code,
        [工装名称] AS tool_name,
        [工装图号] AS drawing_no,
        [机型] AS spec_model,
        [库位] AS current_location_text,
        [当前版次] AS current_version,
        COALESCE([出入库状态], [可用状态], [工装有效状态], '') AS status_text
    FROM [工装身份卡_主表]
    WHERE [序列号] IN ({placeholders})
    """
    rows = DatabaseManager().execute_query(sql, tuple(cleaned_codes))
    return {str(row.get("tool_code", "")).strip(): row for row in rows}


def create_tool_io_order(order_data: dict) -> dict:
    """Create a tool IO order using the actual runtime schema."""
    try:
        db = DatabaseManager()
        items = order_data.get("items")
        if not isinstance(items, list) or not items:
            return {"success": False, "error": "items must contain at least one selected tool"}

        order_type = order_data.get("order_type")
        if order_type not in {"outbound", "inbound"}:
            return {"success": False, "error": "order_type must be outbound or inbound"}

        tool_codes = [str(item.get("tool_code", "")).strip() for item in items if str(item.get("tool_code", "")).strip()]
        if len(tool_codes) != len(items):
            return {"success": False, "error": "every item must include tool_code"}
        if len(set(tool_codes)) != len(tool_codes):
            return {"success": False, "error": "tool_code values must be unique within one order"}

        tool_master_map = _load_tool_master_map(tool_codes)
        missing_codes = [code for code in tool_codes if code not in tool_master_map]
        if missing_codes:
            return {"success": False, "error": f"selected tools not found: {', '.join(missing_codes)}"}

        order_no = generate_order_no_atomic(order_type)
        insert_order_sql = """
        INSERT INTO [工装出入库单_主表] (
            [出入库单号], [单据类型], [单据状态], [发起人ID], [发起人姓名], [发起人角色],
            [部门], [项目代号], [用途], [计划使用时间], [计划归还时间],
            [目标位置ID], [目标位置文本], [备注], [工装数量], [已确认数量],
            [创建时间], [修改时间], [创建人], [修改人], [IS_DELETED]
        ) VALUES (?, ?, 'draft', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), ?, ?, 0)
        """
        db.execute_query(
            insert_order_sql,
            (
                order_no,
                order_type,
                order_data.get("initiator_id"),
                order_data.get("initiator_name"),
                order_data.get("initiator_role"),
                order_data.get("department"),
                order_data.get("project_code"),
                order_data.get("usage_purpose"),
                order_data.get("planned_use_time"),
                order_data.get("planned_return_time"),
                order_data.get("target_location_id"),
                order_data.get("target_location_text"),
                order_data.get("remark"),
                len(items),
                0,
                order_data.get("initiator_name"),
                order_data.get("initiator_name"),
            ),
            fetch=False,
        )

        insert_item_sql = """
        INSERT INTO [工装出入库单_明细] (
            [出入库单号], [工装ID], [工装编码], [工装名称], [工装图号], [规格型号],
            [申请数量], [确认数量], [明细状态], [工装快照状态], [工装快照位置文本],
            [排序号], [创建时间], [修改时间]
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending_check', ?, ?, ?, GETDATE(), GETDATE())
        """
        for idx, item in enumerate(items, start=1):
            tool_code = str(item.get("tool_code", "")).strip()
            tool_row = tool_master_map[tool_code]
            db.execute_query(
                insert_item_sql,
                (
                    order_no,
                    _safe_bigint(item.get("tool_id")),
                    tool_code,
                    item.get("tool_name") or tool_row.get("tool_name"),
                    item.get("drawing_no") or tool_row.get("drawing_no"),
                    item.get("spec_model") or tool_row.get("spec_model"),
                    item.get("apply_qty") or 1,
                    0,
                    tool_row.get("status_text"),
                    tool_row.get("current_location_text"),
                    idx,
                ),
                fetch=False,
            )

        add_tool_io_log(
            {
                "order_no": order_no,
                "action_type": ToolIOAction.CREATE,
                "operator_id": order_data.get("initiator_id"),
                "operator_name": order_data.get("initiator_name"),
                "operator_role": order_data.get("initiator_role"),
                "before_status": "",
                "after_status": "draft",
                "content": f"创建出入库单，单号：{order_no}",
            }
        )
        return {"success": True, "order_no": order_no}
    except Exception as e:
        logger.error(f"创建出入库单失败: {e}")
        return {"success": False, "error": str(e)}


def submit_tool_io_order(order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
    """Submit a draft order using the actual runtime schema."""
    try:
        db = DatabaseManager()
        check_sql = """
        SELECT [单据状态]
        FROM [工装出入库单_主表]
        WHERE [出入库单号] = ? AND [IS_DELETED] = 0
        """
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {"success": False, "error": "order not found"}

        current_status = result[0].get("单据状态")
        if current_status != "draft":
            return {"success": False, "error": f"current status does not allow submit: {current_status}"}

        detail_rows = db.execute_query(
            "SELECT COUNT(*) AS total FROM [工装出入库单_明细] WHERE [出入库单号] = ?",
            (order_no,),
        )
        if not detail_rows or int(detail_rows[0].get("total", 0)) <= 0:
            return {"success": False, "error": "order has no tool items"}

        update_sql = """
        UPDATE [工装出入库单_主表]
        SET [单据状态] = 'submitted',
            [修改时间] = GETDATE(),
            [修改人] = ?
        WHERE [出入库单号] = ?
        """
        db.execute_query(update_sql, (operator_name, order_no), fetch=False)

        add_tool_io_log(
            {
                "order_no": order_no,
                "action_type": ToolIOAction.SUBMIT,
                "operator_id": operator_id,
                "operator_name": operator_name,
                "operator_role": operator_role,
                "before_status": "draft",
                "after_status": "submitted",
                "content": "提交单据，等待保管员确认",
            }
        )
        return {"success": True, "order_no": order_no, "status": "submitted"}
    except Exception as e:
        logger.error(f"提交出入库单失败: {e}")
        return {"success": False, "error": str(e)}


def get_tool_io_order(order_no: str) -> dict:
    """获取出入库单详情"""
    try:
        db = DatabaseManager()

        # 获取主表
        sql = "SELECT * FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
        result = db.execute_query(sql, (order_no,))
        if not result:
            return {}

        order = result[0]

        # 获取明细
        items_sql = "SELECT * FROM 工装出入库单_明细 WHERE 出入库单号 = ? ORDER BY 排序号"
        items = db.execute_query(items_sql, (order_no,))
        order['items'] = items

        return order
    except Exception as e:
        logger.error(f"获取出入库单详情失败: {e}")
        return {}


def get_tool_io_orders(
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
    """查询出入库单列表"""
    try:
        db = DatabaseManager()

        conditions = ["IS_DELETED = 0"]
        params = []

        if order_type:
            conditions.append("单据类型 = ?")
            params.append(order_type)
        if order_status:
            conditions.append("单据状态 = ?")
            params.append(order_status)
        if initiator_id:
            conditions.append("发起人ID = ?")
            params.append(initiator_id)
        if keeper_id:
            conditions.append("保管员ID = ?")
            params.append(keeper_id)
        if keyword:
            conditions.append("(出入库单号 LIKE ? OR 项目代号 LIKE ? OR 用途 LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        if date_from:
            conditions.append("创建时间 >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("创建时间 <= ?")
            params.append(date_to)

        where_clause = " AND ".join(conditions)

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM 工装出入库单_主表 WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(params))
        total = count_result[0].get('total', 0) if count_result else 0

        # Use a single filtered query for pagination so placeholder counts stay aligned
        # even when optional filters are present.
        offset = (page_no - 1) * page_size
        list_sql = f"""
        SELECT * FROM 工装出入库单_主表
        WHERE {where_clause}
        ORDER BY 创建时间 DESC
        OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
        """

        rows = db.execute_query(list_sql, tuple(params))

        return {
            'success': True,
            'data': rows,
            'total': total,
            'page_no': page_no,
            'page_size': page_size
        }
    except Exception as e:
        logger.error(f"查询出入库单列表失败: {e}")
        return {'success': False, 'error': str(e), 'data': [], 'total': 0}


def search_tools(
    keyword: str = None,
    status: str = None,
    location_id: int = None,
    page_no: int = 1,
    page_size: int = 20
) -> dict:
    """搜索工装（支持批量选择）"""
    try:
        db = DatabaseManager()

        # 从现有工装身份卡表查询
        conditions = ["(定检属性 IS NULL OR 定检属性 <> '否')"]
        params = []

        if keyword:
            conditions.append("""
                (序列号 LIKE ? OR 工装图号 LIKE ? OR 工装名称 LIKE ?
                OR 规格型号 LIKE ? OR 当前版次 LIKE ?)
            """)
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, kw, kw])

        where_clause = " AND ".join(conditions)

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM 工装身份卡_主表 WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(params))
        total = count_result[0].get('total', 0) if count_result else 0

        # 查询列表
        offset = (page_no - 1) * page_size
        list_sql = f"""
        SELECT
            序列号 as tool_code,
            工装图号 as drawing_no,
            工装名称 as tool_name,
            规格型号 as spec_model,
            当前版次 as version,
            定检属性 as category,
            定检有效截止 as expiry_date,
            应用历史 as location_info
        FROM 工装身份卡_主表
        WHERE {where_clause}
        ORDER BY 序列号
        OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
        """

        rows = db.execute_query(list_sql, tuple(params))

        return {
            'success': True,
            'data': rows,
            'total': total,
            'page_no': page_no,
            'page_size': page_size
        }
    except Exception as e:
        logger.error(f"搜索工装失败: {e}")
        return {'success': False, 'error': str(e), 'data': [], 'total': 0}


def search_tools(
    keyword: str = None,
    status: str = None,
    location_id: int = None,
    page_no: int = 1,
    page_size: int = 20
) -> dict:
    """Search tool master data from 工装身份卡_主表."""
    try:
        db = DatabaseManager()
        conditions = ["[序列号] IS NOT NULL", "LTRIM(RTRIM([序列号])) <> ''"]
        params = []

        if keyword:
            keyword_like = f"%{keyword.strip()}%"
            conditions.append(
                """
                (
                    [序列号] LIKE ?
                    OR [工装名称] LIKE ?
                    OR [工装图号] LIKE ?
                    OR [机型] LIKE ?
                    OR [库位] LIKE ?
                    OR [当前版次] LIKE ?
                    OR [应用历史] LIKE ?
                    OR [工作包] LIKE ?
                    OR [主体材质] LIKE ?
                    OR [制造商] LIKE ?
                )
                """
            )
            params.extend([keyword_like] * 10)

        if status:
            status_like = f"%{status.strip()}%"
            conditions.append(
                """
                (
                    [可用状态] LIKE ?
                    OR [工装有效状态] LIKE ?
                    OR [出入库状态] LIKE ?
                )
                """
            )
            params.extend([status_like, status_like, status_like])

        if location_id not in (None, ""):
            location_like = f"%{str(location_id).strip()}%"
            conditions.append(
                """
                (
                    [库位] LIKE ?
                    OR [应用历史] LIKE ?
                )
                """
            )
            params.extend([location_like, location_like])

        where_clause = " AND ".join(conditions)
        count_sql = f"SELECT COUNT(*) as total FROM [工装身份卡_主表] WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(params))
        total = count_result[0].get('total', 0) if count_result else 0

        offset = (page_no - 1) * page_size
        list_sql = f"""
        SELECT
            [序列号] as tool_code,
            [序列号] as tool_id,
            [工装名称] as tool_name,
            [工装图号] as drawing_no,
            [机型] as spec_model,
            [机型] as model_code,
            [当前版次] as current_version,
            [库位] as current_location_text,
            [应用历史] as application_history,
            [可用状态] as available_status,
            [工装有效状态] as valid_status,
            [出入库状态] as io_status,
            [产权所有] as owner_name,
            [工作包] as work_package,
            [主体材质] as main_material,
            [制造商] as manufacturer,
            [定检有效截止] as inspection_expiry_date,
            [定检属性] as inspection_category,
            [定检周期] as inspection_cycle,
            COALESCE([出入库状态], [可用状态], [工装有效状态], '') as status_text
        FROM [工装身份卡_主表]
        WHERE {where_clause}
        ORDER BY [序列号]
        OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
        """

        rows = db.execute_query(list_sql, tuple(params))

        return {
            'success': True,
            'data': rows,
            'total': total,
            'page_no': page_no,
            'page_size': page_size
        }
    except Exception as e:
        logger.error(f"搜索工装失败: {e}")
        return {'success': False, 'error': str(e), 'data': [], 'total': 0}


def keeper_confirm_order(
    order_no: str,
    keeper_id: str,
    keeper_name: str,
    confirm_data: dict,
    operator_id: str,
    operator_name: str,
    operator_role: str
) -> dict:
    """保管员确认出入库单"""
    try:
        db = DatabaseManager()

        if not isinstance(confirm_data, dict):
            return {'success': False, 'error': 'confirm_data must be an object'}

        items = confirm_data.get('items')
        if not isinstance(items, list) or not items:
            return {'success': False, 'error': 'confirm_data.items must contain at least one item'}

        # 检查单据状态
        check_sql = "SELECT 单据类型, 单据状态 FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '单据不存在'}

        order_type = result[0].get('单据类型')
        current_status = result[0].get('单据状态')
        if current_status not in ['submitted', 'partially_confirmed']:
            return {'success': False, 'error': f'当前状态不允许确认，当前状态：{current_status}'}

        # 更新明细
        approved_count = 0
        for item in items:
            item_sql = """
            UPDATE 工装出入库单_明细 SET
                保管员确认位置ID = ?,
                保管员确认位置文本 = ?,
                保管员检查结果 = ?,
                保管员检查备注 = ?,
                确认数量 = ?,
                明细状态 = ?,
                确认时间 = GETDATE(),
                修改时间 = GETDATE()
            WHERE 出入库单号 = ? AND 工装编码 = ?
            """
            status = item.get('status', 'approved')
            if status == 'approved':
                approved_count += 1

            db.execute_query(item_sql, (
                item.get('location_id'),
                item.get('location_text'),
                item.get('check_result'),
                item.get('check_remark'),
                item.get('approved_qty', 1),
                status,
                order_no,
                item.get('tool_code')
            ), fetch=False)

        # 更新主表状态
        new_status = 'keeper_confirmed' if approved_count == len(items) else 'partially_confirmed'
        update_sql = """
        UPDATE 工装出入库单_主表 SET
            单据状态 = ?,
            保管员ID = ?,
            保管员姓名 = ?,
            运输类型 = ?,
            运输人ID = ?,
            运输人姓名 = ?,
            保管员确认时间 = GETDATE(),
            已确认数量 = ?,
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """
        db.execute_query(update_sql, (
            new_status,
            keeper_id,
            keeper_name,
            confirm_data.get('transport_type'),
            confirm_data.get('transport_assignee_id'),
            confirm_data.get('transport_assignee_name'),
            approved_count,
            order_no
        ), fetch=False)

        # 记录日志
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.KEEPER_CONFIRM,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': current_status,
            'after_status': new_status,
            'content': f'保管员确认，通过 {approved_count}/{len(items)} 项'
        })

        return {'success': True, 'status': new_status, 'approved_count': approved_count}
    except Exception as e:
        logger.error(f"保管员确认失败: {e}")
        return {'success': False, 'error': str(e)}


def final_confirm_order(
    order_no: str,
    operator_id: str,
    operator_name: str,
    operator_role: str
) -> dict:
    """最终确认完成出入库单"""
    try:
        db = DatabaseManager()

        # 检查单据状态
        check_sql = "SELECT 单据类型, 单据状态 FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '单据不存在'}

        order_type = result[0].get('单据类型')
        current_status = result[0].get('单据状态')

        if current_status not in ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'final_confirmation_pending']:
            return {'success': False, 'error': f'当前状态不允许最终确认，当前状态：{current_status}'}

        # 更新主表状态
        sql = """
        UPDATE 工装出入库单_主表 SET
            单据状态 = 'completed',
            最终确认人 = ?,
            最终确认时间 = GETDATE(),
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """
        db.execute_query(sql, (operator_name, order_no), fetch=False)

        # 更新明细状态
        update_items_sql = """
        UPDATE 工装出入库单_明细 SET
            明细状态 = 'completed',
            出入库完成时间 = GETDATE(),
            修改时间 = GETDATE()
        WHERE 出入库单号 = ? AND 明细状态 = 'approved'
        """
        db.execute_query(update_items_sql, (order_no,), fetch=False)

        # 记录日志
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.COMPLETE,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': current_status,
            'after_status': 'completed',
            'content': f'出入库完成，类型：{order_type}'
        })

        return {'success': True}
    except Exception as e:
        logger.error(f"最终确认失败: {e}")
        return {'success': False, 'error': str(e)}


def reject_tool_io_order(
    order_no: str,
    reject_reason: str,
    operator_id: str,
    operator_name: str,
    operator_role: str
) -> dict:
    """驳回出入库单"""
    try:
        db = DatabaseManager()

        # 检查状态
        check_sql = "SELECT 单据状态 FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '单据不存在'}

        current_status = result[0].get('单据状态')
        if current_status not in ['submitted', 'keeper_confirmed', 'partially_confirmed']:
            return {'success': False, 'error': f'当前状态不允许驳回，当前状态：{current_status}'}

        # 更新状态
        sql = """
        UPDATE 工装出入库单_主表 SET
            单据状态 = 'rejected',
            驳回原因 = ?,
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """
        db.execute_query(sql, (reject_reason, order_no), fetch=False)

        # 更新明细状态
        update_items_sql = """
        UPDATE 工装出入库单_明细 SET
            明细状态 = 'rejected',
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """
        db.execute_query(update_items_sql, (order_no,), fetch=False)

        # 记录日志
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.REJECT,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': current_status,
            'after_status': 'rejected',
            'content': f'驳回原因：{reject_reason}'
        })

        return {'success': True}
    except Exception as e:
        logger.error(f"驳回单据失败: {e}")
        return {'success': False, 'error': str(e)}


def cancel_tool_io_order(
    order_no: str,
    operator_id: str,
    operator_name: str,
    operator_role: str
) -> dict:
    """取消出入库单"""
    try:
        db = DatabaseManager()

        # 检查状态
        check_sql = "SELECT 单据状态 FROM 工装出入库单_主表 WHERE 出入库单号 = ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '单据不存在'}

        current_status = result[0].get('单据状态')
        if current_status in ['completed', 'rejected', 'cancelled']:
            return {'success': False, 'error': f'当前状态不允许取消，当前状态：{current_status}'}

        # 更新状态
        sql = """
        UPDATE 工装出入库单_主表 SET
            单据状态 = 'cancelled',
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """
        db.execute_query(sql, (order_no,), fetch=False)

        # 更新明细状态
        update_items_sql = """
        UPDATE 工装出入库单_明细 SET
            明细状态 = 'rejected',
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """
        db.execute_query(update_items_sql, (order_no,), fetch=False)

        # 记录日志
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.CANCEL,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': current_status,
            'after_status': 'cancelled',
            'content': '单据已取消'
        })

        return {'success': True}
    except Exception as e:
        logger.error(f"取消单据失败: {e}")
        return {'success': False, 'error': str(e)}


def add_tool_io_log(log_data: dict) -> bool:
    """记录操作日志"""
    try:
        db = DatabaseManager()
        sql = """
        INSERT INTO 工装出入库单_操作日志 (
            出入库单号, 明细ID, 操作类型, 操作人ID, 操作人姓名, 操作人角色,
            变更前状态, 变更后状态, 操作内容, 操作时间
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """
        db.execute_query(sql, (
            log_data.get('order_no'),
            log_data.get('item_id'),
            log_data.get('action_type'),
            log_data.get('operator_id'),
            log_data.get('operator_name'),
            log_data.get('operator_role'),
            log_data.get('before_status'),
            log_data.get('after_status'),
            log_data.get('content')
        ), fetch=False)
        return True
    except Exception as e:
        logger.error(f"记录操作日志失败: {e}")
        return False


def get_tool_io_logs(order_no: str) -> list:
    """获取操作日志"""
    try:
        db = DatabaseManager()
        sql = """
        SELECT * FROM 工装出入库单_操作日志
        WHERE 出入库单号 = ?
        ORDER BY 操作时间 DESC
        """
        return db.execute_query(sql, (order_no,))
    except Exception as e:
        logger.error(f"获取操作日志失败: {e}")
        return []


def add_tool_io_notification(notify_data: dict) -> int:
    """Insert a notification record and return its id."""
    conn = None
    cursor = None
    try:
        db = DatabaseManager()
        conn = db.connect()
        cursor = conn.cursor()
        sql = """
        INSERT INTO 工装出入库单_通知记录 (
            出入库单号, 通知类型, 通知渠道, 接收人, 通知标题,
            通知内容, 复制文本, 发送状态, 创建时间
        )
        OUTPUT INSERTED.id AS id
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', GETDATE())
        """
        cursor.execute(sql, (
            notify_data.get('order_no'),
            notify_data.get('notify_type'),
            notify_data.get('notify_channel'),
            notify_data.get('receiver'),
            notify_data.get('title'),
            notify_data.get('content'),
            notify_data.get('copy_text')
        ))
        row = cursor.fetchone()
        conn.commit()
        return int(row[0]) if row else 0
    except Exception as e:
        if conn is not None:
            conn.rollback()
        logger.error(f"add_tool_io_notification failed: {e}")
        return 0
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            db.close(conn)


def update_notification_status(
    notify_id: int,
    status: str,
    send_result: str = None
) -> bool:
    """更新通知状态"""
    try:
        db = DatabaseManager()
        sql = """
        UPDATE 工装出入库单_通知记录 SET
            发送状态 = ?,
            发送时间 = GETDATE(),
            发送结果 = ?
        WHERE id = ?
        """
        db.execute_query(sql, (status, send_result, notify_id), fetch=False)
        return True
    except Exception as e:
        logger.error(f"更新通知状态失败: {e}")
        return False


def get_pending_keeper_orders(keeper_id: str = None) -> list:
    """获取待保管员确认的单据"""
    try:
        db = DatabaseManager()
        sql = """
        SELECT * FROM 工装出入库单_主表
        WHERE 单据状态 IN ('submitted', 'partially_confirmed')
        AND IS_DELETED = 0
        """
        params = []
        if keeper_id:
            sql += " AND (保管员ID = ? OR 保管员ID IS NULL)"
            params.append(keeper_id)
        sql += " ORDER BY 创建时间 DESC"

        return db.execute_query(sql, tuple(params))
    except Exception as e:
        logger.error(f"获取待确认单据失败: {e}")
        return []
