#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime


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


if __name__ == "__main__":
    s = "2019-03-05T13:04:08.120000-05:00"
    f, tz = iso_to_epoch(s)
    assert f == 1551809048.12
    assert tz == "-05:00"
    assert epoch_to_iso(f, tz) == s

