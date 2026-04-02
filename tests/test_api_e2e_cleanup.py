from datetime import datetime, timedelta

from test_runner import api_e2e
from test_runner.api_e2e import _is_known_test_project, _should_cleanup_order


def _build_order(order_no: str, order_status: str, created_at: datetime):
    return {
        "order_no": order_no,
        "order_status": order_status,
        "created_at": created_at.isoformat(timespec="seconds"),
    }


def test_should_cleanup_old_auto_order():
    order = _build_order(
        "TO-OUT-AUTO_04010000_ABCD",
        "keeper_confirmed",
        datetime.now() - timedelta(hours=30),
    )

    should_cleanup, reason = _should_cleanup_order(order)

    assert should_cleanup is True
    assert "auto_test_order" in reason


def test_should_cleanup_old_locked_order():
    order = _build_order(
        "TO-OUT-20260402-003",
        "keeper_confirmed",
        datetime.now() - timedelta(hours=30),
    )

    should_cleanup, reason = _should_cleanup_order(order)

    assert should_cleanup is True
    assert "locked_status=keeper_confirmed" in reason


def test_should_not_cleanup_recent_locked_order():
    order = _build_order(
        "TO-OUT-20260402-004",
        "keeper_confirmed",
        datetime.now() - timedelta(hours=2),
    )

    should_cleanup, reason = _should_cleanup_order(order)

    assert should_cleanup is False
    assert reason == ""


def test_should_cleanup_old_completed_order():
    order = _build_order(
        "TO-OUT-20260401-001",
        "completed",
        datetime.now() - timedelta(hours=26),
    )

    should_cleanup, reason = _should_cleanup_order(order)

    assert should_cleanup is True
    assert "terminal_status=completed" in reason


def test_should_recognize_known_test_project():
    order = {
        "order_no": "TO-OUT-20260402-003",
        "project_code": "WF_TEST_001",
        "order_status": "keeper_confirmed",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    assert _is_known_test_project(order) is True


def test_should_cleanup_recent_test_fixture_order(monkeypatch):
    order = {
        "order_no": "TO-OUT-20260402-003",
        "project_code": "WF_TEST_001",
        "order_status": "keeper_confirmed",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    monkeypatch.setattr(
        api_e2e,
        "_fetch_order_detail_for_cleanup",
        lambda order_no, token: {
            "order_no": order_no,
            "project_code": "WF_TEST_001",
            "items": [{"serial_no": "T000001", "drawing_no": "Tooling_IO_TEST"}],
        },
    )

    should_cleanup, reason = _should_cleanup_order(order, token="dummy-token")

    assert should_cleanup is True
    assert "test_fixture_order" in reason
