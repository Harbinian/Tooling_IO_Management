# -*- coding: utf-8 -*-
"""
宸ヨ瀹氭鍏ㄦ祦绋嬬洃鎺х郴缁?- 鏁版嵁搴撹繛鎺ユā鍧?
========================================
鍔熻兘: 鎻愪緵鏁版嵁搴撹繛鎺ュ拰鏌ヨ鍔熻兘锛堝惈杩炴帴姹狅級
鐗堟湰: V4.0 (杩炴帴姹?+ 浼樺寲鏌ヨ)
鏃ユ湡: 2025-01-23
========================================

鏀寔:
- 鐜鍙橀噺閰嶇疆 (CESOFT_ 鍓嶇紑)
- 缁熶竴閰嶇疆灞?config.settings
- 鏁版嵁搴撹繛鎺ユ睜
- 杩炴帴澶嶇敤
- 鏃ユ湡绫诲瀷鏍囧噯鍖?

鐜鍙橀噺閰嶇疆:
  CESOFT_DB_SERVER     - 鏁版嵁搴撴湇鍔″櫒鍦板潃 (榛樿: 192.168.19.220,1433)
  CESOFT_DB_DATABASE   - 鏁版嵁搴撳悕绉?(榛樿: CXSYSYS)
  CESOFT_DB_USERNAME   - 鐢ㄦ埛鍚?(榛樿: sa)
  CESOFT_DB_PASSWORD   - 瀵嗙爜
  CESOFT_DB_DRIVER     - ODBC椹卞姩 (榛樿: {SQL Server})
  CESOFT_DB_POOL_SIZE  - 杩炴帴姹犲ぇ灏?(榛樿: 5)
  CESOFT_DB_POOL_TIMEOUT - 杩炴帴瓒呮椂(绉? (榛樿: 30)
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

# 娣诲姞椤圭洰鏍圭洰褰曞埌璺緞
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# 灏濊瘯瀵煎叆缁熶竴閰嶇疆灞?
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
    ("工装出入库单_明细", "IX_工装出入库单_明细_序列号", "序列号"),
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


def _build_rename_column_sql(table_name: str, old_name: str, new_name: str) -> str:
    quoted_table = _quote_sql_string(table_name)
    quoted_old_name = _quote_sql_string(old_name)
    quoted_new_name = _quote_sql_string(new_name)
    return f"""
    IF COL_LENGTH(N'{quoted_table}', N'{quoted_old_name}') IS NOT NULL
       AND COL_LENGTH(N'{quoted_table}', N'{quoted_new_name}') IS NULL
    BEGIN
        EXEC sp_rename N'{quoted_table}.{quoted_old_name}', N'{quoted_new_name}', 'COLUMN'
    END
    """


def _build_schema_alignment_sql() -> List[str]:
    sql_statements = [
        _build_rename_column_sql("工装出入库单_明细", "工装编码", "序列号"),
        _build_rename_column_sql("工装出入库单_明细", "规格型号", "机型"),
        _build_add_column_sql("工装出入库单_主表", "工装数量", "INT NULL"),
        _build_add_column_sql("工装出入库单_主表", "已确认数量", "INT NULL"),
        _build_add_column_sql("工装出入库单_主表", "最终确认人", "VARCHAR(64) NULL"),
        _build_add_column_sql("工装出入库单_主表", "取消原因", "VARCHAR(500) NULL"),
        _build_add_column_sql("工装出入库单_明细", "确认人", "VARCHAR(64) NULL"),
        _build_add_column_sql("工装出入库单_明细", "确认时间", "DATETIME NULL"),
        _build_add_column_sql("工装出入库单_明细", "驳回原因", "VARCHAR(500) NULL"),
        _build_add_column_sql("工装出入库单_明细", "出入库完成时间", "DATETIME NULL"),
    ]

    for table_name, index_name, column_list in SCHEMA_ALIGNMENT_INDEXES:
        sql_statements.append(_build_create_index_sql(table_name, index_name, column_list))

    return sql_statements


# ========================================
# 杩炴帴姹犲疄鐜?
# ========================================

class ConnectionPool:
    """
    鏁版嵁搴撹繛鎺ユ睜

    鐗规€?
    - 棰勫垱寤烘寚瀹氭暟閲忕殑杩炴帴
    - 杩炴帴澶嶇敤锛屽噺灏戝垱寤哄紑閿€
    - 绾跨▼瀹夊叏
    - 杩炴帴鍋ュ悍妫€鏌?
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
        self._check_interval = 60  # 60绉掓鏌ヤ竴娆¤繛鎺ュ仴搴?

    def _create_connection(self) -> Optional[pyodbc.Connection]:
        """鍒涘缓鏂拌繛鎺?"""
        for attempt in range(self.max_retries):
            try:
                conn = pyodbc.connect(self.connection_string, timeout=self.timeout_seconds)
                logger.debug(f"鍒涘缓鏁版嵁搴撹繛鎺?(灏濊瘯 {attempt + 1})")
                return conn
            except Exception as e:
                logger.warning(f"鍒涘缓杩炴帴澶辫触 (灏濊瘯 {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(1)
        return None

    def _is_connection_valid(self, conn: pyodbc.Connection) -> bool:
        """妫€鏌ヨ繛鎺ユ槸鍚︽湁鏁?"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False

    def get_connection(self) -> pyodbc.Connection:
        """浠庢睜涓幏鍙栬繛鎺?"""
        with self._lock:
            # 妫€鏌ュ苟娓呯悊澶辨晥杩炴帴
            now = time.time()
            if now - self._last_check > self._check_interval:
                self._pool = [c for c in self._pool if self._is_connection_valid(c)]
                self._last_check = now

            # 澶嶇敤鐜版湁杩炴帴
            if self._pool:
                return self._pool.pop()

        # 鍒涘缓鏂拌繛鎺?
        conn = self._create_connection()
        if conn is None:
            raise ConnectionError("无法创建数据库连接")
        return conn

    def release_connection(self, conn: pyodbc.Connection):
        """灏嗚繛鎺ュ綊杩樺埌姹犱腑"""
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
        """鍏抽棴鎵€鏈夎繛鎺?"""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._pool.clear()

    @property
    def size(self) -> int:
        """褰撳墠姹犱腑杩炴帴鏁?"""
        with self._lock:
            return len(self._pool)


# ========================================
# 鏃ユ湡澶勭悊宸ュ叿
# ========================================

def _normalize_date(value: Any) -> Optional[datetime]:
    """鏍囧噯鍖栨棩鏈熷€?"""
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
    """鏍煎紡鍖栨棩鏈熶负瀛楃涓?"""
    dt = _normalize_date(value)
    if dt is None:
        return ''
    return dt.strftime(fmt)


# ========================================
# 鏁版嵁搴撶鐞嗗櫒
# ========================================

class DatabaseManager:
    """鏁版嵁搴撶鐞嗗櫒锛堝惈杩炴帴姹狅級"""

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

        # 鍔犺浇閰嶇疆
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

        # 鏋勫缓杩炴帴瀛楃涓?
        self._connection_string = (
            f"DRIVER={self.db_config['driver']};"
            f"SERVER={self.db_config['server']};"
            f"DATABASE={self.db_config['database']};"
            f"UID={self.db_config['username']};"
            f"PWD={self.db_config['password']};"
            f"TrustServerCertificate=yes"
        )

        # 鍒濆鍖栬繛鎺ユ睜
        self._init_pool(pool_size)
        self._initialized = True

        logger.info(f"DatabaseManager 鍒濆鍖栧畬鎴愶紝杩炴帴姹犲ぇ灏? {pool_size}")

    def _init_pool(self, pool_size: int):
        """鍒濆鍖栬繛鎺ユ睜"""
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
        """鑾峰彇鏁版嵁搴撹繛鎺ワ紙浠庢睜涓幏鍙栵級"""
        if self._pool is None:
            # 闄嶇骇涓虹洿鎺ヨ繛鎺?
            return pyodbc.connect(self._connection_string, timeout=30)
        return self._pool.get_connection()

    def close(self, conn: pyodbc.Connection):
        """鍏抽棴杩炴帴锛堝綊杩樺埌姹犱腑锛?"""
        if self._pool is not None:
            self._pool.release_connection(conn)
        else:
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def get_connection(self):
        """涓婁笅鏂囩鐞嗗櫒鏂瑰紡鐨勮繛鎺ヨ幏鍙?"""
        conn = self.connect()
        try:
            yield conn
        finally:
            self.close(conn)

    def test_connection(self) -> Tuple[bool, str]:
        """娴嬭瘯鏁版嵁搴撹繛鎺?"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            self.close(conn)
            logger.info("数据库连接测试成功")
            return True, "杩炴帴鎴愬姛"
        except Exception as e:
            logger.error(f"鏁版嵁搴撹繛鎺ユ祴璇曞け璐? {e}")
            return False, str(e)

    def execute_query(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        fetch: bool = True
    ) -> List[Dict]:
        """鎵ц鏌ヨSQL"""
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

                    # 鏍囧噯鍖栨棩鏈熺被鍨?
                    if isinstance(value, datetime):
                        value = value  # 淇濈暀 datetime 瀵硅薄
                    elif value is None:
                        value = None

                    row_dict[col] = value
                result.append(row_dict)

            logger.info(f"查询成功，返回 {len(result)} 条记录")
            return result

        except Exception as e:
            logger.error(f"鏌ヨ鎵ц澶辫触: {str(e)}")
            logger.error(f"SQL: {sql}")
            raise
        finally:
            if conn:
                self.close(conn)

    # ========================================
    # 浼樺寲鍚庣殑鏁版嵁閲囬泦鏂规硶
    # ========================================

    def get_tool_basic_info(self) -> List[Dict]:
        """
        鑾峰彇宸ヨ鍩烘湰淇℃伅锛堢畝鍖栫増 - 浠呬粠宸ヨ韬唤鍗涓昏〃鑾峰彇锛?

        浠庝富琛ㄨ幏鍙?
        - 宸ヨ鍩烘湰淇℃伅
        - 瀹氭鍛ㄦ湡銆佸睘鎬с€佹湁鏁堟湡
        - 娲惧伐鐘舵€?
        """
        sql = """
            SELECT
                -- 宸ヨ鍩烘湰淇℃伅
                m.搴忓垪鍙?
                m.宸ヨ鍥惧彿,
                m.宸ヨ鍚嶇О,
                m.褰撳墠鐗堟,
                m.鍒堕€犵増娆?
                m.鍒堕€犳棩鏈?
                m.瀹氭鍛ㄦ湡,
                m.瀹氭灞炴€?
                m.瀹氭鏈夋晥鎴,
                m.瀹氭娲惧伐鐘舵€?
                m.瀹氭鏈夋晥鏈熷墿浣欏ぉ,
                m.搴旂敤鍘嗗彶
            FROM 宸ヨ韬唤鍗涓昏〃 m
            WHERE m.瀹氭鏈夋晥鎴 IS NOT NULL
              AND (m.瀹氭灞炴€?IS NULL OR m.瀹氭灞炴€?<> '鍚?')
              AND (m.搴旂敤鍘嗗彶 IS NULL OR m.搴旂敤鍘嗗彶 NOT LIKE '%灏佸瓨%')
        """

        results = self.execute_query(sql)

        tools = []
        now = datetime.now()

        for row in results:
            # 鏍囧噯鍖栨棩鏈?
            deadline_date = _normalize_date(row.get('瀹氭鏈夋晥鎴'))

            # 璁＄畻鍓╀綑澶╂暟
            remaining_days = row.get('瀹氭鏈夋晥鏈熷墿浣欏ぉ')
            if remaining_days is None and deadline_date:
                remaining_days = (deadline_date - now).days
            elif remaining_days is not None:
                try:
                    remaining_days = int(remaining_days)
                except (ValueError, TypeError):
                    remaining_days = None

            tool = {
                'serial_no': row.get('搴忓垪鍙?', ''),
                'drawing_no': row.get('宸ヨ鍥惧彿', ''),
                'tool_name': row.get('宸ヨ鍚嶇О', ''),
                'version': row.get('褰撳墠鐗堟', ''),
                'manufacture_version': row.get('鍒堕€犵増娆?', ''),
                'manufacture_date': _format_date(row.get('鍒堕€犳棩鏈?')),
                'cycle': row.get('瀹氭鍛ㄦ湡', ''),
                'attribute': row.get('瀹氭灞炴€?', ''),
                'deadline': _format_date(row.get('瀹氭鏈夋晥鎴')),
                'deadline_date': deadline_date,
                'dispatch_status': row.get('瀹氭娲惧伐鐘舵€?', ''),
                'remaining_days': remaining_days,
                'application_history': row.get('搴旂敤鍘嗗彶', ''),
                # 浣跨敤涓昏〃鐨勬湁鏁堟湡浣滀负瀹為檯鎴鏃ユ湡
                'effective_deadline_date': deadline_date,
                'effective_remaining_days': remaining_days
            }
            tools.append(tool)

        return tools

    def get_dispatch_info(self) -> List[Dict]:
        """鑾峰彇娲惧伐淇℃伅"""
        sql = """
            SELECT
                d.搴忓垪鍙?
                d.宸ヨ鍥惧彿,
                d.娲惧伐鍙?
                d.鐢宠宸ヨ瀹氭鏃ユ湡,
                d.瀹屾垚浜?
                d.瀹屾垚鏃ユ湡,
                d.鐢宠浜虹‘璁?
                d.TPITR,
                d.宸ヨ鐗堟,
                d.娑夊強鍒嗕綋缁勪欢鏁伴噺,
                m.鏃ユ湡Date as 娲惧伐鏃ユ湡
            FROM 宸ヨ瀹氭娲惧伐_鏄庣粏 d
            LEFT JOIN 宸ヨ瀹氭娲惧伐_涓昏〃 m ON d.ExcelServerRCID = m.ExcelServerRCID AND d.ExcelServerWIID = m.ExcelServerWIID
            ORDER BY m.鏃ユ湡Date DESC
        """
        results = self.execute_query(sql)

        dispatches = []
        for row in results:
            dispatches.append({
                'serial_no': row.get('搴忓垪鍙?', ''),
                'drawing_no': row.get('宸ヨ鍥惧彿', ''),
                'dispatch_no': row.get('娲惧伐鍙?', ''),
                'apply_date': _normalize_date(row.get('鐢宠宸ヨ瀹氭鏃ユ湡')),
                'complete_person': row.get('瀹屾垚浜?', ''),
                'complete_date': _normalize_date(row.get('瀹屾垚鏃ユ湡')),
                'applicant_confirm': row.get('鐢宠浜虹‘璁?', ''),
                'tpitr': row.get('TPITR', ''),
                'tool_version': row.get('宸ヨ鐗堟', ''),
                'component_count': row.get('娑夊強鍒嗕綋缁勪欢鏁伴噺', ''),
                'dispatch_date': _normalize_date(row.get('娲惧伐鏃ユ湡'))
            })
        return dispatches

    def get_all_tpitr_info(self) -> List[Dict]:
        """鑾峰彇鎵€鏈夋妧鏈姹備俊鎭?"""
        sql = """
            SELECT
                宸ヨ鍥惧彿,
                鐗堟,
                缂栧埗,
                缂栧埗鏃ユ湡,
                鏍″浜?
                鏍″鏃ユ湡,
                鏍″缁撹,
                鎵瑰噯浜?
                鎵瑰噯鏃ユ湡,
                鎵瑰噯缁撹,
                浼氱浜?
                璐ㄩ噺浼氱鏃ユ湡,
                浼氱缁撹,
                鏈夋晥鐘舵€?
                缂栧彿No,
                鏍″鎰忚,
                鎵瑰噯鎰忚,
                浼氱鎰忚
            FROM TPITR_涓昏〃_V11
        """
        results = self.execute_query(sql)

        tpitrs = []
        for row in results:
            tpitrs.append({
                'drawing_no': row.get('宸ヨ鍥惧彿', ''),
                'version': row.get('鐗堟', ''),
                'author': row.get('缂栧埗', ''),
                'author_date': _normalize_date(row.get('缂栧埗鏃ユ湡')),
                'checker': row.get('鏍″浜?', ''),
                'check_date': _normalize_date(row.get('鏍″鏃ユ湡')),
                'check_conclusion': row.get('鏍″缁撹', ''),
                'approver': row.get('鎵瑰噯浜?', ''),
                'approve_date': _normalize_date(row.get('鎵瑰噯鏃ユ湡')),
                'approve_conclusion': row.get('鎵瑰噯缁撹', ''),
                'signer': row.get('浼氱浜?', ''),
                'sign_date': _normalize_date(row.get('璐ㄩ噺浼氱鏃ユ湡')),
                'sign_conclusion': row.get('浼氱缁撹', ''),
                'valid_status': row.get('鏈夋晥鐘舵€?', ''),
                'tpitr_no': row.get('缂栧彿No', ''),
                'check_comment': row.get('鏍″鎰忚', ''),
                'approve_comment': row.get('鎵瑰噯鎰忚', ''),
                'sign_comment': row.get('浼氱鎰忚', '')
            })
        return tpitrs

    def get_acceptance_info(self) -> List[Dict]:
        """鑾峰彇楠屾敹淇℃伅"""
        try:
            sql = """
                SELECT
                    m.娲惧伐鍙?
                    m.琛ㄧ紪鍙?
                    m.搴忓垪鍙?
                    m.楠屾敹鐘舵€?
                    m.璁″垝鍛樻鏌ュ畬鎴愭棩鏈?
                    m.淇濈鍛樼粍缁囬獙鏀舵棩鏈?
                    m.璐ㄦ楠屾敹鏃ユ湡,
                    m.宸ヨ壓楠屾敹鏃ユ湡,
                    m.楠屾敹瀹屾垚鏃ユ湡,
                    m.淇濈鍛?
                    m.鑱斿悎楠屾敹璇存槑,
                    m.鏈€鏂伴€氱煡鍗曞彿,
                    m.澶囨敞,
                    m.鍒涘缓鏃堕棿,
                    m.淇敼鏃堕棿
                FROM 宸ヨ楠屾敹绠＄悊_涓昏〃 m
                ORDER BY m.淇敼鏃堕棿 DESC
            """
            results = self.execute_query(sql)
        except Exception as e:
            logger.warning(f"鑾峰彇楠屾敹淇℃伅澶辫触锛堣〃鍙兘涓嶅瓨鍦級: {str(e)}")
            return []

        acceptances = []
        for row in results:
            acceptances.append({
                'dispatch_no': str(row.get('娲惧伐鍙?', '') or ''),
                'table_no': str(row.get('琛ㄧ紪鍙?', '') or ''),
                'serial_no': str(row.get('搴忓垪鍙?', '') or ''),
                'acceptance_status': str(row.get('楠屾敹鐘舵€?', '') or '待检查'),
                'inspector_check_date': _normalize_date(row.get('璁″垝鍛樻鏌ュ畬鎴愭棩鏈?')),
                'keeper_org_date': _normalize_date(row.get('淇濈鍛樼粍缁囬獙鏀舵棩鏈?')),
                'qc_acceptance_date': _normalize_date(row.get('璐ㄦ楠屾敹鏃ユ湡')),
                'process_acceptance_date': _normalize_date(row.get('宸ヨ壓楠屾敹鏃ユ湡')),
                'acceptance_complete_date': _normalize_date(row.get('楠屾敹瀹屾垚鏃ユ湡')),
                'keeper': str(row.get('淇濈鍛?', '') or ''),
                'acceptance_note': str(row.get('鑱斿悎楠屾敹璇存槑', '')) if row.get('鑱斿悎楠屾敹璇存槑') else '',
                'notice_no': str(row.get('鏈€鏂伴€氱煡鍗曞彿', '')) if row.get('鏈€鏂伴€氱煡鍗曞彿') else '',
                'remarks': str(row.get('澶囨敞', '')) if row.get('澶囨敞') else '',
                'create_time': _normalize_date(row.get('鍒涘缓鏃堕棿')),
                'modify_time': _normalize_date(row.get('淇敼鏃堕棿'))
            })
        return acceptances

    def get_nonconforming_notices(self) -> List[Dict]:
        """鑾峰彇涓嶅悎鏍煎伐瑁呴€氱煡鍗?"""
        try:
            sql = """
                SELECT
                    m.閫氱煡鍗曞彿, m.鍏宠仈娲惧伐鍙? m.鍏宠仈琛ㄧ紪鍙? m.搴忓垪鍙?
                    m.妫€楠屽憳, m.缂栧埗浜? m.缂栧埗鏃ユ湡, m.澶勭悊鐘舵€?
                    m.澶嶆鏃ユ湡, m.澶嶆缁撹, m.澶嶆浜?
                    m.鍏抽棴鏃ユ湡, m.鍏抽棴浜? m.鍏抽棴璇存槑, m.鍒涘缓鏃堕棿
                FROM 涓嶅悎鏍煎伐瑁呴€氱煡鍗昣涓昏〃 m
                ORDER BY m.鍒涘缓鏃堕棿 DESC
            """
            results = self.execute_query(sql)

            notices = []
            for row in results:
                notices.append({
                    'notice_no': str(row.get('閫氱煡鍗曞彿', '')),
                    'dispatch_no': str(row.get('鍏宠仈娲惧伐鍙?', '')),
                    'table_no': str(row.get('鍏宠仈琛ㄧ紪鍙?', '')),
                    'serial_no': str(row.get('搴忓垪鍙?', '')),
                    'inspector': str(row.get('妫€楠屽憳', '')),
                    'creator': str(row.get('缂栧埗浜?', '')),
                    'create_date': _normalize_date(row.get('缂栧埗鏃ユ湡')),
                    'process_status': str(row.get('澶勭悊鐘舵€?', '') or '待处理'),
                    'recheck_date': _normalize_date(row.get('澶嶆鏃ユ湡')),
                    'recheck_conclusion': str(row.get('澶嶆缁撹', '')),
                    'rechecker': str(row.get('澶嶆浜?', '')),
                    'close_date': _normalize_date(row.get('鍏抽棴鏃ユ湡')),
                    'closer': str(row.get('鍏抽棴浜?', '')),
                    'close_note': str(row.get('鍏抽棴璇存槑', '')),
                    'create_time': _normalize_date(row.get('鍒涘缓鏃堕棿'))
                })
            return notices
        except Exception as e:
            logger.warning(f"鑾峰彇涓嶅悎鏍奸€氱煡鍗曞け璐? {str(e)}")
            return []

    def get_inspection_records(self) -> List[Dict]:
        """鑾峰彇宸ヨ瀹氭璁板綍"""
        try:
            sql = """
                SELECT 搴忓垪鍙? 宸ヨ鍚嶇О, 宸ヨ鍥惧彿, ExcelServerRCID, ExcelServerWIID
                FROM 宸ヨ瀹氭璁板綍_涓昏〃 ORDER BY 搴忓彿 DESC
            """
            results = self.execute_query(sql)
            return [{'serial_no': r.get('搴忓垪鍙?', ''),
                     'tool_name': r.get('宸ヨ鍚嶇О', ''),
                     'drawing_no': r.get('宸ヨ鍥惧彿', ''),
                     'rcid': r.get('ExcelServerRCID', ''),
                     'wiid': r.get('ExcelServerWIID', '')} for r in results]
        except Exception as e:
            logger.warning(f"鑾峰彇宸ヨ瀹氭璁板綍澶辫触: {str(e)}")
            return []

    def get_repair_records(self) -> List[Dict]:
        """鑾峰彇宸ヨ杩斾慨璁板綍"""
        try:
            sql = """
                SELECT 搴忓垪鍙? 宸ヨ鍚嶇О, 宸ヨ鍥惧彿, ExcelServerRCID, ExcelServerWIID
                FROM 宸ヨ杩斾慨璁板綍_涓昏〃 ORDER BY 搴忓彿 DESC
            """
            results = self.execute_query(sql)
            return [{'serial_no': r.get('搴忓垪鍙?', ''),
                     'tool_name': r.get('宸ヨ鍚嶇О', ''),
                     'drawing_no': r.get('宸ヨ鍥惧彿', ''),
                     'rcid': r.get('ExcelServerRCID', ''),
                     'wiid': r.get('ExcelServerWIID', '')} for r in results]
        except Exception as e:
            logger.warning(f"鑾峰彇宸ヨ杩斾慨璁板綍澶辫触: {str(e)}")
            return []

    def get_new_rework_applications(self) -> List[Dict]:
        """鑾峰彇鏈悓姝ョ殑杩斿伐鐢宠鍗?"""
        sql = """
            SELECT r.OA鐢宠鍗曠紪鍙? r.娲惧伐鍙? r.搴忓垪鍙? r.宸ヨ鍥惧彿, r.宸ヨ鍚嶇О,
                   r.杩斿伐绫诲瀷, r.鐩爣鐗堟, r.杩斿伐鍐呭, r.闇€姹傛棩鏈? r.杞綍浜? r.杞綍鏃ユ湡,
                   r.楠屾敹鏃ユ湡, r.楠屾敹浜哄憳, r.宸ヨ璁″垝鍛? r.璁″垝纭鏃ユ湡, t.褰撳墠鐗堟 as 韬唤鍗＄増娆?
            FROM 宸ヨ壓瑁呭杩斿伐鐢宠鍗昣涓昏〃 r
            LEFT JOIN 宸ヨ韬唤鍗涓昏〃 t ON r.搴忓垪鍙?= t.搴忓垪鍙?
            WHERE r.OA鐢宠鍗曠紪鍙?IS NOT NULL
              AND r.娲惧伐鍙?NOT LIKE 'C%'
              AND NOT EXISTS (SELECT 1 FROM 宸ヨ楠屾敹绠＄悊_涓昏〃 m WHERE m.娲惧伐鍙?= r.娲惧伐鍙?
              AND (r.瀛愰」绫诲瀷 = '澶栧崗杩斾慨' OR r.杩斿伐绫诲瀷 = '鍗囩増杩斾慨')
            ORDER BY r.杞綍鏃ユ湡 DESC
        """
        results = self.execute_query(sql)
        return self._parse_application_results(results, '杩斿伐')

    def get_new_tooling_applications(self) -> List[Dict]:
        """鑾峰彇鏈悓姝ョ殑鏂板埗鐢宠鍗?"""
        sql = """
            SELECT n.缂栧彿, n.娲惧伐鍙? n.宸ヨ搴忓垪鍙? n.宸ヨ鍥惧彿, n.宸ヨ鍚嶇О,
                   n.椤圭洰浠ｅ彿, n.鐗堟, n.宸ヤ綔鍖? n.鍒堕€犱緷鎹? n.鎶€鏈姹?
                   n.杞綍浜哄憳, n.杞綍鏃ユ湡, n.棰勮浣跨敤鏃堕棿, n.鐩爣鐗堟
            FROM 宸ヨ壓瑁呭鐢宠鍗昣涓昏〃 n
            WHERE n.缂栧彿 IS NOT NULL
              AND n.鎿嶄綔绫诲瀷 IN ('鏂板缓', '鏁堢巼澶嶅埗')
              AND n.娲惧伐鍙?NOT LIKE 'C%'
              AND NOT EXISTS (SELECT 1 FROM 宸ヨ楠屾敹绠＄悊_涓昏〃 m WHERE m.娲惧伐鍙?= n.娲惧伐鍙?
              AND NOT EXISTS (
                  SELECT 1 FROM 宸ヨ壓瑁呭杩斿伐鐢宠鍗昣涓昏〃 r
                  WHERE r.娲惧伐鍙?= n.娲惧伐鍙?
                    AND (r.瀛愰」绫诲瀷 = '澶栧崗杩斾慨' OR r.杩斿伐绫诲瀷 = '鍗囩増杩斾慨')
              )
            ORDER BY n.杞綍鏃ユ湡 DESC
        """
        results = self.execute_query(sql)
        return self._parse_application_results(results, '鏂板埗')

    def _parse_application_results(self, results: List[Dict], app_type: str) -> List[Dict]:
        """瑙ｆ瀽鐢宠鍗曠粨鏋?"""
        apps = []
        for row in results:
            apps.append({
                'oa_no': row.get('OA鐢宠鍗曠紪鍙?', ''),
                'apply_no': row.get('缂栧彿', ''),
                'dispatch_no': row.get('娲惧伐鍙?', ''),
                'serial_no': row.get('搴忓垪鍙?', '') or row.get('宸ヨ搴忓垪鍙?', ''),
                'drawing_no': row.get('宸ヨ鍥惧彿', ''),
                'tool_name': row.get('宸ヨ鍚嶇О', ''),
                'rework_type': row.get('杩斿伐绫诲瀷', ''),
                'target_version': row.get('鐩爣鐗堟', ''),
                'rework_content': row.get('杩斿伐鍐呭', ''),
                'required_date': _normalize_date(row.get('闇€姹傛棩鏈?')),
                'transcriber': row.get('杞綍浜?', '') or row.get('杞綍浜哄憳', ''),
                'transcribe_date': _normalize_date(row.get('杞綍鏃ユ湡')),
                'acceptance_date': _normalize_date(row.get('楠屾敹鏃ユ湡')),
                'acceptor': row.get('楠屾敹浜哄憳', ''),
                'planner': row.get('宸ヨ璁″垝鍛?', ''),
                'confirm_date': _normalize_date(row.get('璁″垝纭鏃ユ湡')),
                'card_version': row.get('韬唤鍗＄増娆?', ''),
                'version': row.get('鐗堟', ''),
                'project_code': row.get('椤圭洰浠ｅ彿', ''),
                'work_package': row.get('宸ヤ綔鍖?', ''),
                'manufacture_basis': row.get('鍒堕€犱緷鎹?', ''),
                'tech_requirement': row.get('鎶€鏈姹?', ''),
                'expected_use_date': _normalize_date(row.get('棰勮浣跨敤鏃堕棿')),
                'application_type': app_type
            })
        return apps


# ========================================
# 棰勮瑙勫垯鐩稿叧鐨勬暟鎹鐞?
# ========================================

def calculate_alert_level(deadline_date) -> Tuple[str, str, str, str]:
    """璁＄畻棰勮绛夌骇"""
    if not deadline_date:
        return 'UNKNOWN', '鏈煡', '#cccccc', '鉂?'

    today = datetime.now()
    remaining_days = (deadline_date - today).days

    if remaining_days <= 30:
        return 'CRITICAL', '绱ф€?', '#ff0000', '馃敶'
    elif remaining_days <= 90:
        return 'WARNING', '閲嶈', '#ff9900', '馃煛'
    elif remaining_days <= 180:
        return 'NOTICE', '鎻愰啋', '#ffcc00', '馃煝'
    else:
        return 'NORMAL', '姝ｅ父', '#00ff00', '鈿?'


def get_tpitr_status_detail(tpitr: Dict) -> Dict:
    """Return a conservative TPITR workflow status summary."""
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
        if '发布' in status_text or '彂甯' in status_text:
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

    if str(check_conclusion) in {'不同意', '涓嶅悓鎰?'}:
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

    if str(approve_conclusion) in {'不同意', '涓嶅悓鎰?'}:
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

    if str(sign_conclusion) in {'不同意', '涓嶅悓鎰?'}:
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


# ========================================
# 鐩戞帶缁熻鏁版嵁锛堜娇鐢ㄤ紭鍖栧悗鐨勬煡璇級
# ========================================

def get_monitor_stats() -> Dict:
    """Return lightweight dashboard counts without relying on legacy corrupted logic."""
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
        logger.error("????????: %s", str(e))
        return {'expiry': 0, 'expiry_expired': 0, 'expiry_upcoming': 0, 'total': 0}


def get_db_manager() -> DatabaseManager:
    """Return a database manager instance."""
    return DatabaseManager()


def test_db_connection() -> Tuple[bool, str]:
    """Test database connectivity."""
    try:
        DatabaseManager()
        return True, '???????'
    except Exception as e:
        return False, f'???????: {str(e)}'


def sync_applications_to_acceptance() -> Dict:
    """Placeholder compatibility hook for acceptance sync."""
    return {'success': True, 'synced': 0}


def add_acceptance_record(dispatch_no: str, serial_no: str, drawing_no: str,
                          tool_name: str, **kwargs) -> Dict:
    """Placeholder compatibility hook for acceptance insert."""
    return {'success': True}


def update_acceptance_status(dispatch_no: str, status: str, **kwargs) -> Dict:
    """Placeholder compatibility hook for acceptance status update."""
    return {'success': True}


def save_acceptance_account(dispatch_no: str, table_no: str, serial_no: str,
                            drawing_no: str, tool_name: str, **kwargs) -> Dict:
    """Placeholder compatibility hook for acceptance account save."""
    return {'success': True}


def get_inspector_acceptance_tasks(inspector: str = None) -> List[Dict]:
    """Return no acceptance tasks in compatibility mode."""
    return []


def start_inspection(dispatch_no: str, inspector: str) -> Dict:
    """Placeholder compatibility hook for starting inspection."""
    return {'success': True}


def submit_inspection_result(dispatch_no: str, result: str, **kwargs) -> Dict:
    """Placeholder compatibility hook for inspection result submit."""
    return {'success': True}


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


def get_tpitr_status() -> Dict:
    """Return lightweight TPITR status stats."""
    try:
        tpitrs = DatabaseManager().get_all_tpitr_info()
        details = []
        published = 0
        for tp in tpitrs:
            status = get_tpitr_status_detail(tp)
            if status['status'] == '???':
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


def get_acceptance_detail() -> List[Dict]:
    """Return acceptance detail when available."""
    try:
        return DatabaseManager().get_acceptance_info()
    except Exception:
        return []


def get_tpitr_categories() -> Dict:
    """Return empty TPITR categories in compatibility mode."""
    return {
        'has_tpitr_count': 0,
        'in_use_count': 0,
        'low_priority_count': 0,
        'categories': {'has_tpitr': [], 'in_use': [], 'low_priority': []},
    }


def get_expired_tpitr_status() -> Dict:
    """Return empty expired TPITR stats in compatibility mode."""
    return {'total_expired': 0, 'has_tpitr': 0, 'missing_tpitr': 0, 'expired_tools': []}


def get_overdue_dispatch_status() -> Dict:
    """Return empty overdue dispatch stats in compatibility mode."""
    return {'total_overdue': 0, 'no_dispatch': 0, 'dispatched': 0, 'overdue_tools': []}


def ensure_tool_io_tables():
    """Create the Tool IO tables required by the runtime if they do not exist."""
    db = DatabaseManager()
    create_statements = [
        """
        IF OBJECT_ID(N'??????_??', N'U') IS NULL
        CREATE TABLE [??????_??] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [?????] VARCHAR(64) NOT NULL UNIQUE,
            [????] VARCHAR(16) NOT NULL,
            [????] VARCHAR(32) NOT NULL DEFAULT 'draft',
            [???ID] VARCHAR(64) NOT NULL,
            [?????] VARCHAR(64) NOT NULL,
            [?????] VARCHAR(32) NOT NULL,
            [??] VARCHAR(64) NULL,
            [????] VARCHAR(64) NULL,
            [??] VARCHAR(255) NULL,
            [??????] DATETIME NULL,
            [??????] DATETIME NULL,
            [????ID] BIGINT NULL,
            [??????] VARCHAR(255) NULL,
            [???ID] VARCHAR(64) NULL,
            [?????] VARCHAR(64) NULL,
            [????] VARCHAR(32) NULL,
            [???ID] VARCHAR(64) NULL,
            [?????] VARCHAR(64) NULL,
            [???????] TEXT NULL,
            [??????] TEXT NULL,
            [??????] TEXT NULL,
            [???????] DATETIME NULL,
            [??????] DATETIME NULL,
            [??????] DATETIME NULL,
            [????] INT NOT NULL DEFAULT 0,
            [?????] INT NOT NULL DEFAULT 0,
            [?????] VARCHAR(64) NULL,
            [????] VARCHAR(500) NULL,
            [????] VARCHAR(500) NULL,
            [??] VARCHAR(500) NULL,
            [org_id] VARCHAR(64) NULL,
            [????] DATETIME NOT NULL DEFAULT GETDATE(),
            [????] DATETIME NOT NULL DEFAULT GETDATE(),
            [???] VARCHAR(64) NULL,
            [???] VARCHAR(64) NULL,
            [IS_DELETED] TINYINT NOT NULL DEFAULT 0
        )
        """,
        """
        IF OBJECT_ID(N'??????_??', N'U') IS NULL
        CREATE TABLE [??????_??] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [?????] VARCHAR(64) NOT NULL,
            [??ID] BIGINT NULL,
            [???] VARCHAR(64) NOT NULL,
            [????] VARCHAR(255) NULL,
            [????] VARCHAR(255) NULL,
            [??] VARCHAR(255) NULL,
            [????] DECIMAL(18,2) NOT NULL DEFAULT 1,
            [????] DECIMAL(18,2) NOT NULL DEFAULT 0,
            [????] VARCHAR(32) NOT NULL DEFAULT 'pending_check',
            [??????] VARCHAR(255) NULL,
            [????????] VARCHAR(255) NULL,
            [???????ID] BIGINT NULL,
            [?????????] VARCHAR(255) NULL,
            [???????] VARCHAR(64) NULL,
            [???????] VARCHAR(500) NULL,
            [???] VARCHAR(64) NULL,
            [??????] VARCHAR(64) NULL,
            [????] VARCHAR(500) NULL,
            [??????] VARCHAR(500) NULL,
            [????] DATETIME NULL,
            [???????] DATETIME NULL,
            [???] INT NOT NULL DEFAULT 1,
            [????] DATETIME NOT NULL DEFAULT GETDATE(),
            [????] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'??????_????', N'U') IS NULL
        CREATE TABLE [??????_????] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [?????] VARCHAR(64) NOT NULL,
            [??ID] BIGINT NULL,
            [????] VARCHAR(64) NOT NULL,
            [???ID] VARCHAR(64) NULL,
            [?????] VARCHAR(64) NULL,
            [?????] VARCHAR(64) NULL,
            [?????] VARCHAR(64) NULL,
            [?????] VARCHAR(64) NULL,
            [????] TEXT NULL,
            [????] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'??????_????', N'U') IS NULL
        CREATE TABLE [??????_????] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [?????] VARCHAR(64) NOT NULL,
            [????] VARCHAR(64) NOT NULL,
            [????] VARCHAR(64) NULL,
            [???] VARCHAR(255) NULL,
            [????] VARCHAR(255) NULL,
            [????] TEXT NULL,
            [????] TEXT NULL,
            [????] VARCHAR(32) NOT NULL DEFAULT 'pending',
            [????] DATETIME NULL,
            [????] TEXT NULL,
            [????] INT NOT NULL DEFAULT 0,
            [????] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'?????', N'U') IS NULL
        CREATE TABLE [?????] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [????] VARCHAR(64) NOT NULL,
            [????] VARCHAR(255) NOT NULL,
            [????] VARCHAR(255) NULL,
            [???] VARCHAR(64) NULL,
            [???] VARCHAR(64) NULL,
            [????] VARCHAR(255) NULL,
            [??] VARCHAR(500) NULL
        )
        """,
        f"""
        IF OBJECT_ID(N'{ORDER_NO_SEQUENCE_TABLE}', N'U') IS NULL
        CREATE TABLE {ORDER_NO_SEQUENCE_TABLE} (
            [sequence_key] VARCHAR(32) NOT NULL PRIMARY KEY,
            [current_value] INT NOT NULL,
            [updated_at] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_??????_??_??' AND object_id = OBJECT_ID(N'??????_??'))
        CREATE INDEX [IX_??????_??_??] ON [??????_??]([????])
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_??????_??_???' AND object_id = OBJECT_ID(N'??????_??'))
        CREATE INDEX [IX_??????_??_???] ON [??????_??]([???])
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_??????_??_??' AND object_id = OBJECT_ID(N'??????_??'))
        CREATE INDEX [IX_??????_??_??] ON [??????_??]([?????])
        """,
    ]

    try:
        for sql in create_statements:
            db.execute_query(sql, fetch=False)
        logger.info('?????????????')
        return True
    except Exception as e:
        logger.error('?????????????: %s', e)
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
    """鍒涘缓鍑哄叆搴撳崟锛堣崏绋跨姸鎬侊級"""
    try:
        db = DatabaseManager()
        order_no = generate_order_no_atomic(order_data.get('order_type', 'outbound'))

        sql = """
        INSERT INTO 宸ヨ鍑哄叆搴撳崟_涓昏〃 (
            鍑哄叆搴撳崟鍙? 鍗曟嵁绫诲瀷, 鍗曟嵁鐘舵€?
            鍙戣捣浜篒D, 鍙戣捣浜哄鍚? 鍙戣捣浜鸿鑹?
            閮ㄩ棬, 椤圭洰浠ｅ彿, 鐢ㄩ€? 璁″垝浣跨敤鏃堕棿, 璁″垝褰掕繕鏃堕棿,
            鐩爣浣嶇疆ID, 鐩爣浣嶇疆鏂囨湰, 澶囨敞,
            鍒涘缓鏃堕棿, 淇敼鏃堕棿
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

        # 鎻掑叆鏄庣粏
        items = order_data.get('items', [])
        for idx, item in enumerate(items):
            item_sql = """
            INSERT INTO 宸ヨ鍑哄叆搴撳崟_鏄庣粏 (
                鍑哄叆搴撳崟鍙? 宸ヨID, 搴忓垪鍙? 宸ヨ鍚嶇О, 宸ヨ鍥惧彿, 鏈哄瀷,
                鐢宠鏁伴噺, 鏄庣粏鐘舵€? 鎺掑簭鍙? 鍒涘缓鏃堕棿, 淇敼鏃堕棿
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

        # 鏇存柊涓昏〃宸ヨ鏁伴噺
        update_sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_涓昏〃 SET 宸ヨ鏁伴噺 = ? WHERE 鍑哄叆搴撳崟鍙?= ?
        """
        db.execute_query(update_sql, (len(items), order_no), fetch=False)

        # 璁板綍鏃ュ織
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.CREATE,
            'operator_id': order_data.get('initiator_id'),
            'operator_name': order_data.get('initiator_name'),
            'operator_role': order_data.get('initiator_role'),
            'before_status': '',
            'after_status': 'draft',
            'content': f"鍒涘缓鍑哄叆搴撳崟锛屽崟鍙凤細{order_no}"
        })

        return {'success': True, 'order_no': order_no}
    except Exception as e:
        logger.error(f"鍒涘缓鍑哄叆搴撳崟澶辫触: {e}")
        return {'success': False, 'error': str(e)}


def submit_tool_io_order(order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
    """鎻愪氦鍑哄叆搴撳崟"""
    try:
        db = DatabaseManager()

        # 妫€鏌ュ崟鎹姸鎬?
        check_sql = "SELECT 鍗曟嵁鐘舵€?FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃 WHERE 鍑哄叆搴撳崟鍙?= ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '鍗曟嵁涓嶅瓨鍦?'}

        current_status = result[0].get('鍗曟嵁鐘舵€?')
        if current_status != 'draft':
            return {'success': False, 'error': f'褰撳墠鐘舵€佷笉鍏佽鎻愪氦锛屽綋鍓嶇姸鎬侊細{current_status}'}

        # 鏇存柊鐘舵€佷负宸叉彁浜?
        sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_涓昏〃
        SET 鍗曟嵁鐘舵€?= 'submitted', 淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ?
        """
        db.execute_query(sql, (order_no,), fetch=False)

        # 璁板綍鏃ュ織
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.SUBMIT,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': 'draft',
            'after_status': 'submitted',
            'content': '鎻愪氦鍗曟嵁锛岀瓑寰呬繚绠″憳纭'
        })

        return {'success': True}
    except Exception as e:
        logger.error(f"鎻愪氦鍑哄叆搴撳崟澶辫触: {e}")
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


