from datetime import datetime, timedelta
from utils.time import (
    current_datetime,
    current_datetime_str,
    start_datetime_of_current_month,
    start_datetime_of_current_week,
    start_datetime_of_current_day,
    start_datetime_of_current_month_str,
)


def date_range():
    return {
        "start_date": start_datetime_of_current_month_str(),
        "end_date": current_datetime_str(),
    }


def stop_running_time_entry(time_entries):
    for t in time_entries:
        if t.end_date is None:
            t.end_date = current_datetime_str()


class WorkedTime:
    def __init__(self, time_entries):
        self.time_entries = time_entries

    @classmethod
    def from_time_entries_in_range(
        cls, time_entries, start_date: datetime, end_date: datetime
    ):
        time_entries_in_range = [
            t for t in time_entries if t.in_range(start_date, end_date)
        ]
        return cls(time_entries_in_range)

    def total_time_in_seconds(self):
        times = [t.elapsed_time for t in self.time_entries]
        total_time = sum(times, timedelta())
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
    return WorkedTime.from_time_entries_in_range(
        time_entries,
        start_date=start_datetime_of_current_day(),
        end_date=current_datetime(),
    ).summary()


def worked_time_in_week(time_entries):
    return WorkedTime.from_time_entries_in_range(
        time_entries,
        start_date=start_datetime_of_current_week(),
        end_date=current_datetime(),
    ).summary()


def worked_time_in_month(time_entries):
    return WorkedTime.from_time_entries_in_range(
        time_entries,
        start_date=start_datetime_of_current_month(),
        end_date=current_datetime(),
    ).summary()


def summary(time_entries, time_offset):
    offset_in_minutes = time_offset if time_offset else 300
    print(offset_in_minutes)
    stop_running_time_entry(time_entries)
    return {
        'day': worked_time_in_day(time_entries),
        'week': worked_time_in_week(time_entries),
        'month': worked_time_in_month(time_entries),
    }
