#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import datetime
import dateutil.relativedelta as relativedelta
import pytz
import time
import tzlocal

TS_FMT = "%Y-%m-%dT%H:%M:%S.%f"
LOCAL_ZONE = tzlocal.get_localzone()
LOCAL_ZONE_NAME = LOCAL_ZONE.zone # America/New_York

DatetimeTuple = namedtuple('DatetimeTuple',
        ['year', 'month', 'day', 'hour', 'minute', 'second', 'millisecond'],
        defaults=[1970, 1, 1, 0, 0, 0, 0])


def standardize_datetime(date_time, time_zone=None):
    """Standardize datetime (object or string) to iso8601 UTC string format.

    Parameters
    ----------
    date_time : tuple of str or datetime
        String representation of datetime, with a tuple of (year, month,
        day, hour, minute, second, millisecond), define timezone by
        *timezone* argument. Or define with datetime object, if tzinfo is defined,
        ignore *time_zone*.
    time_zone : str
        Name of time zone, default is local zone, e.g. America/New_York,
        see also: pytz.all_timezones.

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
    >>> print(standardize_datetime(t0))
    2016-11-06T03:00:00.000Z
    >>> t_tuple = (2016, 11, 5, 23)
    >>> print(standardize_datetime(t_tuple))
    2016-11-06T03:00:00.000Z
    """
    if time_zone is None:
        _tz = LOCAL_ZONE
    else:
        _tz = pytz.timezone(time_zone)

    if isinstance(date_time, tuple):
        dt_tuple = DatetimeTuple(*date_time)
        _t = datetime(dt_tuple.year, dt_tuple.month, dt_tuple.day,
                      dt_tuple.hour, dt_tuple.minute, dt_tuple.second,
                      dt_tuple.millisecond * 1000)
        t = datetime_with_timezone(_tz.localize(_t), 'UTC')
    else: # datetime
        if date_time.tzinfo is not None:
            t = date_time.astimezone(pytz.timezone('UTC'))
        else:
            _t = datetime_with_timezone(date_time, _tz.zone)
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


def datetime_with_timezone(date_time, time_zone=None):
    """Function to represent datetime object *date_time* with timezone info.
    If input *date_time* does have tzinfo, and if *time_zone* is defined, convert
    *date_time* to defined timezone, otherwise does nothing.
    If input *date_time* does not have tzinfo, set with defined *time_zone*, no
    changes of date time.

    Parameters
    ----------
    date_time : datetime
        Datetime object.
    time_zone : str
        Name of timezone, default is local time zone, e.g. 'EST',
        see pytz.all_timezones.

    Returns
    -------
    r : datetime
        Datetime object with timezone info.

    Examples
    --------
    >>> from datetime import datetime
    >>> dt0 = datetime.now()  # local timezone datetime, but without tzinfo explicitly define.
    >>> dt0_w_tz = datetime_with_timezone(dt0)
    >>> print(dt0_w_tz.tzinfo.zone)
    'America/New_York'
    >>> dt1 = datetime_with_timezone(dt0_w_tz, time_zone='UTC')  # represent last datetime in UTC zone
    >>> print(dt1.tzinfo.zone)
    'UTC'
    >>> print(dt1.hour - dt0_w_tz.hour) # UTC if ahead of EST by 5 hours
    5
    >>> dt2 = datetime(2020, 11, 10, 1, 12, 3, 456789) # arbitrary datetime but w/o zone
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
        _timezone = pytz.timezone(time_zone)

    if date_time.tzinfo is not None:
        if time_zone is not None:
            _dt1 = date_time.astimezone(_timezone)
            _dt = _timezone.localize(datetime(_dt1.year, _dt1.month, _dt1.day,
                                              _dt1.hour, _dt1.minute, _dt1.second,
                                              _dt1.microsecond))
        else:
            _dt1 = date_time
            _dt = date_time.tzinfo.localize(datetime(
                                              _dt1.year, _dt1.month, _dt1.day,
                                              _dt1.hour, _dt1.minute, _dt1.second,
                                              _dt1.microsecond))
    else:
        _dt1 = date_time
        _dt = _timezone.localize(datetime(_dt1.year, _dt1.month, _dt1.day,
                                          _dt1.hour, _dt1.minute, _dt1.second,
                                          _dt1.microsecond))
    return _dt


def is_dst(date_time):
    """Return if *date_time* is in daylight saving time period.

    Examples
    --------
    >>> from datetime import datetime
    >>>
    >>> t0 = datetime(2016, 11, 2, 12, 34, 56, 123456)  # local time at America/New_York
    >>> print(is_dst(t0))
    True
    >>> print(is_dst(t0.astimezone(pytz.timezone('UTC'))))
    False
    """
    if date_time.tzinfo is None:
        return bool(pytz.timezone(LOCAL_ZONE_NAME).localize(date_time).dst())
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

    is_retro = 'before' in dt
    dt_dict = {}
    dt_tuple = dt.replace('after', '').replace('and', ',').replace('before', ',').strip(' ,').split(',')
    for part in dt_tuple:
        v, k = part.strip().split()
        dt_dict[time_unit_table[k]] = int(v)

    dt = relativedelta.relativedelta(**dt_dict)

    ref_dt_as_utc = datetime_with_timezone(ref_dt, time_zone='UTC')
    if is_retro:
        _datetime_as_utc = ref_dt_as_utc - dt
    else:
        _datetime_as_utc = ref_dt_as_utc + dt
    _datetime = datetime_with_timezone(_datetime_as_utc, time_zone=ref_dt.tzinfo.zone)
    if epoch:
        r = _datetime.timestamp
    else:
        r = _datetime
    return datetime_with_timezone(r)


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