TOOL_LOCKED_ORDER_STATUSES = (
    "submitted",
    "keeper_confirmed",
    "partially_confirmed",
    "transport_notified",
    "transport_in_progress",
    "transport_completed",
    "final_confirmation_pending",
)


def check_tools_available(tool_codes: List[str], exclude_order_no: Optional[str] = None) -> Dict[str, Any]:
    """Check whether tools are already occupied by active orders."""
    cleaned_codes = []
    seen_codes = set()
    for code in tool_codes or []:
        normalized = str(code).strip()
        if not normalized or normalized in seen_codes:
            continue
        seen_codes.add(normalized)
        cleaned_codes.append(normalized)

    if not cleaned_codes:
        return {"success": True, "available": True, "occupied_tools": []}

    code_placeholders = ",".join(["?"] * len(cleaned_codes))
    status_placeholders = ",".join(["?"] * len(TOOL_LOCKED_ORDER_STATUSES))
    sql = f"""
    SELECT
        detail.[序列号] AS tool_code,
        detail.[工装名称] AS tool_name,
        main.[出入库单号] AS order_no,
        main.[单据类型] AS order_type,
        main.[单据状态] AS order_status,
        main.[发起人姓名] AS initiator_name,
        main.[创建时间] AS created_at
    FROM [工装出入库单_明细] AS detail
    INNER JOIN [工装出入库单_主表] AS main
        ON main.[出入库单号] = detail.[出入库单号]
    WHERE detail.[序列号] IN ({code_placeholders})
      AND main.[IS_DELETED] = 0
      AND main.[单据状态] IN ({status_placeholders})
    """
    params: List[Any] = list(cleaned_codes) + list(TOOL_LOCKED_ORDER_STATUSES)

    normalized_exclude_order_no = str(exclude_order_no or "").strip()
    if normalized_exclude_order_no:
        sql += " AND main.[出入库单号] <> ?"
        params.append(normalized_exclude_order_no)

    sql += " ORDER BY main.[创建时间] DESC, main.[出入库单号] DESC"
    rows = DatabaseManager().execute_query(sql, tuple(params))
    occupied_tools = [
        {
            "tool_code": str(row.get("tool_code", "")).strip(),
            "tool_name": row.get("tool_name", ""),
            "order_no": row.get("order_no", ""),
            "order_type": row.get("order_type", ""),
            "order_status": row.get("order_status", ""),
            "initiator_name": row.get("initiator_name", ""),
            "created_at": row.get("created_at"),
        }
        for row in rows
        if str(row.get("tool_code", "")).strip()
    ]
    return {
        "success": True,
        "available": not occupied_tools,
        "occupied_tools": occupied_tools,
    }


