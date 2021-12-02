# -*- coding: utf-8 -*-

import logging
import requests
import json
from simplejson import JSONDecodeError
import pandas as pd
from .utils import LOCAL_ZONE_NAME
from .pb import unpack_raw_data

_LOGGER = logging.getLogger(__name__)

PAYLOAD_KEYS = ('val', 'status', 'severity')

URL_DEFAULT = 'http://127.0.0.1:17665'
JSON_HEADERS = {"Content-Type": "application/json"}
DEFAULT_FMT = 'raw'


class ArchiverDataClient(object):
    """Client for data retrieval.

    Parameters
    ----------
    url : str
        Base url for data retrieval API (including port number if needed), default
        is 'http://127.0.0.1:17665'.

    Keyword Arguments
    -----------------
    format : str
        The format of data to request, default is 'raw', could be 'json' as well,
        this option only applies to the server side, does not alter the format of
        the returned dataset.
    """
    def __init__(self, url=None, **kws):
        self._url_config = [URL_DEFAULT, '/retrieval/data/getData.', DEFAULT_FMT]
        self.url = url
        self.format = kws.get('format', None)
        _LOGGER.debug(f"URL of data client is: {self.url}")
        _LOGGER.debug(f"Data request in the format of '{self.format}'")

    @property
    def format(self):
        """JSON, RAW.
        """
        return self._url_config[2]

    @format.setter
    def format(self, fmt=None):
        if fmt is None:
            self._url_config[2] = DEFAULT_FMT
        else:
            self._url_config[2] = fmt.lower()

    @property
    def url(self):
        return ''.join(self._url_config)

    @url.setter
    def url(self, url):
        if url is None:
            self._url_config[0] = URL_DEFAULT
        else:
            self._url_config[0] = url

    def get_data_at_time(self, pv_list, at_time):
        """Get data at timestampe defined by *at_time* for list of PVs defined
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

    def get_data(self, pv, **kws):
        """Retrieve data from Archive Appliance, return as `pandas.DataFrame`.

        Parameters
        ----------
        pv : str
            PV name.

        Keyword Arguments
        -----------------
        from_time : str
            A string of start time of the data in ISO8601 format.
        to_time : str
            A string of end time of the data in ISO8601 format.
        tz : str
            Name of timezone for the returned index, default is local zone.

        Returns
        -------
        r : DataFrame
            Dataframe with the index of timestamp.
        """
        ifrom = kws.get('from_time', None)
        ito = kws.get('to_time', None)
        tz = kws.get('tz', LOCAL_ZONE_NAME)
        p = ['pv={}'.format(pv)]
        if ifrom is not None:
            p.append('from={}'.format(ifrom))
        if ito is not None:
            p.append('to={}'.format(ito))

        url = self.url + '?' + '&'.join(p)

        r = requests.get(url)
        if not r.ok:
            _LOGGER.error(f"Failed to get data, error code {r.status_code}")
            return None
        if self.format == 'raw':
            data = unpack_raw_data(r.content)
            return normalize(data, tz)
        elif self.format == 'json':
            try:
                data = r.json()
            except JSONDecodeError:
                return None
            else:
                return normalize(data, tz)
        else:
            _LOGGER.warning("Unsupported data foramt")
            data = r.text
            return data

    def __repr__(self):
        return f"[({self.format}) Data Client] hooked to Archiver Appliance at: {self._url_config[0]}"


def normalize(data, tz='UTC'):
    """Normalize data as pandas.DataFrame.

    Parameters
    ----------
    data : list
        List of dict from data client.
    tz : str
        String of timezone, e.g. 'US/Eastern', see also: `pytz.all_timezones`.

    Returns
    -------
    r : DataFrame
        Pandas dataframe object.
    """
    meta = data[0]['meta']
    payloads = data[0]['data']
    if not payloads:
        _LOGGER.warning("Hit empty payloads, return None.")
        return None

    payload0 = payloads[0]
    other_val_keys = PAYLOAD_KEYS #[k for k in payload0 if k not in ('secs', 'nanos')]
    ts_list = []
    val_list = []
    other_val_dict = dict()

    for d in payloads:
        ts_list.append(int((d['secs'] + d['nanos']/1e9)*1e3))
        for k in other_val_keys:
            other_val_dict.setdefault(k, []).append(d[k])

    df = pd.DataFrame()
    df['time'] = ts_list
    df.set_index('time', inplace=True)
    for k in other_val_keys:
        df[k] = other_val_dict[k]

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
