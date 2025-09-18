# -*- coding: utf-8 -*-

import requests
import pandas as pd
from typing import Union
from types import SimpleNamespace

from archappl.config import SITE_ADMIN_URL


class ArchiverMgmtClient(object):
    """Management client for Archiver Appliance.

    Parameters
    ----------
    url : str
        Base url of BPL, defaults the one defined in config.ini file:
        1. ~/.pyarchappl/config.ini
        2. /etc/pyarchappl/config.ini
        otherwise, fallbacks to one deployed with the package.
    """
    def __init__(self, url: Union[str, None] = None):
        self._url_config = [SITE_ADMIN_URL, '/mgmt/bpl']
        self.url = url

    @property
    def url(self):
        """str: URL of archiver appliance (management).
        """
        return ''.join(self._url_config)

    @url.setter
    def url(self, url: Union[str, None]):
        if url is None:
            self._url_config[0] = SITE_ADMIN_URL
        else:
            self._url_config[0] = url

    def get_appliance_info(self):
        """Get the appliance information for the specified appliance.
        """
        url = self.url + '/getApplianceInfo'
        return requests.get(url).json()

    def get_all_pvs(self, pv: str, limit: int = 10, **kws):
        """Get the PVs in the cluster, return empty list if not being archived.

        Parameters
        ----------
        pv : str
            Only return PVs matched `pv` pattern (unix wildcard).
        limit : int
            Length of returned list of PVs, default is 10.

        Keyword Arguments
        -----------------
        expanded : bool
            If true, return ALL PV with all fields, caution it may return a huge amount data.

        Returns
        -------
        r : list[str]
            A list of PV names
        """
        if kws.pop("expanded", False):
            url = self.url + '/getAllExpandedPVNames'
        else:
            url = self.url + '/getAllPVs'
        kws.update({'pv': pv, 'limit': limit})
        return requests.get(url + _make_params(kws)).json()

    def get_pv_status(self, pv: Union[str, list[str]], **kws) -> dict[str, SimpleNamespace]:
        """Get the status of a PV.

        Parameters
        ----------
        pv : list[str], str
            A PV name or String pattern (unix wildcard) or a list of PV names/patterns.

        Returns
        -------
        r : dict[str, SimpleNamespace]
            A dict of PV status, PV names as the keys.
        """
        url = self.url + '/getPVStatus'
        if isinstance(pv, str):
            kws.update({'pv': pv})
            r = requests.get(url + _make_params(kws)).json()
            return {i['pvName']: SimpleNamespace(**i) for i in r}
        else:  # a list of pv string patterns
            pv_status: dict = {}
            for _pv in pv:
                _kws = {k: v for k, v in kws.items()}
                _kws.update({'pv': _pv})
                r = requests.get(url + _make_params(_kws)).json()
                pv_status.update({i['pvName']: SimpleNamespace(**i) for i in r})
            return pv_status

    def get_pv_type_info(self, pv: str) -> Union[SimpleNamespace, None]:
        """Get the type info for a given PV.

        In the archiver appliance terminology, the *PVTypeInfo* contains the
        various archiving parameters for a PV.

        Parameters
        ----------
        pv : str
            A PV name.

        Returns
        -------
        r : SimpleNamespace or None
            PV type info or None.
        """
        url = self.url + '/getPVTypeInfo'
        r = requests.get(url + '?pv={}'.format(pv))
        if r.ok:
            return SimpleNamespace(**r.json())
        else:
            return None

    def get_pv_details(self, pv: str) -> Union[pd.DataFrame, None]:
        """ Get the details of a PV.

        Parameters
        ----------
        pv : str
            A PV name.

        Returns
        -------
        r : pd.DataFrame or None
            PV details or None.
        """
        url = self.url + '/getPVDetails'
        r = requests.get(url + '?pv={}'.format(pv))
        if r.ok:
            return pd.DataFrame.from_records(r.json(), index=['source', 'name'])
        else:
            return None

    def archive_pv(self, pv: str, op: str = None, **kws):
        """Archive operations for one PV.

        Note that it supports archive multiple PVs through a single API request, but
        here we do not explicitly do that.

        Parameters
        ----------
        pv : str
            One PV name to be operated.
        op : str
            Specific archive operation:
            * 'archive' (default): start to archive.
            * 'pause': pause archiving.
            * 'resume': resume archiving.
            * 'abort': abort archiving.
            * 'update': change archiving configuration.

        Keyword Arguments
        -----------------
        `archive`
            samplingperiod:
                The sampling period to be used. Optional, default value is
                1.0 seconds.
            samplingmethod:
                The sampling method to be used. For now, this is one of SCAN
                or MONITOR. Optional, default value is MONITOR.
            controllingPV:
                The controlling PV for conditional archiving. Optional;
                if unspecified, we do not use conditional archiving.
            policy:
                Override the policy execution process and use this policy
                instead. Optional; if unspecified, we go thru the normal
                policy execution process.
            appliance:
                If specified (value is the identity of the appliance),
                the sampling and archiving are done on the specified appliance.
        `update`
            samplingmethod, samplingperiod
        """
        kparams = {'pv': pv}
        url = self.url + '/archivePV'
        if op is None:
            kparams.update(kws)
        elif op == 'pause':
            url = self.url + '/pauseArchivingPV'
        elif op == 'resume':
            url = self.url + '/resumeArchivingPV'
        elif op == 'abort':
            url = self.url + '/abortArchivingPV'
        elif op == 'update':
            url = self.url + '/changeArchivalParameters'
            kparams.update(kws)
        return requests.get(url + _make_params(kparams)).json()

    def get_stores_for_pv(self, pv: str) -> Union[list, None]:
        """ Gets the names of the data stores for this PV.

        Parameters
        ----------
        pv : str
            A PV name.

        Returns
        -------
        r : list or None
            A list of data stores or None.
        """
        url = self.url + '/getStoresForPV'
        r = requests.get(url + '?pv={}'.format(pv))
        if r.ok:
            return r.json()
        else:
            return None

    # def delete_pv(self, pv, delete_data=False):
    #     """ Stop archiving the specified PV. The PV needs to be paused first.
    #     """
    #     url = self.url + '/deletePV'
    #     return requests.get(url + _make_params({'deleteData': delete_data, 'pv': pv})).json()

    def __repr__(self):
        return "[Admin Client] Archiver Appliance on: {url}".format(url=self.url)


def _make_params(d: dict):
    p = ['{k}={v}'.format(k=k, v=v) for k,v in d.items()
            if v is not None]
    if p:
        return '?' + '&'.join(p)
    else:
        return ''


if __name__ == '__main__':
    a = ArchiverMgmtClient()
    assert str(a) == '[Admin Client] Archiver Appliance on: http://127.0.0.1:17665/mgmt/bpl'
    # URL
    assert a.url == 'http://127.0.0.1:17665/mgmt/bpl'

    # get appliance info
    print(a.get_appliance_info())

    # get all pvs
    print(a.get_all_pvs())
    print(a.get_all_pvs(pv='*fake*'))
    print(a.get_all_pvs(pv='*aussian*', limit=1))

    # get pv status
    print(a.get_pv_status())

    # get pv type info
    print(a.get_pv_type_info(pv='TST:gaussianNoise'))

