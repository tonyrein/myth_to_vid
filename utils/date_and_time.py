import iso8601
from django.utils import timezone

import datetime
import pytz


"""
Pass: a datetime, possibly not tz-aware
Return: a timezone-aware datetime,
using UTC.
"""
def ensure_tz_aware(dt):
    if not timezone.is_aware(dt):
        dt = timezone.make_aware(dt, pytz.timezone('Etc/UTC'))
    return dt

"""
Pass: a timezone-aware datetime in
any arbitrary timezone

Return: a timezone-aware datetime using UTC
"""
def ensure_utc(dt):
    if not 'UTC' in dt.tzinfo._tzname.upper():
        dt = dt.astimezone(pytz.timezone('Etc/UTC'))
    return dt

"""
Pass: a tz-aware datetime in utc
Return: the equivalent local dt
From http://stackoverflow.com/questions/4563272/how-to-convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-stand/13287083#13287083
"""
def utc_dt_to_local_dt(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

"""
Given two time/date strings in the format 2015-11-22 18:00:03,
figure out the number of seconds between them.

Pass:
  * Two iso-format time/date strings. We assume that both are UTC.
Return:
  * Difference between them, in seconds (int)
"""
def time_diff_from_strings(start_time, end_time):
    end_dt = iso8601.parse_date(end_time, pytz.timezone('Etc/UTC'))
    start_dt = iso8601.parse_date(start_time, pytz.timezone('Etc/UTC'))
    return (int)(end_dt.timestamp() - start_dt.timestamp())