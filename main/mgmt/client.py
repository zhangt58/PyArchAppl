# -*- coding: utf-8 -*-

import requests
import json


URL_DEFAULT = 'http://127.0.0.1:17665'


class ArchiverMgmtClient(object):
    """Management client for Archiver Appliance.

    Parameters
    ----------
    url : str
        Base url of BPL, default is `http://127.0.0.1:17665`,
    """
    def __init__(self, url=None):
        self._url_config = [URL_DEFAULT, '/mgmt/bpl']
        self.url = url

    @property
    def url(self):
        """URL of archiver appliance (management).
        """
        return ''.join(self._url_config)
    
    @url.setter
    def url(self, url):
        if url is None:
            self._url_config[0] = URL_DEFAULT
        else:
            self._url_config[0] = url

    def get_appliance_info(self):
        """Get the appliance information for the specified appliance.
        """
        url = self.url + '/getApplianceInfo'
        return requests.get(url).json()
    
    def get_all_pvs(self, expanded=False, **kws):
        """Get all the PVs in the cluster.

        Parameters
        ----------
        expanded : bool
            If true, return PV with all fields.

        Keyword Arguments
        -----------------
        pv : str
            Only return PVs matched `pv` pattern.
        limit : int
            Length of returned list of PVs.
        """
        if expanded:
            url = self.url + '/getAllExpandedPVNames'
        else:
            url = self.url + '/getAllPVs' 
        return requests.get(url + _make_params(kws)).json()

    def get_pv_status(self, **kws):
        """Get the status of a PV.
        """
        url = self.url + '/getPVStatus' 
        return requests.get(url + _make_params(kws)).json()

    def get_pv_type_info(self, pv):
        """Get the type info for a given PV.
        
        In the archiver appliance terminology, the *PVTypeInfo* contains the
        various archiving parameters for a PV.
        """
        url = self.url + '/getPVTypeInfo' 
        return requests.get(url + '?pv={}'.format(pv)).json()

    def archive_pv(self, pv, op=None, **kws):
        """Archive operations for one or more PVs.

        Parameters
        ----------
        pv : str or List(str)
            Name of PVs (list) to be operated.
        op : str
            Specific archive operation:
            * 'archive' (default): start to archive.
            * 'pause': pause archiving.
            * 'resume': resume archiving.
            * 'abort': abort arhiving.
            * 'update': change archiving configuration.

        Keyword Arguments
        -----------------
        :archive:
            samplingperiod:
                The sampling period to be used. Optional, default value is
                1.0 seconds.
            samplingmethod:
                The sampling method to be used. For now, this is one of SCAN
                or MONITOR. Optional, default value is MONITOR.
            controllingPV:
                The controlling PV for coditional archiving. Optional;
                if unspecified, we do not use conditional archiving.
            policy:
                Override the policy execution process and use this policy
                instead. Optional; if unspecified, we go thru the normal
                policy execution process.
            appliance:
                If specified (value is the identity of the appliance),
                the sampling and archiving are done on the specified appliance.
        :update:
            samplingmethod, samplingperiod
        """
        kparams = {'pv': pv}
        if op is None:
            url = self.url + '/archivePV'
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

    def get_stores_for_pv(self, pv):
        """ Gets the names of the data stores for this PV.
        """
        url = self.url + '/getStoresForPV' 
        return requests.get(url + '?pv={}'.format(pv)).json()

    def delete_pv(self, pv, delete_data=False):
        """ Stop archiving the specified PV. The PV needs to be paused first.
        """
        url = self.url + '/deletePV' 
        return requests.get(url + _make_params({'deleteData': delete_data, 'pv': pv})).json()

    def __repr__(self):
        return "[Admin Client] Archiver Appliance on: {url}".format(url=self.url)


def _make_params(d):
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

