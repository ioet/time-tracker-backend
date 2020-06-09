from datetime import datetime, timedelta, timezone
from utils.time import (
    datetime_str,
    get_current_month,
    get_current_year,
    current_datetime,
    current_datetime_str,
)


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


def str_to_datetime(
    value: str, conversion_format: str = '%Y-%m-%dT%H:%M:%S.%fZ'
) -> datetime:
    if 'Z' in value:
        return datetime.strptime(value, conversion_format).astimezone(
            timezone.utc
        )
    else:
        return datetime.fromisoformat(value).astimezone(timezone.utc)


def date_range():
    return {
        "start_date": start_datetime_of_current_month_str(),
        "end_date": current_datetime_str(),
    }


def filter_time_entries(
    time_entries, start_date: datetime, end_date: datetime = current_datetime()
):
    return [
        t
        for t in time_entries
        if start_date <= str_to_datetime(t.start_date) <= end_date
        or start_date <= str_to_datetime(t.end_date) <= end_date
    ]


def stop_running_time_entry(time_entries):
    for t in time_entries:
        if t.end_date is None:
            t.end_date = current_datetime_str()


class WorkedTime:
    def __init__(self, time_entries):
        self.time_entries = time_entries

    def total_time_in_seconds(self):
        times = []

        for t in self.time_entries:
            start_datetime = str_to_datetime(t.start_date)
            end_datetime = str_to_datetime(t.end_date)

            elapsed_time = end_datetime - start_datetime
            times.append(elapsed_time)

        total_time = timedelta()
        for time in times:
            total_time += time

        return total_time.total_seconds()

    def hours(self):
        return self.total_time_in_seconds() // 3600

    def minutes(self):
        return (self.total_time_in_seconds() % 3600) // 60

    def seconds(self):
        return (self.total_time_in_seconds() % 3600) % 60

    def summary(self):
        return {
            "hours": self.hours(),
            "minutes": self.minutes(),
            "seconds": round(self.seconds(), 2),
        }


def worked_time_in_day(time_entries):
    day_time_entries = filter_time_entries(
        time_entries, start_date=start_datetime_of_current_day()
    )
    return WorkedTime(day_time_entries).summary()


def worked_time_in_week(time_entries):
    week_time_entries = filter_time_entries(
        time_entries, start_date=start_datetime_of_current_week()
    )
    return WorkedTime(week_time_entries).summary()


def worked_time_in_month(time_entries):
    month_time_entries = filter_time_entries(
        time_entries, start_date=start_datetime_of_current_month()
    )
    return WorkedTime(month_time_entries).summary()


def summary(time_entries, time_offset):
    print(time_offset)
    stop_running_time_entry(time_entries)
    return {
        'day': worked_time_in_day(time_entries),
        'week': worked_time_in_week(time_entries),
        'month': worked_time_in_month(time_entries),
    }
