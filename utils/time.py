import pytz
from typing import Dict
from datetime import datetime, timezone, timedelta


def current_datetime_str() -> str:
    from utils.time import datetime_str

    return datetime_str(current_datetime())


def current_datetime() -> datetime:
    return datetime.now(pytz.UTC)


def get_current_year() -> int:
    return datetime.now().year


def get_current_month() -> int:
    return datetime.now().month


def get_current_day() -> int:
    return datetime.now().day


def datetime_str(value: datetime) -> str:
    if value is not None:
        return value.isoformat()
    else:
        return None


def get_date_range_of_month(year: int, month: int) -> Dict[str, str]:
    def get_last_day_of_month(year: int, month: int) -> int:
        from calendar import monthrange

        return monthrange(year=year, month=month)[1]

    first_day_of_month = 1
    start_date = datetime(
        year=year, month=month, day=first_day_of_month, tzinfo=timezone.utc
    )

    last_day_of_month = get_last_day_of_month(year=year, month=month)
    end_date = datetime(
        year=year,
        month=month,
        day=last_day_of_month,
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
        tzinfo=timezone.utc,
    )

    return {
        'start_date': datetime_str(start_date),
        'end_date': datetime_str(end_date),
    }


def start_datetime_of_current_month() -> datetime:
    return datetime(
        year=get_current_year(),
        month=get_current_month(),
        day=1,
        tzinfo=timezone.utc,
    )


def start_datetime_of_current_week() -> datetime:
    today = current_datetime()
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=000000)
    return monday


def start_datetime_of_current_day() -> datetime:
    today = current_datetime()
    today = today.replace(hour=0, minute=0, second=0, microsecond=000000)
    return today


def start_datetime_of_current_month_str() -> str:
    return datetime_str(start_datetime_of_current_month())


def str_to_datetime(value: str) -> datetime:
    from dateutil.parser import isoparse
    from dateutil.tz import tzutc

    assert type(isoparse(value).tzinfo) == tzutc
    return isoparse(value)
