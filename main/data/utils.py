#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zoneinfo
import dateutil.relativedelta as relativedelta
import re
import time
from datetime import datetime
from typing import Union

from archappl.config import SITE_CONFIG

TS_FMT = "%Y-%m-%dT%H:%M:%S.%f"
LOCAL_ZONE_NAME = SITE_CONFIG.get("misc", {}).get("local_timezone", time.tzname[0])
LOCAL_ZONE = zoneinfo.ZoneInfo(LOCAL_ZONE_NAME)
UTC_ZONE = zoneinfo.ZoneInfo("UTC")


class DatetimeTuple:
    def __init__(self, year: int = 1970, month: int = 1, day: int = 1,
                 hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond


def standardize_datetime(date_time: Union[tuple, datetime], time_zone: Union[str, None] = None):
    """Standardize datetime (object or tuple of int) to iso8601 UTC string format.

    Parameters
    ----------
    date_time : tuple | datetime
        A tuple of `(year, month, day, hour, minute, second, millisecond)` or a shorter one;
        or define with a datetime object, if `tzinfo` is defined, ignore *time_zone*.
    time_zone : str
        Name of timezone, default is local time zone, e.g. 'EST',
        see `zoneinfo.available_timezones()`.

    Returns
    -------
    r : tuple
        A tuple of datetime object and ISO8601 UTC string represented datetime, e.g.
        '2020-11-19T12:28:30.000Z'.

    Examples
    --------
    >>> from datetime import datetime
    >>> t0_dst = datetime(2016, 11, 5, 23, 0, 0, 0)
    >>> t0 = datetime_with_timezone(t0_dst)
    >>> print(standardize_datetime(t0)[1])
    2016-11-06T03:00:00.000Z
    >>> t_tuple = (2016, 11, 5, 23)
    >>> print(standardize_datetime(t_tuple)[1])
    2016-11-06T03:00:00.000Z
    """
    if time_zone is None:
        _tz = LOCAL_ZONE
    else:
        _tz = zoneinfo.ZoneInfo(time_zone)

    if isinstance(date_time, tuple):
        # a tuple as datetime without tzinfo
        dt_tuple = DatetimeTuple(*date_time)
        _t = datetime(dt_tuple.year, dt_tuple.month, dt_tuple.day,
                      dt_tuple.hour, dt_tuple.minute, dt_tuple.second,
                      dt_tuple.millisecond * 1000)
        # represent the datetime at the defined timezone and convert to UTC zone
        t = datetime_with_timezone(_t.replace(tzinfo=_tz), 'UTC')
    else:
        # date_time is a datetime object
        if date_time.tzinfo is not None:
            # convert to UTC zone for a datetime with tzinfo defined
            t = date_time.astimezone(UTC_ZONE)
        else:
            # represent the datetime at the defined timezone
            _t = datetime_with_timezone(date_time, _tz.key)
            # then convert to UTC zone
            t = datetime_with_timezone(_t, 'UTC')
    return t, f"{t.year:4d}-{t.month:02d}-{t.day:02d}T{t.hour:02d}:{t.minute:02d}:{t.second:02d}.{int(t.microsecond/1000.0):03d}Z"


def iso_to_epoch(s):
    """Conert ISO datetime string to epoch float.

    Parameters
    ----------
    s : str
        ISO datetime string.

    Returns
    -------
    r : tuple
        epoch sec and timezone string.

    See Also
    --------
    epoch_to_iso
    """
    ts, tz = s[:-6], s[-6:]
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
    return dt.timestamp(), tz


def epoch_to_iso(ts, tz="-05:00"):
    """Return ISO datetime string from epoch sec.

    Parameters
    ----------
    ts : float
        Epoch sec.
    tz : str
        Timezone string.

    Returns
    -------
    r : str
        ISO datetime string.
    """
    return datetime.fromtimestamp(ts).isoformat() + tz


def datetime_with_timezone(date_time, time_zone: Union[str, None] = None):
    """Represent datetime object *date_time* with timezone info (`tzinfo`).

    If the input *date_time* does have `tzinfo`, and if *time_zone* is defined, convert
    *date_time* to the defined timezone, otherwise does nothing.

    If the input *date_time* does NOT have `tzinfo` (`tzinfo` is None), set with the defined *time_zone*
    as the `tzinfo`, keep the date time values untouched.

    Parameters
    ----------
    date_time : datetime
        Datetime object.
    time_zone : str
        Name of timezone, default is local time zone, e.g. 'EST',
        see `zoneinfo.available_timezones()`.

    Returns
    -------
    r : datetime
        Datetime object with timezone info.

    Examples
    --------
    >>> from datetime import datetime
    >>> dt0 = datetime.now()  # local timezone datetime, but without tzinfo explicitly define.
    >>> print(dt0.isoformat())
    2025-09-17T14:58:16.409648
    >>> dt0_w_tz = datetime_with_timezone(dt0)
    >>> print(dt0_w_tz.tzinfo.key)
    America/Detroit
    >>> print(dt0_w_tz.tzname())
    EDT
    >>> dt1 = datetime_with_timezone(dt0_w_tz, time_zone='UTC')  # represent last datetime in UTC zone
    >>> print(dt1.tzinfo.key)
    UTC
    >>> print(dt1.hour - dt0_w_tz.hour) # UTC is ahead of EDT by 4 hours
    4
    >>> dt2 = datetime(2020, 11, 10, 1, 12, 3, 456789) # arbitrary datetime but w/o zone
    >>> print(dt2)
    2020-11-10 01:12:03.456789
    >>> # present dt2 at local zone
    >>> dt2_local = datetime_with_timezone(dt2)
    >>> print(dt2_local)
    2020-11-10 01:12:03.456789-05:00
    >>> # amend it with 'UTC' zone, only affect tz
    >>> dt2_at_utc = datetime_with_timezone(dt2, time_zone='UTC')
    >>> print(dt2_at_utc) # only append timezone +00:00
    2020-11-10 01:12:03.456789+00:00
    >>> # represent dt2 at UTC zone
    >>> dt2_as_utc = datetime_with_timezone(dt2_local, time_zone='UTC')
    >>> print(dt2_as_utc)
    2020-11-10 06:12:03.456789+00:00
    >>> print((dt2_at_utc - dt2_local).total_seconds() / 3600)
    -5.0
    >>> print((dt2_as_utc - dt2_local).total_seconds())
    0.0
    """
    if time_zone is None:
        _timezone = LOCAL_ZONE
    else:
        _timezone = zoneinfo.ZoneInfo(time_zone)
    if date_time.tzinfo is not None:
        if time_zone is not None:
            # convert to the defined timezone
            return date_time.astimezone(_timezone)
        else:
            return date_time
    else:
        # set the defined timezone
        return date_time.replace(tzinfo=_timezone)


def is_dst(date_time):
    """Return if *date_time* is in daylight saving time period.

    Examples
    --------
    >>> from datetime import datetime
    >>>
    >>> t0 = datetime(2016, 11, 2, 12, 34, 56, 123456)  # local time at America/New_York
    >>> print(is_dst(t0))
    True
    >>> print(is_dst(t0.astimezone(zoneinfo.ZoneInfo('UTC'))))
    False
    """
    if date_time.tzinfo is None:
        return bool(datetime_with_timezone(date_time).dst())
    else:
        return bool(datetime_with_timezone(date_time).dst())


# see phantasy.parse_dt
def parse_dt(dt, ref_datetime=None, epoch=None):
    """Parse delta time defined by *dt*, which is presenting in plain English,
    e.g. '1 hour and 30 mins ago', return datetime object at the same timezone.
    The if tzinfo is missing in *ref_datetime*, use local timezone.

    Parameters
    ----------
    dt : str
        Relative time difference w.r.t. current date time, defined in valid units:
        *years*, *months*, *weeks*, *days*, *hours*, *minutes*, *seconds*,
        *microseconds*, and some unit alias: *year*, *month*, *week*, *day*,
        *hour*, *minute*, *second*, *microsecond*, *mins*, *secs*, *msecs*,
        *min*, *sec*, *msec*, could be linked by string 'and' or ',',
        ends with 'before', or begins with 'after', e.g. '5 mins before',
        '1 hour and 30 mins before', 'after 15 seconds', etc.
    ref_datetime : datetime
        Datetime object, with tzinfo, if not defined, use current local datetime.
    epoch : bool
        If return date time as seconds since Epoch.

    Warning
    -------
    Only support integer number when defining time unit.

    Returns
    -------
    ret : datetime
        Datetime object with the same tzinfo of reference datetime.

    See Also
    --------
    datetime_with_timezone

    Examples
    --------
    >>> dt0 = datetime_with_timezone(datetime.now())
    >>> dt1 = parse_dt("1 hour before", dt0)
    >>> dt2 = parse_dt("after 1 hour", dt0)
    >>> assert dt0 - dt1 == dt2 - dt0
    >>> assert (dt0 - dt1).total_seconds() == 3600.0
    >>> dt_str = '1 month, 2 weeks, 4 hours, 7 mins and 10 secs before'
    >>> print(parse_dt(dt_str, datetime(2016, 12, 10, 12, 34, 56, 123456)))
    >>> # local tz EST --> datetime at DST
    2016-10-27 09:27:46.123456-04:00
    >>> t0 = datetime(2016, 11, 5, 23, 0, 0, 0)  # DST
    >>> print(datetime_with_timezone(t0))
    2016-11-05 23:00:00-04:00
    >>> parse_dt("after 3 hours", t0)
    2016-11-06 01:00:00-05:00
    """
    if ref_datetime is None:
        ref_dt = datetime_with_timezone(datetime.now())
    elif isinstance(ref_datetime, datetime):
        if ref_datetime.tzinfo is None:
            ref_dt = datetime_with_timezone(ref_datetime)
        else:
            ref_dt = ref_datetime
    else:
        raise TypeError("Invalid datetime variable.")

    time_unit_table = {'years': 'years', 'months': 'months', 'weeks': 'weeks',
                       'days': 'days', 'hours': 'hours', 'minutes': 'minutes',
                       'seconds': 'seconds', 'microseconds': 'microseconds',
                       'year': 'years', 'month': 'months', 'week': 'weeks',
                       'day': 'days', 'hour': 'hours', 'minute': 'minutes',
                       'second': 'seconds', 'microsecond': 'microseconds',
                       'min': 'minutes', 'sec': 'seconds',
                       'msec': 'microseconds', 'mins': 'minutes',
                       'secs': 'seconds', 'msecs': 'microseconds'}

    is_retro = 'before' in dt or 'ago' in dt
    dt_dict = {}
    dt_tuple = dt.replace('after', '').replace('and', ',').replace('before', ',').replace('ago', ',').strip(' ,').split(',')
    for part in dt_tuple:
        v, k = part.strip().split()
        dt_dict[time_unit_table[k]] = int(v)

    dt = relativedelta.relativedelta(**dt_dict)

    ref_dt_as_utc = datetime_with_timezone(ref_dt, time_zone='UTC')
    if is_retro:
        _datetime_as_utc = ref_dt_as_utc - dt
    else:
        _datetime_as_utc = ref_dt_as_utc + dt
    _datetime = datetime_with_timezone(_datetime_as_utc, time_zone=ref_dt.tzinfo.key)
    if epoch:
        r = _datetime.timestamp
    else:
        r = _datetime
    return datetime_with_timezone(r)


def iso_to_datetime(s: str) -> tuple[datetime, str]:
    """ Parse a ISO8601 string into a datetime object with ZoneInfo.

    Supported inputs:
    - 2021-04-15T21:25:00.000Z     -> UTC
    - 2021-04-15T17:25:00.00-04:00 -> UTC-4
    - 2021-04-15T17:25:00.00       -> local zone
    - 2021-04-15T17:25:00          -> expand ms, local zone
    - 2021-04-15T17:25             -> expand seconds + ms, local zone

    Returns
    -------
    r : tuple
        A tuple of datetime object and isoformat at UTC zone.
    """
    # Normalize Z → +00:00
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    # Expand forms like YYYY-MM-DDTHH:MM
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$", s):
        s += ":00.00"
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", s):
        s += ".00"

    # Try parsing with timezone info
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        raise ValueError(f"Unsupported datetime format: {s}")

    # If no tzinfo, add local zone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL_ZONE)

    # convert to UTC zone
    return standardize_datetime(dt, "UTC")


# see phantasy_ui.printlog
def printlog(*msg, ctime=None, fmt=None):
    """Print message(s) with current timestamp or defined by *ctime*.

    Parameters
    ----------
    msg :
        Messages.
    ctime : float
        Timestamp.
    fmt : str
        Format for strftime(), default is "%Y-%m-%dT%H:%M:%S.%f".

    Examples
    --------
    >>> printlog('a', 'b', 'c')
    [2020-01-14T11:22:10.475744] a, b, c
    >>> printlog(1, 2, 3)
    [2020-01-14T11:22:57.500679] a, b
    >>> printlog("This is a log message.")
    [2020-01-14T11:23:40.389471] This is a log message.
    """
    ts = time.time() if ctime is None else ctime
    f = TS_FMT if fmt is None else fmt
    print("[{}] {}".format(
        datetime.fromtimestamp(ts).strftime(f), ', '.join((str(i) for i in msg))))


if __name__ == "__main__":
    s = "2019-03-05T13:04:08.120000-05:00"
    f, tz = iso_to_epoch(s)
    assert f == 1551809048.12
    assert tz == "-05:00"
    assert epoch_to_iso(f, tz) == s

