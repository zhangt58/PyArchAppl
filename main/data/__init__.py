from .client import ArchiverDataClient
from .utils import iso_to_epoch
from .utils import epoch_to_iso
from .utils import parse_dt
from .utils import datetime_with_timezone
from .utils import is_dst
from .utils import standardize_datetime
from .utils import printlog

def dformat(*args, **kws):
    """Return ISO8601 format of date time.

    Input up to 7 arguments as year, month, day, hour, minute, second,
    millisecond, it is recommended always input year, month, day, hour,
    minute, second and millisecond as 0 if not input.
    """
    _, tstr = standardize_datetime(args, **kws)
    return tstr


def dformat_(*args, **kws):
    """Return datetime object based on the input datatime tuple.
    """
    t, _ = standardize_datetime(args, **kws)
    return t


FRIBArchiverDataClient = ArchiverDataClient(
    "http://epicsarchiver1.ftc:17668")

ReAArchiverDataClient = ArchiverDataClient(
    "http://rea-epicsarch.frib.msu.edu")


__all__ = [
    "iso_to_epoch", "epoch_to_iso",
    "parse_dt",
    "datetime_with_timezone",
    "is_dst",
    "standardize_datetime",
    "dformat", "dformat_",
    "printlog"
]
