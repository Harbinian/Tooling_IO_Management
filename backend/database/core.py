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
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
