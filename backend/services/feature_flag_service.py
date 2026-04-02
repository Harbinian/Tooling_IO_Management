# -*- coding: utf-8 -*-
"""Feature flag service for centralized feature management."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from backend.database.repositories.system_config_repository import SystemConfigRepository

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Centralized service for managing feature flags with caching."""

    def __init__(self, cache_ttl_seconds: int = 60):
        self._repo = SystemConfigRepository()
        self._cache: Dict[str, Tuple[str, datetime]] = {}
        self._cache_ttl = cache_ttl_seconds

    def _is_cache_valid(self, flag_key: str) -> bool:
        if flag_key not in self._cache:
            return False
        _, cached_at = self._cache[flag_key]
        return datetime.now() - cached_at < timedelta(seconds=self._cache_ttl)

    def _get_cached_value(self, flag_key: str) -> Optional[str]:
        if not self._is_cache_valid(flag_key):
            return None
        return self._cache[flag_key][0]

    def _set_cache(self, flag_key: str, value: str) -> None:
        self._cache[flag_key] = (value, datetime.now())

    def _invalidate_cache(self, flag_key: str) -> None:
        if flag_key in self._cache:
            del self._cache[flag_key]

    def is_enabled(self, flag_key: str) -> bool:
        """Check if a feature flag is enabled."""
        cached = self._get_cached_value(flag_key)
        if cached is not None:
            return cached.lower() in ("true", "1", "yes")

        db_value = self._repo.get_config(flag_key)
        if db_value is not None:
            self._set_cache(flag_key, db_value)
            return db_value.lower() in ("true", "1", "yes")

        return False

    def get_flag_value(self, flag_key: str, default: Optional[str] = None) -> Optional[str]:
        """Get the raw value of a feature flag."""
        cached = self._get_cached_value(flag_key)
        if cached is not None:
            return cached

        db_value = self._repo.get_config(flag_key)
        if db_value is not None:
            self._set_cache(flag_key, db_value)
            return db_value

        return default

    def get_all_flags(self) -> List[Dict]:
        """Get all feature flags with metadata."""
        return self._repo.list_configs()

    def set_flag(self, flag_key: str, value: Any, operator_id: str) -> bool:
        """Update a feature flag value and invalidate cache."""
        str_value = str(value) if value is not None else ""
        success = self._repo.set_config(flag_key, str_value, operator_id)
        if success:
            self._invalidate_cache(flag_key)
        return success

    def invalidate_cache(self, flag_key: str) -> None:
        """Explicitly invalidate cache for a specific flag."""
        self._invalidate_cache(flag_key)

    def invalidate_all_cache(self) -> None:
        """Clear all cached values."""
        self._cache.clear()


_feature_flag_service: Optional[FeatureFlagService] = None


def get_feature_flag_service() -> FeatureFlagService:
    """Get the singleton FeatureFlagService instance."""
    global _feature_flag_service
    if _feature_flag_service is None:
        _feature_flag_service = FeatureFlagService()
    return _feature_flag_service


def is_feature_enabled(flag_key: str) -> bool:
    """Convenience function to check if a feature flag is enabled."""
    return get_feature_flag_service().is_enabled(flag_key)


def get_feature_flag_value(flag_key: str, default: Optional[str] = None) -> Optional[str]:
    """Convenience function to get a feature flag value."""
    return get_feature_flag_service().get_flag_value(flag_key, default)