def _build_tool_occupied_error(occupied_tools: List[Dict[str, Any]]) -> str:
    """Build a user-facing occupied tool message."""
    if not occupied_tools:
        return ""

    summary_parts = []
    seen_pairs = set()
    for item in occupied_tools:
        tool_code = str(item.get("tool_code", "")).strip()
        order_no = str(item.get("order_no", "")).strip()
        if not tool_code or not order_no:
            continue
        key = (tool_code, order_no)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        summary_parts.append(f"{tool_code}（单号：{order_no}，状态：{item.get('order_status', '-') or '-'}）")

    if not summary_parts:
        return "所选工装已被其他进行中的单据占用"
    return "以下工装已被其他进行中的单据占用：" + "；".join(summary_parts)


def create_tool_io_order(order_data: dict) -> dict:
    """Create a tool IO order using the actual runtime schema."""
    try:
        db = DatabaseManager()
        items = order_data.get("items")
        if not isinstance(items, list) or not items:
            return {"success": False, "error": "请至少选择一项工装"}
        if not all(isinstance(item, dict) for item in items):
            return {"success": False, "error": "工装明细格式不正确"}

        order_type = order_data.get("order_type")
        if order_type not in {"outbound", "inbound"}:
            return {"success": False, "error": "单据类型不正确"}

        tool_codes = [str(item.get("tool_code", "")).strip() for item in items if str(item.get("tool_code", "")).strip()]
        if len(tool_codes) != len(items):
            return {"success": False, "error": "每条明细都必须包含序列号"}
        if len(set(tool_codes)) != len(tool_codes):
            return {"success": False, "error": "同一张单据内不能重复选择相同序列号"}

        try:
            tool_master_map = _load_tool_master_map(tool_codes)
        except Exception as exc:
            logger.warning("加载工装主表失败，创建单据时回退到请求快照: %s", exc)
            tool_master_map = {}

        missing_codes = [code for code in tool_codes if code not in tool_master_map]
        for item in items:
            tool_code = str(item.get("tool_code", "")).strip()
            if tool_code in missing_codes:
                tool_master_map[tool_code] = {
                    "tool_code": tool_code,
                    "tool_name": item.get("tool_name", ""),
                    "drawing_no": item.get("drawing_no", ""),
                    "spec_model": item.get("spec_model", ""),
                    "current_location_text": item.get("current_location_text", ""),
                    "status_text": item.get("status_text", ""),
                }

        missing_codes = [code for code in tool_codes if code not in tool_master_map]
        if missing_codes:
            return {"success": False, "error": f"以下工装不存在：{', '.join(missing_codes)}"}

        occupied = check_tools_available(tool_codes)
        if not occupied.get("available", True):
            return {"success": False, "error": _build_tool_occupied_error(occupied.get("occupied_tools", [])), "occupied_tools": occupied.get("occupied_tools", [])}

        order_no = generate_order_no_atomic(order_type)
        insert_order_sql = """
        INSERT INTO [工装出入库单_主表] (
            [出入库单号], [单据类型], [单据状态], [发起人ID], [发起人姓名], [发起人角色],
            [部门], [项目代号], [用途], [计划使用时间], [计划归还时间],
            [目标位置ID], [目标位置文本], [备注], [工装数量], [已确认数量], [org_id],
            [创建时间], [修改时间], [创建人], [修改人], [IS_DELETED]
        ) VALUES (?, ?, 'draft', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), ?, ?, 0)
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
                order_data.get("org_id"),
                order_data.get("initiator_name"),
                order_data.get("initiator_name"),
            ),
            fetch=False,
        )

        insert_item_sql = """
        INSERT INTO [工装出入库单_明细] (
            [出入库单号], [工装ID], [序列号], [工装名称], [工装图号], [机型],
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
            return {"success": False, "error": "单据不存在"}

        current_status = result[0].get("单据状态")
        if current_status != "draft":
            return {"success": False, "error": f"当前状态不允许提交：{current_status}"}

        detail_rows = db.execute_query(
            "SELECT [序列号] AS tool_code FROM [工装出入库单_明细] WHERE [出入库单号] = ?",
            (order_no,),
        )
        if not detail_rows:
            return {"success": False, "error": "单据没有工装明细"}

        tool_codes = [str(row.get("tool_code", "")).strip() for row in detail_rows if str(row.get("tool_code", "")).strip()]
        occupied = check_tools_available(tool_codes, exclude_order_no=order_no)
        if not occupied.get("available", True):
            return {"success": False, "error": _build_tool_occupied_error(occupied.get("occupied_tools", [])), "occupied_tools": occupied.get("occupied_tools", [])}

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
    """鑾峰彇鍑哄叆搴撳崟璇︽儏"""
    try:
        db = DatabaseManager()

        # 鑾峰彇涓昏〃
        sql = "SELECT * FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃 WHERE 鍑哄叆搴撳崟鍙?= ?"
        result = db.execute_query(sql, (order_no,))
        if not result:
            return {}

        order = result[0]

        # 鑾峰彇鏄庣粏
        items_sql = "SELECT * FROM 工装出入库单_明细 WHERE 出入库单号 = ? ORDER BY 排序号"
        items = db.execute_query(items_sql, (order_no,))
        order['items'] = items

        return order
    except Exception as e:
        logger.error(f"鑾峰彇鍑哄叆搴撳崟璇︽儏澶辫触: {e}")
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
    """鏌ヨ鍑哄叆搴撳崟鍒楄〃"""
    try:
        db = DatabaseManager()

        conditions = ["IS_DELETED = 0"]
        params = []

        if order_type:
            conditions.append("鍗曟嵁绫诲瀷 = ?")
            params.append(order_type)
        if order_status:
            conditions.append("鍗曟嵁鐘舵€?= ?")
            params.append(order_status)
        if initiator_id:
            conditions.append("鍙戣捣浜篒D = ?")
            params.append(initiator_id)
        if keeper_id:
            conditions.append("淇濈鍛業D = ?")
            params.append(keeper_id)
        if keyword:
            conditions.append("(鍑哄叆搴撳崟鍙?LIKE ? OR 椤圭洰浠ｅ彿 LIKE ? OR 鐢ㄩ€?LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        if date_from:
            conditions.append("鍒涘缓鏃堕棿 >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("鍒涘缓鏃堕棿 <= ?")
            params.append(date_to)

        where_clause = " AND ".join(conditions)

        # 鏌ヨ鎬绘暟
        count_sql = f"SELECT COUNT(*) as total FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃 WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(params))
        total = count_result[0].get('total', 0) if count_result else 0

        # Use a single filtered query for pagination so placeholder counts stay aligned
        # even when optional filters are present.
        offset = (page_no - 1) * page_size
        list_sql = f"""
        SELECT * FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃
        WHERE {where_clause}
        ORDER BY 鍒涘缓鏃堕棿 DESC
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
        logger.error(f"鏌ヨ鍑哄叆搴撳崟鍒楄〃澶辫触: {e}")
        return {'success': False, 'error': str(e), 'data': [], 'total': 0}


def search_tools(
    keyword: str = None,
    status: str = None,
    location_id: int = None,
    page_no: int = 1,
    page_size: int = 20
) -> dict:
    """Search tool master data from ?????_??."""
    try:
        db = DatabaseManager()
        serial_column = '[???]'
        spec_model_column = '[??]'

        probe_sql = """
        SELECT
            CASE WHEN COL_LENGTH(N'?????_??', N'???') IS NOT NULL THEN 1 ELSE 0 END AS has_serial,
            CASE WHEN COL_LENGTH(N'?????_??', N'????') IS NOT NULL THEN 1 ELSE 0 END AS has_spec_model
        """
        probe = db.execute_query(probe_sql)
        if probe:
            if not probe[0].get('has_serial'):
                serial_column = '[????]'
            if probe[0].get('has_spec_model'):
                spec_model_column = '[????]'

        conditions = [f"{serial_column} IS NOT NULL", f"LTRIM(RTRIM({serial_column})) <> ''"]
        params = []

        if keyword:
            keyword_like = f"%{keyword.strip()}%"
            conditions.append(
                f"""
                (
                    {serial_column} LIKE ?
                    OR [????] LIKE ?
                    OR [????] LIKE ?
                    OR {spec_model_column} LIKE ?
                    OR [??] LIKE ?
                    OR [????] LIKE ?
                    OR [????] LIKE ?
                    OR [???] LIKE ?
                    OR [????] LIKE ?
                    OR [???] LIKE ?
                )
                """
            )
            params.extend([keyword_like] * 10)

        if status:
            status_like = f"%{status.strip()}%"
            conditions.append(
                """
                (
                    [????] LIKE ?
                    OR [??????] LIKE ?
                    OR [?????] LIKE ?
                )
                """
            )
            params.extend([status_like, status_like, status_like])

        if location_id not in (None, ''):
            location_like = f"%{str(location_id).strip()}%"
            conditions.append(
                """
                (
                    [??] LIKE ?
                    OR [????] LIKE ?
                )
                """
            )
            params.extend([location_like, location_like])

        where_clause = ' AND '.join(conditions)
        count_sql = f"SELECT COUNT(*) AS total FROM [?????_??] WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(params))
        total = int(count_result[0].get('total', 0)) if count_result else 0

        offset = max(page_no - 1, 0) * page_size
        list_sql = f"""
        SELECT
            {serial_column} AS tool_code,
            {serial_column} AS tool_id,
            {serial_column} AS ???,
            [????] AS tool_name,
            [????] AS drawing_no,
            {spec_model_column} AS spec_model,
            {spec_model_column} AS ??,
            [????] AS current_version,
            [??] AS current_location_text,
            [????] AS application_history,
            [????] AS available_status,
            [??????] AS valid_status,
            [?????] AS io_status,
            [????] AS owner_name,
            [???] AS work_package,
            [????] AS main_material,
            [???] AS manufacturer,
            [??????] AS inspection_expiry_date,
            [????] AS inspection_category,
            [????] AS inspection_cycle,
            COALESCE([?????], [????], [??????], '') AS status_text
        FROM [?????_??]
        WHERE {where_clause}
        ORDER BY {serial_column}
        OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
        """
        rows = db.execute_query(list_sql, tuple(params))
        return {
            'success': True,
            'data': rows,
            'total': total,
            'page_no': page_no,
            'page_size': page_size,
        }
    except Exception as e:
        logger.error('??????: %s', e)
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
    """淇濈鍛樼‘璁ゅ嚭鍏ュ簱鍗?"""
    try:
        db = DatabaseManager()

        if not isinstance(confirm_data, dict):
            return {'success': False, 'error': 'confirm_data must be an object'}

        items = confirm_data.get('items')
        if not isinstance(items, list) or not items:
            return {'success': False, 'error': 'confirm_data.items must contain at least one item'}

        # 妫€鏌ュ崟鎹姸鎬?
        check_sql = "SELECT 鍗曟嵁绫诲瀷, 鍗曟嵁鐘舵€?FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃 WHERE 鍑哄叆搴撳崟鍙?= ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '鍗曟嵁涓嶅瓨鍦?'}

        order_type = result[0].get('鍗曟嵁绫诲瀷')
        current_status = result[0].get('鍗曟嵁鐘舵€?')
        if current_status not in ['submitted', 'partially_confirmed']:
            return {'success': False, 'error': f'褰撳墠鐘舵€佷笉鍏佽纭锛屽綋鍓嶇姸鎬侊細{current_status}'}

        # 鏇存柊鏄庣粏
        approved_count = 0
        for item in items:
            item_sql = """
            UPDATE 宸ヨ鍑哄叆搴撳崟_鏄庣粏 SET
                淇濈鍛樼‘璁や綅缃甀D = ?,
                淇濈鍛樼‘璁や綅缃枃鏈?= ?,
                淇濈鍛樻鏌ョ粨鏋?= ?,
                淇濈鍛樻鏌ュ娉?= ?,
                纭鏁伴噺 = ?,
                鏄庣粏鐘舵€?= ?,
                纭浜? = ?,
                纭鏃堕棿 = GETDATE(),
                椹冲洖鍘熷洜 = ?,
                淇敼鏃堕棿 = GETDATE()
            WHERE 鍑哄叆搴撳崟鍙?= ? AND 搴忓垪鍙?= ?
            """
            status = item.get('status', 'approved')
            if status == 'approved':
                approved_count += 1
            reject_reason = ''
            if status != 'approved':
                reject_reason = str(item.get('reject_reason') or item.get('check_remark') or '').strip()

            db.execute_query(item_sql, (
                item.get('location_id'),
                item.get('location_text'),
                item.get('check_result'),
                item.get('check_remark'),
                item.get('approved_qty', 1),
                status,
                keeper_id or operator_id,
                reject_reason or None,
                order_no,
                item.get('tool_code')
            ), fetch=False)

        # 鏇存柊涓昏〃鐘舵€?
        new_status = 'keeper_confirmed' if approved_count == len(items) else 'partially_confirmed'
        update_sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_涓昏〃 SET
            鍗曟嵁鐘舵€?= ?,
            淇濈鍛業D = ?,
            淇濈鍛樺鍚?= ?,
            杩愯緭绫诲瀷 = ?,
            杩愯緭浜篒D = ?,
            杩愯緭浜哄鍚?= ?,
            淇濈鍛樼‘璁ゆ椂闂?= GETDATE(),
            宸茬‘璁ゆ暟閲?= ?,
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ?
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

        # 璁板綍鏃ュ織
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.KEEPER_CONFIRM,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': current_status,
            'after_status': new_status,
            'content': f'淇濈鍛樼‘璁わ紝閫氳繃 {approved_count}/{len(items)} 椤?'
        })

        return {'success': True, 'status': new_status, 'approved_count': approved_count}
    except Exception as e:
        logger.error(f"淇濈鍛樼‘璁ゅけ璐? {e}")
        return {'success': False, 'error': str(e)}


def final_confirm_order(
    order_no: str,
    operator_id: str,
    operator_name: str,
    operator_role: str
) -> dict:
    """鏈€缁堢‘璁ゅ畬鎴愬嚭鍏ュ簱鍗?"""
    try:
        db = DatabaseManager()

        # 妫€鏌ュ崟鎹姸鎬?
        check_sql = "SELECT 鍗曟嵁绫诲瀷, 鍗曟嵁鐘舵€?FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃 WHERE 鍑哄叆搴撳崟鍙?= ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '鍗曟嵁涓嶅瓨鍦?'}

        order_type = result[0].get('鍗曟嵁绫诲瀷')
        current_status = result[0].get('鍗曟嵁鐘舵€?')

        if current_status not in ['keeper_confirmed', 'partially_confirmed', 'transport_notified', 'final_confirmation_pending']:
            return {'success': False, 'error': f'褰撳墠鐘舵€佷笉鍏佽鏈€缁堢‘璁わ紝褰撳墠鐘舵€侊細{current_status}'}

        # 鏇存柊涓昏〃鐘舵€?
        sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_涓昏〃 SET
            鍗曟嵁鐘舵€?= 'completed',
            鏈€缁堢‘璁や汉 = ?,
            鏈€缁堢‘璁ゆ椂闂?= GETDATE(),
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ?
        """
        db.execute_query(sql, (operator_name, order_no), fetch=False)

        # 鏇存柊鏄庣粏鐘舵€?
        update_items_sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_鏄庣粏 SET
            鏄庣粏鐘舵€?= 'completed',
            鍑哄叆搴撳畬鎴愭椂闂?= GETDATE(),
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ? AND 鏄庣粏鐘舵€?= 'approved'
        """
        db.execute_query(update_items_sql, (order_no,), fetch=False)

        # 璁板綍鏃ュ織
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
        logger.error(f"鏈€缁堢‘璁ゅけ璐? {e}")
        return {'success': False, 'error': str(e)}


def reject_tool_io_order(
    order_no: str,
    reject_reason: str,
    operator_id: str,
    operator_name: str,
    operator_role: str
) -> dict:
    """椹冲洖鍑哄叆搴撳崟"""
    try:
        db = DatabaseManager()

        # 妫€鏌ョ姸鎬?
        check_sql = "SELECT 鍗曟嵁鐘舵€?FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃 WHERE 鍑哄叆搴撳崟鍙?= ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '鍗曟嵁涓嶅瓨鍦?'}

        current_status = result[0].get('鍗曟嵁鐘舵€?')
        if current_status not in ['submitted', 'keeper_confirmed', 'partially_confirmed']:
            return {'success': False, 'error': f'褰撳墠鐘舵€佷笉鍏佽椹冲洖锛屽綋鍓嶇姸鎬侊細{current_status}'}

        # 鏇存柊鐘舵€?
        sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_涓昏〃 SET
            鍗曟嵁鐘舵€?= 'rejected',
            椹冲洖鍘熷洜 = ?,
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ?
        """
        db.execute_query(sql, (reject_reason, order_no), fetch=False)

        # 鏇存柊鏄庣粏鐘舵€?
        update_items_sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_鏄庣粏 SET
            鏄庣粏鐘舵€?= 'rejected',
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ?
        """
        db.execute_query(update_items_sql, (order_no,), fetch=False)

        # 璁板綍鏃ュ織
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
        logger.error(f"椹冲洖鍗曟嵁澶辫触: {e}")
        return {'success': False, 'error': str(e)}


def cancel_tool_io_order(
    order_no: str,
    operator_id: str,
    operator_name: str,
    operator_role: str
) -> dict:
    """鍙栨秷鍑哄叆搴撳崟"""
    try:
        db = DatabaseManager()

        # 妫€鏌ョ姸鎬?
        check_sql = "SELECT 鍗曟嵁鐘舵€?FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃 WHERE 鍑哄叆搴撳崟鍙?= ?"
        result = db.execute_query(check_sql, (order_no,))
        if not result:
            return {'success': False, 'error': '鍗曟嵁涓嶅瓨鍦?'}

        current_status = result[0].get('鍗曟嵁鐘舵€?')
        if current_status in ['completed', 'rejected', 'cancelled']:
            return {'success': False, 'error': f'褰撳墠鐘舵€佷笉鍏佽鍙栨秷锛屽綋鍓嶇姸鎬侊細{current_status}'}

        # 鏇存柊鐘舵€?
        sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_涓昏〃 SET
            鍗曟嵁鐘舵€?= 'cancelled',
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ?
        """
        db.execute_query(sql, (order_no,), fetch=False)

        # 鏇存柊鏄庣粏鐘舵€?
        update_items_sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_鏄庣粏 SET
            鏄庣粏鐘舵€?= 'rejected',
            淇敼鏃堕棿 = GETDATE()
        WHERE 鍑哄叆搴撳崟鍙?= ?
        """
        db.execute_query(update_items_sql, (order_no,), fetch=False)

        # 璁板綍鏃ュ織
        add_tool_io_log({
            'order_no': order_no,
            'action_type': ToolIOAction.CANCEL,
            'operator_id': operator_id,
            'operator_name': operator_name,
            'operator_role': operator_role,
            'before_status': current_status,
            'after_status': 'cancelled',
            'content': '鍗曟嵁宸插彇娑?'
        })

        return {'success': True}
    except Exception as e:
        logger.error(f"鍙栨秷鍗曟嵁澶辫触: {e}")
        return {'success': False, 'error': str(e)}


def add_tool_io_log(log_data: dict) -> bool:
    """璁板綍鎿嶄綔鏃ュ織"""
    try:
        db = DatabaseManager()
        sql = """
        INSERT INTO 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織 (
            鍑哄叆搴撳崟鍙? 鏄庣粏ID, 鎿嶄綔绫诲瀷, 鎿嶄綔浜篒D, 鎿嶄綔浜哄鍚? 鎿嶄綔浜鸿鑹?
            鍙樻洿鍓嶇姸鎬? 鍙樻洿鍚庣姸鎬? 鎿嶄綔鍐呭, 鎿嶄綔鏃堕棿
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
        logger.error(f"璁板綍鎿嶄綔鏃ュ織澶辫触: {e}")
        return False


def get_tool_io_logs(order_no: str) -> list:
    """鑾峰彇鎿嶄綔鏃ュ織"""
    try:
        db = DatabaseManager()
        sql = """
        SELECT * FROM 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織
        WHERE 鍑哄叆搴撳崟鍙?= ?
        ORDER BY 鎿嶄綔鏃堕棿 DESC
        """
        return db.execute_query(sql, (order_no,))
    except Exception as e:
        logger.error(f"鑾峰彇鎿嶄綔鏃ュ織澶辫触: {e}")
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
        INSERT INTO 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍 (
            鍑哄叆搴撳崟鍙? 閫氱煡绫诲瀷, 閫氱煡娓犻亾, 鎺ユ敹浜? 閫氱煡鏍囬,
            閫氱煡鍐呭, 澶嶅埗鏂囨湰, 鍙戦€佺姸鎬? 鍒涘缓鏃堕棿
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
    """鏇存柊閫氱煡鐘舵€?"""
    try:
        db = DatabaseManager()
        sql = """
        UPDATE 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍 SET
            鍙戦€佺姸鎬?= ?,
            鍙戦€佹椂闂?= GETDATE(),
            鍙戦€佺粨鏋?= ?
        WHERE id = ?
        """
        db.execute_query(sql, (status, send_result, notify_id), fetch=False)
        return True
    except Exception as e:
        logger.error(f"鏇存柊閫氱煡鐘舵€佸け璐? {e}")
        return False


def get_pending_keeper_orders(keeper_id: str = None) -> list:
    """鑾峰彇寰呬繚绠″憳纭鐨勫崟鎹?"""
    try:
        db = DatabaseManager()
        sql = """
        SELECT * FROM 宸ヨ鍑哄叆搴撳崟_涓昏〃
        WHERE 鍗曟嵁鐘舵€?IN ('submitted', 'partially_confirmed')
        AND IS_DELETED = 0
        """
        params = []
        if keeper_id:
            sql += " AND (淇濈鍛業D = ? OR 淇濈鍛業D IS NULL)"
            params.append(keeper_id)
        sql += " ORDER BY 鍒涘缓鏃堕棿 DESC"

        return db.execute_query(sql, tuple(params))
    except Exception as e:
        logger.error(f"鑾峰彇寰呯‘璁ゅ崟鎹け璐? {e}")
        return []

