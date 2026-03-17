# -*- coding: utf-8 -*-
"""Database utility functions."""

from backend.database.utils.date_utils import (
    normalize_date,
    format_date,
    format_datetime,
    get_date_range,
    is_date_in_range,
)

from backend.database.utils.sql_utils import (
    quote_sql_string,
    build_add_column_sql,
    build_create_index_sql,
    build_rename_column_sql,
    build_in_clause,
    build_pagination_sql,
    build_count_sql,
    is_duplicate_key_error,
    safe_bigint,
    build_where_clause,
    build_set_clause,
)

__all__ = [
    # Date utils
    "normalize_date",
    "format_date",
    "format_datetime",
    "get_date_range",
    "is_date_in_range",
    # SQL utils
    "quote_sql_string",
    "build_add_column_sql",
    "build_create_index_sql",
    "build_rename_column_sql",
    "build_in_clause",
    "build_pagination_sql",
    "build_count_sql",
    "is_duplicate_key_error",
    "safe_bigint",
    "build_where_clause",
    "build_set_clause",
]
