#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import dateutil.relativedelta as relativedelta
import tzlocal
import pytz

LOCAL_ZONE = tzlocal.get_localzone()
LOCAL_ZONE_NAME = LOCAL_ZONE.zone


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
    If input *date_time* does have tzinfo, and if *time_zone* is defined, convert *date_time* to
    defined timezone, otherwise does nothing.
    If input *date_time* does not have tzinfo, set with defined *time_zone*.

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
    >>> # amend it with 'UTC' zone, only affect tz
    >>> dt2_w_utc = datetime_with_timezone(dt2, time_zone='UTC')
    >>> print(dt2_w_utc)
    2020-11-10 01:12:03.456789+00:00
    """
    if time_zone is None:
        _timezone = LOCAL_ZONE
    else:
        _timezone = pytz.timezone(time_zone)

    if date_time.tzinfo is not None:
        if time_zone is not None:
            _dt = date_time.astimezone(_timezone)
        else:
            _dt = date_time
    else:
        _dt = date_time.replace(tzinfo=_timezone)
    return _dt


# see phantasy.parse_dt
def parse_dt(dt, ref_datetime=None, epoch=None, timezone=None, **kws):
    """Parse delta time defined by *dt*, which is approching plain English,
    e.g. '1 hour and 30 mins ago', return datetime object with tzinfo at *timezone*.

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
        Datetime object, with *timezone* info.
    epoch : bool
        If return date time as seconds since Epoch.
    timezone : str
        Name of time zone, default is local time zone, e.g. 'EST',
        see pytz.all_timezones.

    Keyword Arguments
    -----------------
    align_tz: bool
        If True, returned date time with the tzinfo as reference date time.

    Warning
    -------
    Only support integer number when defining time unit.

    Returns
    -------
    ret : datetime
        Datetime object.

    See Also:
    ---------
    datetime_with_timezone

    Examples
    --------
    >>> dt0 = datetime_with_timezone(datetime.now())
    >>> dt1 = parse_dt("1 hour before", dt0)
    >>> dt2 = parse_dt("after 1 hour", dt0)
    >>> assert dt0 - dt0 == dt2 - dt1
    >>> dt_str = '1 month, 2 weeks, 4 hours, 7 mins and 10 secs before'
    >>> print(parse_dt(dt_str, datetime(2016, 12, 10, 12, 34, 56, 123456))) # local tz EST
    2016-10-27 08:27:46.123456-05:00
    >>> # east daylight saving
    >>> print(parse_dt(dt_str, datetime(2016, 12, 10, 12, 34, 56, 123456), align_tz=True))
    2016-10-27 09:27:46.123456-04:00
    >>>
    """
    if timezone is None:
        tz = LOCAL_ZONE
    else:
        tz = pytz.timezone(timezone)
    if ref_datetime is None:
        timenow = datetime.now(tz=tz)
    elif isinstance(ref_datetime, datetime):
        timenow = ref_datetime.astimezone(tz)
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

    if is_retro:
        _datetime = timenow - dt
    else:
        _datetime = timenow + dt
    if epoch:
        r = _datetime.timestamp
    else:
        r = _datetime
    if kws.get('align_tz', False):
        return r.astimezone(ref_datetime.tzinfo)
    else:
        return r


if __name__ == "__main__":
    s = "2019-03-05T13:04:08.120000-05:00"
    f, tz = iso_to_epoch(s)
    assert f == 1551809048.12
    assert tz == "-05:00"
    assert epoch_to_iso(f, tz) == s

