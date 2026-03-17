# -*- coding: utf-8 -*-
"""
Database connection pool implementation.
"""

import pyodbc
import logging
import threading
import time
from typing import List, Optional

logger = logging.getLogger(__name__)


class ConnectionPool:
    """
    Database connection pool.

    Features:
    - Pre-create specified number of connections
    - Connection reuse to reduce creation overhead
    - Thread-safe
    - Connection health checking
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
        self._check_interval = 60  # Check connection health every 60 seconds

    def _create_connection(self) -> Optional[pyodbc.Connection]:
        """Create a new connection."""
        for attempt in range(self.max_retries):
            try:
                conn = pyodbc.connect(self.connection_string, timeout=self.timeout_seconds)
                logger.debug(f"Created database connection (attempt {attempt + 1})")
                return conn
            except Exception as e:
                logger.warning(f"Failed to create connection (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(1)
        return None

    def _is_connection_valid(self, conn: pyodbc.Connection) -> bool:
        """Check if connection is valid."""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False

    def get_connection(self) -> pyodbc.Connection:
        """Get a connection from the pool."""
        with self._lock:
            # Check and clean up invalid connections
            now = time.time()
            if now - self._last_check > self._check_interval:
                self._pool = [c for c in self._pool if self._is_connection_valid(c)]
                self._last_check = now

            # Reuse existing connection
            if self._pool:
                return self._pool.pop()

        # Create new connection
        conn = self._create_connection()
        if conn is None:
            raise ConnectionError("Failed to create database connection")
        return conn

    def release_connection(self, conn: pyodbc.Connection):
        """Return a connection to the pool."""
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
        """Close all connections."""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._pool.clear()

    @property
    def size(self) -> int:
        """Current number of connections in the pool."""
        with self._lock:
            return len(self._pool)
