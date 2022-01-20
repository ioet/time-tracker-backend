import pytz
from typing import Dict
from datetime import datetime, timezone


def datetime_str(value: datetime) -> str:
    if value is not None:
        return value.isoformat()
    else:
        return None


def current_datetime() -> datetime:
    return datetime.now(pytz.UTC)


def current_datetime_str() -> str:
    return datetime_str(current_datetime())


def get_current_year() -> int:
    return datetime.now(pytz.UTC).year


def get_current_month() -> int:
    return datetime.now(pytz.UTC).month


def get_current_day() -> int:
    return datetime.now(pytz.UTC).day


def get_date_range_of_month(year: int, month: int):
    def get_last_day_of_month(year: int, month: int) -> int:
        from calendar import monthrange

        return monthrange(year=year, month=month)[1]

    start_date = datetime(year=year, month=month, day=1, tzinfo=timezone.utc)

    end_date = datetime(
        year=year,
        month=month,
        day=get_last_day_of_month(year, month),
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
        tzinfo=timezone.utc,
    )

    return start_date, end_date


def str_to_datetime(value: str) -> datetime:
    def to_utc(date: datetime) -> datetime:
        from pytz import timezone

        _tz = timezone('UTC')
        localized = _tz.localize(date)
        return localized

    from dateutil import parser

    no_timezone_info = parser.parse(value).tzinfo is None
    if no_timezone_info:
        return to_utc(parser.parse(value))
    else:
        return parser.parse(value)
