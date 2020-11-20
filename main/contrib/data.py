# -*- coding: utf-8 -*-


from archappl.client import FRIBArchiverDataClient
import time
from archappl import tqdm
from archappl import printlog


def _get_data(pv, from_time, to_time, client=None):
    if client is None:
        client = FRIBArchiverDataClient
    data = client.get_data(pv,
                           from_time=from_time,
                           to_time=to_time)
    if len(data.iloc[:, 0]) == 1:
        return None
    data.drop(columns=['severity', 'status'], inplace=True)
    data.rename(columns={'val': pv}, inplace=True)
    return data


def get_dataset_with_pvs(pv_list, from_time, to_time, **kws):
    """Pull data from Archiver Appliance, with a given list of PVs, within defined time slot.

    Parameters
    ----------
    pv_list : list
        A list of process variables.
    from_time : str
        A string of start time of the data in ISO8601 format.
    to_time : str
        A string of end time of the data in ISO8601 format.

    Keyword Arguments
    -----------------
    client : ArchiverDataClient
        ArchiverDataClient instance, default is FRIBArchiverDataClient.
    resample : str
        The offset string or object representing target conversion, e.g. resample with 1 second
        offset could be defined as '1S'.
    verbose : int
        Verbosity level of the log output, default is 0, no output, 1, output progress, 2 output
        progress with description.

    Returns
    -------
    r : dataframe
        Pandas dataframe with datetime as the index, and device PV names as columns

    See Also
    --------
    archappl.dformat

    Examples
    --------
    >>> from archappl.client import ArchiverDataClient
    >>> data_client = ArchiverDataClient()
    >>> data_client.url = "http://127.0.0.1:17665"
    >>>
    >>> from archappl import dformat
    >>> t0 = dformat(2020, 11, 16, 15, 10)
    >>> t1 = dformat(2020, 11, 16, 16, 17)
    >>>
    >>> pv_list = ['VA:LS1_CA01:BPM_D1129:X_RD', 'VA:LS1_CA01:BPM_D1129:Y_RD',
                   'VA:LS1_CA01:BPM_D1144:X_RD', 'VA:LS1_CA01:BPM_D1144:Y_RD']
    >>> data_set = get_dataset_with_pvs(pv_list, t0, t1,
                                        resample="1S", verbose=2,
                                        client=data_client)
    """
    t0 = time.time()
    client = kws.pop('client', None)
    resample = kws.pop('resample', None)
    verbose = kws.pop('verbose', 0)
    df_list = []
    if verbose != 0:
        pbar = tqdm(pv_list)
    else:
        pbar = pv_list
    for pv in pbar:
            data_ = _get_data(pv, from_time, to_time, client=client)
            if data_ is None:
                if verbose > 1:
                    pbar.set_description(f"Skip {pv}")
                continue
            df_list.append(data_)
            if verbose > 1:
                pbar.set_description(f"Fetched {pv}")
    data = df_list[0].join(df_list[1:], how='outer')
    data.fillna(method='ffill', inplace=True)
    if resample is not None:
        data = data.resample(resample).ffill()
        data.dropna(inplace=True)
    if verbose > 0:
        printlog(f"Fetched all, time cost: {time.time() - t0:.1f} seconds.")
    return data


def get_dataset_with_devices(element_list, field_list, from_time, to_time, **kws):
    """Pull data from Archiver Appliance, with a given list of devices and dynamic fields,
    within defined time slot.

    Parameters
    ----------
    element_list : list
        A list of high-level device element objects.
    field_list : list
        A list of field names should applied to all elements, otherwise skip invalid field which
        does not belong to some element.
    from_time : str
        A string of start time of the data in ISO8601 format.
    to_time : str
        A string of end time of the data in ISO8601 format.

    Keyword Arguments
    -----------------
    client : ArchiverDataClient
        ArchiverDataClient instance, default is FRIBArchiverDataClient.
    resample : str
        The offset string or object representing target conversion, e.g. resample with 1 second
        offset could be defined as '1S'.
    verbose : int
        Verbosity level of the log output, default is 0, no output, 1, output progress, 2 output
        progress with description.
    handle : str
        PV handle for field list, by default is 'readback', other options: 'setpoint'.

    Returns
    -------
    r : dataframe
        Pandas dataframe with datetime as the index, and device PV names as columns

    See Also
    --------
    get_dataset
    phantasy.CaElement, phantasy.CaField
    archappl.dformat

    Examples
    --------
    >>> from archappl.client import ArchiverDataClient
    >>> data_client = ArchiverDataClient()
    >>> data_client.url = "http://127.0.0.1:17665"
    >>>
    >>> from phantasy import MachinePortal
    >>> mp = MachinePortal("FRIB_VA", "LS1FS1")
    >>> bpms = mp.get_elements(type="BPM")

    >>> from archappl import dformat
    >>> t0 = dformat(2020, 11, 16, 15, 10)
    >>> t1 = dformat(2020, 11, 16, 16, 17)
    >>> field_list = ['X', 'Y']
    >>> data_set = get_dataset_with_devices(bpms, field_list, t0, t1,
                                            resample="1S", verbose=2,
                                            client=data_client)
    """
    handle = kws.pop('handle', 'readback')
    pv_list = [i.pv(field=f, handle=handle)[0] for i in element_list
                for f in field_list if i.pv(field=f, handle=handle) != []]
    return get_dataset_with_pvs(pv_list, from_time, to_time, **kws)


def get_dataset_at_time_with_pvs(pv_list, at_time, **kws):
    """Pull data from Archiver Appliance, with a given list of PVs at a specified time.

    Parameters
    ----------
    pv_list : list
        A list of process variables.
    at_time : str
        A string of time of the data in ISO8601 format.

    Keyword Arguments
    -----------------
    client : ArchiverDataClient
        ArchiverDataClient instance, default is FRIBArchiverDataClient.
    verbose : int
        Verbosity level of the log output, default is 0, no output, 1, output progress, 2 output
        progress with description.

    Returns
    -------
    r : dataframe
        Pandas dataframe.
    """
    client = kws.pop('client', None)
