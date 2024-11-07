# -*- coding: utf-8 -*-

import logging
import requests
import json
from typing import Union
from simplejson import JSONDecodeError
import pandas as pd
from .utils import LOCAL_ZONE_NAME
from .pb import unpack_raw_data

from archappl.config import SITE_DATA_URL, SITE_DATA_FORMAT

_LOGGER = logging.getLogger(__name__)
PAYLOAD_KEYS = ('val', 'status', 'severity')
JSON_HEADERS = {"Content-Type": "application/json"}


class ArchiverDataClient(object):
    """Client for data retrieval.

    Parameters
    ----------
    url : str
        Base url for data retrieval API (including port number if applicable), defaults the one
        defined in config.ini file:
        1. ~/.pyarchappl/config.ini
        2. /etc/pyarchappl/config.ini
        otherwise, fallbacks to one deployed with the package.

    Keyword Arguments
    -----------------
    format : str
        The format of data to request, defaults to `data_format` defined in config file,
        could be 'raw' or 'json'. This option only applies to requests to the server, does not
        alter the format of the returned dataset.
    """
    def __init__(self, url: Union[str, None] = None, **kws):
        self._url_config = [SITE_DATA_URL , '/retrieval/data/getData.', SITE_DATA_FORMAT]
        self.url = url
        self.format = kws.get('format', None)
        _LOGGER.debug(f"URL of data client is: {self.url}")
        _LOGGER.debug(f"Data request in the format of '{self.format}'")

    @property
    def format(self):
        """str : Define how the data returned from the request, in 'json' or 'raw'.
        """
        return self._url_config[2]

    @format.setter
    def format(self, fmt: Union[str, None]):
        if fmt is None:
            self._url_config[2] = SITE_DATA_FORMAT
        else:
            self._url_config[2] = fmt.lower()

    @property
    def url(self):
        return ''.join(self._url_config)

    @url.setter
    def url(self, url: Union[str, None]):
        if url is None:
            self._url_config[0] = SITE_DATA_URL
        else:
            self._url_config[0] = url

    def get_data_at_time(self, pv_list, at_time):
        """Get data at timestamp defined by *at_time* for list of PVs defined
        by *pv_list*.
        """
        p = ['at={}'.format(at_time)]
        url = self.url.rsplit('/', 1)[0] + '/getDataAtTime' \
              + '?' + '&'.join(p)
        r = requests.post(url, data=json.dumps(pv_list),
                          headers=JSON_HEADERS)
        try:
            ret = r.json()
            assert ret != {}
        except JSONDecodeError:
            ret = None
        except AssertionError:
            ret = None
        finally:
            return ret

    def get_data(self, pv: str, **kws) -> Union[pd.DataFrame, None]:
        """Retrieve data from Archive Appliance as a `pandas.DataFrame`.

        Parameters
        ----------
        pv : str
            A string of PV name.

        Keyword Arguments
        -----------------
        from_time : str
            A string of start time of the dataset in ISO8601 format.
        to_time : str
            A string of end time of the dataset in ISO8601 format.
        tz : str
            The timezone name for the returned dataframe index, defaults to the local zone.
        last_n : int
            Limit the number of data rows to the defined integer, defaults to 0, return all.

        Returns
        -------
        r : pd.DataFrame
            A pandas dataframe with the timestamp as the index.
        """
        from_time = kws.get('from_time', None)
        to_time = kws.get('to_time', None)
        last_n = kws.get('last_n', 0)
        tz = kws.get('tz', LOCAL_ZONE_NAME)
        p = ['pv={}'.format(pv)]
        if from_time is not None:
            p.append('from={}'.format(from_time))
        if to_time is not None:
            p.append('to={}'.format(to_time))

        url = self.url + '?' + '&'.join(p)

        r = requests.get(url)
        if not r.ok:
            _LOGGER.error(f"Fetched data error: {r.status_code}")
            return None
        if self.format == 'raw':
            return normalize(unpack_raw_data(r.content), tz, last_n=last_n)
        else:  # json
            try:
                data_ = r.json()
            except JSONDecodeError:
                return None
            else:
                return normalize(data_, tz, last_n=last_n)

    def __repr__(self):
        return f"[({self.format}) Data Client] hooked to Archiver Appliance at: {self._url_config[0]}"


def normalize(data: list[dict], tz: str = 'UTC', **kws) -> Union[pd.DataFrame, None]:
    """Normalize data as pandas.DataFrame.

    Parameters
    ----------
    data : list
        A list of dict of data returned from the data client.
    tz : str
        String of timezone, e.g. 'US/Eastern', see also: `pytz.all_timezones`.
    last_n : int
        Limit the number of data rows to the defined integer, defaults to 0, return all.

    Returns
    -------
    r : pd.DataFrame
        A pandas dataframe with timestamp as the index, 'val', 'status', 'severity' as columns.
    """
    if len(data) == 0:
        _LOGGER.warning("Hit empty data, return None.")
        return None
    meta = data[0]['meta']
    payloads = data[0]['data']
    if not payloads:
        _LOGGER.warning("Hit empty payloads, return None.")
        return None

    last_n = kws.get('last_n', 0)
    other_val_keys = PAYLOAD_KEYS
    ts_list = []
    other_val_dict = dict()

    for d in payloads[-last_n:]:
        ts_list.append(int((d['secs'] + d['nanos'] / 1e9) * 1e3))
        for k in other_val_keys:
            other_val_dict.setdefault(k, []).append(d[k])

    df = pd.DataFrame.from_dict(other_val_dict)
    df['time'] = ts_list
    df.set_index('time', inplace=True)

    idx_utc = pd.to_datetime(df.index, unit='ms').tz_localize('UTC')
    if tz != 'UTC':
        df.index = idx_utc.tz_convert(tz)
        _LOGGER.debug(f"Converted timezone from UTC to {tz}")
    else:
        df.index = idx_utc
    return df


if __name__ == '__main__':
    a = ArchiverDataClient()
    print(a)
    print(a.url)

    #a.format = 'txt'
    #print(a.url)

    data = a.get_data(pv='TST:gaussianNoise')
    #print(a.get_data(pv='TST:gaussianNoise', ts_from='a', ts_to='d'))
    import matplotlib.pyplot as plt
    data.plot()
    plt.show()
