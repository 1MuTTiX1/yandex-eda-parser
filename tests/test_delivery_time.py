import pytest

pytest.importorskip("selenium", reason="selenium не установлен")

from datetime import datetime  # noqa: E402

from eda_parser.scraper import target_delivery_time  # noqa: E402


def test_target_is_tomorrow_at_hour():
    now = datetime(2026, 11, 11, 14, 43, 12)
    assert target_delivery_time(15, now) == datetime(2026, 11, 12, 15, 0)


def test_target_crosses_month_boundary():
    now = datetime(2026, 11, 30, 23, 59)
    assert target_delivery_time(15, now) == datetime(2026, 12, 1, 15, 0)
