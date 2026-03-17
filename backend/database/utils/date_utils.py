# -*- coding: utf-8 -*-
"""Date utility functions."""

from datetime import datetime
from typing import Any, Optional


def normalize_date(value: Any) -> Optional[datetime]:
    """
    Standardize date value.

    Handles various input formats:
    - datetime objects (returned as-is)
    - strings in various formats (Y-m-d, Y-m-d H:M:S, etc.)
    - None or empty values (returns None)

    Args:
        value: The value to normalize

    Returns:
        datetime object or None
    """
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


def format_date(value: Any, fmt: str = '%Y-%m-%d') -> str:
    """
    Format date as string.

    Args:
        value: The value to format (will be normalized first)
        fmt: Output format string

    Returns:
        Formatted date string or empty string
    """
    dt = normalize_date(value)
    if dt is None:
        return ''
    return dt.strftime(fmt)


def format_datetime(value: Any, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format datetime as string with time.

    Args:
        value: The value to format
        fmt: Output format string

    Returns:
        Formatted datetime string or empty string
    """
    return format_date(value, fmt)


def get_date_range(days: int) -> tuple:
    """
    Get date range from today.

    Args:
        days: Number of days (negative for past, positive for future)

    Returns:
        Tuple of (start_date, end_date) as datetime objects
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if days >= 0:
        return (today, today.replace(day=today.day + days))
    else:
        return (today.replace(day=today.day + days), today)


def is_date_in_range(date: Optional[datetime], start: Optional[datetime], end: Optional[datetime]) -> bool:
    """
    Check if date is within range.

    Args:
        date: Date to check
        start: Start of range (inclusive)
        end: End of range (inclusive)

    Returns:
        True if date is in range
    """
    if date is None:
        return False
    if start is not None and date < start:
        return False
    if end is not None and date > end:
        return False
    return True
