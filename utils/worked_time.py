import pytz
from datetime import datetime, timedelta, timezone
from utils.time import datetime_str, str_to_datetime
from copy import deepcopy


class DateRange:
    def __init__(self, _timezone):
        self.tz = _timezone

    def start(self):
        raise NotImplementedError

    def end(self):
        return datetime.now(self.tz)


class MonthDateRange(DateRange):
    def start(self):
        return (
            datetime.now(self.tz)
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .replace(day=1)
        )


class WeekDateRange(DateRange):
    def start(self):
        result = datetime.now(self.tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        result = result - timedelta(days=result.weekday())
        return result


class DayDateRange(DateRange):
    def start(self):
        return datetime.now(self.tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )


def date_range():
    dr = MonthDateRange(pytz.UTC)
    start = dr.start() - timedelta(days=6)
    return {
        "start_date": datetime_str(start),
        "end_date": datetime_str(dr.end()),
    }


class WorkedTime:
    def __init__(self, time_entries):
        self.time_entries = time_entries

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


def filter_time_entries(time_entries, dr: DateRange):
    start, end = dr.start(), dr.end()
    result = []
    for t in time_entries:
        te_start, te_end = (
            str_to_datetime(t.start_date),
            str_to_datetime(t.end_date),
        )
        in_range = start <= te_start <= end or start <= te_end <= end
        if in_range:
            result.append(deepcopy(t))
    return result


def cut_time_entries_out_of_range(time_entries, dr):
    start, end = dr.start(), dr.end()
    for t in time_entries:
        te_start, te_end = (
            str_to_datetime(t.start_date),
            str_to_datetime(t.end_date),
        )
        if te_start < start:
            t.start_date = datetime_str(start)
        if end < te_end:
            t.end_date = datetime_str(end)


def worked_time_in_day(time_entries, tz):
    dr = DayDateRange(tz)
    day_time_entries = filter_time_entries(time_entries, dr)
    cut_time_entries_out_of_range(day_time_entries, dr)
    return WorkedTime(day_time_entries).summary()


def worked_time_in_week(time_entries, tz):
    dr = WeekDateRange(tz)
    week_time_entries = filter_time_entries(time_entries, dr)
    cut_time_entries_out_of_range(week_time_entries, dr)
    return WorkedTime(week_time_entries).summary()


def worked_time_in_month(time_entries, tz):
    dr = MonthDateRange(tz)
    month_time_entries = filter_time_entries(time_entries, dr)
    cut_time_entries_out_of_range(month_time_entries, dr)
    return WorkedTime(month_time_entries).summary()


def stop_running_time_entry(time_entries, tz):
    end = datetime.now(tz)
    for t in time_entries:
        if t.end_date is None:
            t.end_date = datetime_str(end)


def change_timezones(time_entries, tz):
    for t in time_entries:
        start_date = str_to_datetime(t.start_date)
        end_date = str_to_datetime(t.end_date)

        t.start_date = datetime_str(start_date.astimezone(tz))
        t.end_date = datetime_str(end_date.astimezone(tz))


def summary(time_entries, time_offset):
    offset_in_minutes = time_offset if time_offset else 300
    tz = timezone(timedelta(minutes=-offset_in_minutes))
    stop_running_time_entry(time_entries, tz)
    change_timezones(time_entries, tz)
    return {
        'day': worked_time_in_day(time_entries, tz),
        'week': worked_time_in_week(time_entries, tz),
        'month': worked_time_in_month(time_entries, tz),
    }
