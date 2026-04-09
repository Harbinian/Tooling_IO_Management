# -*- coding: utf-8 -*-
"""pytest configuration for test suite."""
import os
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marks tests requiring real database connection (skip when TESTING_DB_URL not set)"
    )


def pytest_collection_modifyitems(items):
    """Skip integration tests when no database is available."""
    db_url = os.environ.get("TESTING_DB_URL") or os.environ.get("DATABASE_URL")
    skip_integration = pytest.mark.skip(
        reason="No TESTING_DB_URL configured — integration tests skipped"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
