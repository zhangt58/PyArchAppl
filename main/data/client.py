# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd


URL_DEFAULT = 'http://127.0.0.1:17665'

class ArchiverDataClient(object):
    """Client for data retrieval.

    Parameters
    ----------
    url : str
        Base url for data retrieval API, default is 'http://127.0.0.1:17665'.
    """
    def __init__(self, url=None):
        self._url_config = [URL_DEFAULT, '/retrieval/data/getData.', 'json']
        self.url = url

    @property
    def format(self):
        """CSV, MAT, SVG, JSON, TXT, RAW.
        """
        return self._url_config[2]

    @format.setter
    def format(self, fmt):
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
        
    def get_data(self, pv, **kws):
        """Retrieve data from Archive Appliance, return as `pandas.DataFrame`.

        Parameters
        ----------
        pv : str
            PV name.

        Keyword Arguments
        -----------------
        ifrom : str
            Starting date time to retrieve.
        to : str
            End data time.
        """
        ifrom = kws.get('ifrom', None)
        ito = kws.get('to', None)
        p = ['pv={}'.format(pv)]
        if ifrom is not None:
            p.append('from={}'.format(ifrom))
        if ito is not None:
            p.append('to={}'.format(ito))
        url = self.url + '?' + '&'.join(p)

        r = requests.get(url)
        if self.format == 'json':
            data = r.json()
        else:
            data = r.text

        return _normalize(data)
    
    def __repr__(self):
        return "[Data Client] Archiver Appliance on: {url}".format(url=self.url)


def _normalize(data):
    """Normalize data as pandas.DataFrame.
    """
    d_data = data[0]['data']
    val_ks = [k for k in d_data[0] if k not in ('secs', 'nanos')]

    df = pd.DataFrame()
    
    df['ts'] = [d['secs'] + d['nanos']/1e9 for d in d_data]
    df = df.set_index('ts')
    for k in val_ks:
        df[k] = [d[k] for d in d_data]

    idx = pd.to_datetime(df.index, unit='s').tz_localize('UTC').tz_convert('US/Eastern')
    df.index = idx
    return df


if __name__ == '__main__':
    a = ArchiverDataClient()
    print(a)
    print(a.url)

    #a.format = 'txt'
    #print(a.url)

    data = a.get_data(pv='TST:gaussianNoise')
    #print(a.get_data(pv='TST:gaussianNoise', ifrom='a', to='d'))
    import matplotlib.pyplot as plt
    data.plot()
    plt.show()
