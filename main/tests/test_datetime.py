# -*- coding: utf-8 -*-
from datetime import datetime
import pytz

from archappl.data import is_dst
from archappl.data import parse_dt
from archappl.data import datetime_with_timezone
from archappl.data.utils import LOCAL_ZONE_NAME


T0_DST = datetime(2016, 11, 5, 23, 0, 0, 0)  # DST
T1_EST = datetime(2016, 11, 6 ,6, 0, 0, 0)


def test_func_datetime_with_timezone():
    """Test `datetime_with_timezone()`.
    """
    tt0 = datetime_with_timezone(T0_DST)
    tt1 = datetime_with_timezone(T1_EST)

    assert tt0.tzinfo.zone == LOCAL_ZONE_NAME
    assert bool(tt0.dst()) == True
    assert bool(tt0.dst()) == is_dst(T0_DST)

    assert tt1.tzinfo.zone == LOCAL_ZONE_NAME
    assert bool(tt1.dst()) == False
    assert bool(tt1.dst()) == is_dst(T1_EST)

    t0_at_utc = datetime_with_timezone(T0_DST, time_zone='UTC')
    assert (tt0 - t0_at_utc).total_seconds() / 3600 == 4.0

    t1_at_utc = datetime_with_timezone(T1_EST, time_zone='UTC')
    assert (tt1 - t1_at_utc).total_seconds() / 3600 == 5.0

    t0_as_utc = datetime_with_timezone(tt0, time_zone='UTC')
    assert (tt0 - t0_as_utc).total_seconds() == 0.0

    t1_as_utc = datetime_with_timezone(tt1, time_zone='UTC')
    assert (tt1 - t1_as_utc).total_seconds() == 0.0


def test_func_is_dst():
    """Test `is_dst()`.
    """
    assert is_dst(T0_DST) == True
    assert is_dst(T1_EST) == False

def test_func_parse_dt1():
    """Test `parse_dt()`.
    """
    dt_str = "after 3 hours"
    tt0 = datetime_with_timezone(T0_DST)
    t0_as_utc = datetime_with_timezone(tt0, time_zone='UTC')
    t0_after_utc = parse_dt(dt_str, t0_as_utc)
    assert (t0_after_utc - t0_as_utc).total_seconds() / 3600 == 3.0

    t0_after_local = parse_dt(dt_str, tt0)
    assert (t0_after_local - tt0).total_seconds() / 3600 == 3.0
    assert (t0_after_local - t0_after_utc).total_seconds() == 0.0

    dt_str = "3 hours before"
    t0_before_utc = parse_dt(dt_str, t0_as_utc)
    assert (t0_before_utc - t0_as_utc).total_seconds() / 3600 == -3.0

    t0_before_local = parse_dt(dt_str, tt0)
    assert (t0_before_local - tt0).total_seconds() / 3600 == -3.0
    assert (t0_before_local - t0_before_utc).total_seconds() == 0.0


def test_func_parse_dt2():
    """Test returned datetime DST or not.
    """
    tt0 = datetime_with_timezone(T0_DST)  # DST
    assert is_dst(tt0) == True
    assert is_dst(T0_DST) == True

    tt0_after_four_hrs = parse_dt("after 4 hours", tt0)
    assert is_dst(tt0_after_four_hrs) == False
    assert (tt0_after_four_hrs - tt0).total_seconds() == 4 * 3600

    assert (datetime_with_timezone(tt0_after_four_hrs, time_zone='UTC') -
            datetime_with_timezone(tt0, time_zone='UTC')).total_seconds() \
            == 4 * 3600
