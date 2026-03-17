# -*- coding: utf-8 -*-
"""SQL utility functions."""

from typing import List, Any, Optional


def quote_sql_string(value: str) -> str:
    """
    Quote SQL string for safe inclusion in SQL.

    Args:
        value: String to quote

    Returns:
        Quoted string
    """
    return value.replace("'", "''")


def build_add_column_sql(table_name: str, column_name: str, definition: str) -> str:
    """
    Build SQL to add a column if it doesn't exist.

    Args:
        table_name: Name of the table
        column_name: Name of the column
        definition: Column definition (e.g., 'VARCHAR(64) NULL')

    Returns:
        SQL statement
    """
    quoted_table = quote_sql_string(table_name)
    quoted_column = quote_sql_string(column_name)
    return f"""
    IF COL_LENGTH(N'{quoted_table}', N'{quoted_column}') IS NULL
    BEGIN
        ALTER TABLE [{table_name}] ADD [{column_name}] {definition}
    END
    """


def build_create_index_sql(table_name: str, index_name: str, column_list: str) -> str:
    """
    Build SQL to create an index if it doesn't exist.

    Args:
        table_name: Name of the table
        index_name: Name of the index
        column_list: Comma-separated column names

    Returns:
        SQL statement
    """
    quoted_table = quote_sql_string(table_name)
    quoted_index = quote_sql_string(index_name)
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


def build_rename_column_sql(table_name: str, old_name: str, new_name: str) -> str:
    """
    Build SQL to rename a column.

    Args:
        table_name: Name of the table
        old_name: Current column name
        new_name: New column name

    Returns:
        SQL statement
    """
    quoted_table = quote_sql_string(table_name)
    quoted_old_name = quote_sql_string(old_name)
    quoted_new_name = quote_sql_string(new_name)
    return f"""
    IF COL_LENGTH(N'{quoted_table}', N'{quoted_old_name}') IS NOT NULL
       AND COL_LENGTH(N'{quoted_table}', N'{quoted_new_name}') IS NULL
    BEGIN
        EXEC sp_rename N'{quoted_table}.{quoted_old_name}', N'{quoted_new_name}', 'COLUMN'
    END
    """


def build_in_clause(values: List[Any], param_prefix: str = "") -> tuple:
    """
    Build IN clause with placeholders.

    Args:
        values: List of values
        param_prefix: Prefix for parameter names

    Returns:
        Tuple of (placeholder_string, param_tuple)
    """
    placeholders = ",".join(["?"] * len(values))
    return placeholders, tuple(values)


def build_pagination_sql(
    base_sql: str,
    order_by: str,
    page_no: int = 1,
    page_size: int = 20
) -> str:
    """
    Build paginated SQL query.

    Args:
        base_sql: Base SELECT query (without ORDER BY)
        order_by: ORDER BY clause
        page_no: Page number (1-indexed)
        page_size: Number of records per page

    Returns:
        Paginated SQL query
    """
    offset = max(page_no - 1, 0) * page_size
    return f"""
    {base_sql}
    {order_by}
    OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
    """


def build_count_sql(base_sql: str) -> str:
    """
    Build COUNT query from base SQL.

    Args:
        base_sql: Base SELECT query

    Returns:
        SELECT COUNT(*) query
    """
    # Remove SELECT ... FROM and add COUNT(*)
    if "ORDER BY" in base_sql.upper():
        base_sql = base_sql[:base_sql.upper().rfind("ORDER BY")]
    return f"SELECT COUNT(*) AS total FROM ({base_sql}) AS count_query"


def is_duplicate_key_error(error: Exception) -> bool:
    """
    Check if error is a duplicate key violation.

    Args:
        error: Exception to check

    Returns:
        True if it's a duplicate key error
    """
    message = str(error).lower()
    return (
        "duplicate" in message
        or "unique" in message
        or "2601" in message
        or "2627" in message
    )


def safe_bigint(value: Any) -> Optional[int]:
    """
    Convert value to BIGINT-safe integer.

    Args:
        value: Value to convert

    Returns:
        Integer or None
    """
    if value in (None, ""):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def build_where_clause(conditions: List[str], conjunction: str = "AND") -> str:
    """
    Build WHERE clause from conditions.

    Args:
        conditions: List of condition strings
        conjunction: Logical operator (AND/OR)

    Returns:
        WHERE clause string
    """
    if not conditions:
        return ""
    return f" WHERE {f' {conjunction} '.join(conditions)}"


def build_set_clause(assignments: List[str]) -> str:
    """
    Build SET clause from assignments.

    Args:
        assignments: List of assignment strings (e.g., "column = ?")

    Returns:
        SET clause string
    """
    if not assignments:
        return ""
    return f" SET {', '.join(assignments)}"
