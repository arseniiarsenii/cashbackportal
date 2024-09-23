import random
from datetime import datetime, timedelta, timezone


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def start_of_month(date: datetime | None = None) -> datetime:
    if date is None:
        date = utc_now()
    return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(tz=timezone.utc)


def random_dt(start: datetime, end: datetime) -> datetime:
    delta = end - start
    int_delta = int(delta.total_seconds())
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)
