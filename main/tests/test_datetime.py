# -*- coding: utf-8 -*-
from datetime import datetime

from archappl.data import is_dst
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
    assert tt1.tzinfo.zone == LOCAL_ZONE_NAME
    assert bool(tt1.dst()) == False



def test_func_is_dst():
    """Test `is_dst()`.
    """
    assert is_dst(T0_DST) == True
    assert is_dst(T1_EST) == False


