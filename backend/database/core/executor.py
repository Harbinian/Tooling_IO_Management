# -*- coding: utf-8 -*-
"""
Query executor with logging wrapper.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from backend.database.core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class QueryExecutor:
    """
    Query executor with standardized logging.

    Provides a wrapper around DatabaseManager.execute_query with:
    - Query logging
    - Performance metrics
    - Error handling
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def execute(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        fetch: bool = True,
        log_query: bool = True
    ) -> List[Dict]:
        """
        Execute a query with logging.

        Args:
            sql: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            log_query: Whether to log the query

        Returns:
            List of result dictionaries
        """
        start_time = datetime.now()

        try:
            if log_query:
                logger.debug(f"Executing query: {sql[:200]}...")

            result = self._db.execute_query(sql, params, fetch)

            elapsed = (datetime.now() - start_time).total_seconds()
            if log_query:
                logger.info(f"Query executed in {elapsed:.3f}s, returned {len(result)} rows")

            return result

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error(f"Query failed after {elapsed:.3f}s: {str(e)}")
            logger.error(f"SQL: {sql}")
            if params:
                logger.error(f"Params: {params}")
            raise

    def execute_many(
        self,
        sql: str,
        params_list: List[Tuple],
        log_queries: bool = True
    ) -> int:
        """
        Execute a query multiple times with different parameters.

        Args:
            sql: SQL query string
            params_list: List of parameter tuples
            log_queries: Whether to log queries

        Returns:
            Number of affected rows
        """
        from backend.database.core.database_manager import DatabaseManager

        conn = None
        cursor = None
        try:
            conn = self._db.connect()
            cursor = conn.cursor()

            for params in params_list:
                if log_queries:
                    logger.debug(f"Executing batch: {sql[:100]}...")
                cursor.execute(sql, params)

            conn.commit()
            return len(params_list)

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Batch execution failed: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._db.close(conn)

    def execute_with_transaction(
        self,
        queries: List[Tuple[str, Optional[Tuple]]],
        log_queries: bool = True
    ) -> bool:
        """
        Execute multiple queries in a single transaction.

        Args:
            queries: List of (sql, params) tuples
            log_queries: Whether to log queries

        Returns:
            True if successful
        """
        from backend.database.core.database_manager import DatabaseManager

        conn = None
        cursor = None
        try:
            conn = self._db.connect()
            cursor = conn.cursor()

            for sql, params in queries:
                if log_queries:
                    logger.debug(f"Transaction query: {sql[:100]}...")
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

            conn.commit()
            logger.info(f"Transaction committed successfully ({len(queries)} queries)")
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Transaction failed and rolled back: {str(e)}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                self._db.close(conn)
