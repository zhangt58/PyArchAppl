# -*- coding: utf-8 -*-

from datetime import datetime
import time
import pandas as pd
from archappl.client import FRIBArchiverDataClient
from archappl.data.utils import LOCAL_ZONE_NAME
from archappl import printlog
from archappl import TQDM_INSTALLED


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


def _get_data_at_time(pv_list, at_time, client=None):
    if client is None:
        client = FRIBArchiverDataClient
    data = client.get_data_at_time(pv_list, at_time)
    if data == {} or data is None:
        return None
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
    if verbose != 0 and TQDM_INSTALLED:
        from archappl import tqdm
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
    tz : str
        Name of timezone for the returned index, default is local zone.

    Returns
    -------
    r : dataframe
        Pandas dataframe.
    """
    client = kws.pop('client', None)
    tz = kws.pop('tz', LOCAL_ZONE_NAME)
    data_ = _get_data_at_time(pv_list, at_time, client)
    return _to_df(data_, tz=tz, **kws)


def get_dataset_at_time_with_devices(element_list, field_list, at_time, **kws):
    """Pull data from Archiver Appliance, with a given list of devices and dynamic fields at a
    specified time.

    Parameters
    ----------
    element_list : list
        A list of high-level device element objects.
    field_list : list
        A list of field names should applied to all elements, otherwise skip invalid field which
        does not belong to some element.
    at_time : str
        A string of time of the data in ISO8601 format.

    Keyword Arguments
    -----------------
    client : ArchiverDataClient
        ArchiverDataClient instance, default is FRIBArchiverDataClient.
    handle : str
        PV handle for field list, by default is 'readback', other options: 'setpoint'.
    tz : str
        Name of timezone for the returned index, default is local zone.

    Returns
    -------
    r : dataframe
        Pandas dataframe.
    """
    handle = kws.pop('handle', 'readback')
    all_pv_list = []
    pv_list_per_element = []
    field_list_per_element = []
    elem_list = []

    for i in element_list:
        _pv_list = []
        _field_list = []
        for f in field_list:
            if f not in i.fields:
                continue
            _field_list.append(f)
            field_pv_list_ = i.pv(field=f, handle=handle)
            _pv_list.append(field_pv_list_)
            all_pv_list.extend(field_pv_list_)
        if _field_list == []:
            continue
        elem_list.append(i)
        pv_list_per_element.append(_pv_list)
        field_list_per_element.append(_field_list)

    client = kws.pop('client', None)
    tz = kws.pop('tz', LOCAL_ZONE_NAME)
    data_ = _get_data_at_time(all_pv_list, at_time, client)
    pv_val_dict = {k: v['val'] for k, v in data_.items()}
    fval_list = []  # list of element with field values
    for elem_, pv_list_, field_list_  in zip(elem_list, pv_list_per_element, field_list_per_element):
        ename = elem_.name
        etype = elem_.family
        epos = elem_.sb
        for fname, ipv_tuple in zip(field_list_, pv_list_):
            if ipv_tuple[0] not in data_:
                continue
            v = data_[ipv_tuple[0]]
            ms = int((v['secs'] + v['nanos'] / 1e9) * 1e3)
            vset = elem_.get_settings(fname, pv_val_dict)
            fval_list.append((ename, fname, etype, epos, vset, ms))
    df = _to_df_sm(fval_list, tz=tz, **kws)
    return df


def _get_ion_info(t):
    # to be tested
    pv_ion_mass = "FE_ISRC1:BEAM:A_BOOK"
    pv_ion_charge = "FE_ISRC1:BEAM:Q_BOOK"
    pv_ion_number = "FE_ISRC1:BEAM:Z_BOOK"
    pv_ion_name = "FE_ISRC1:BEAM:ELMT_BOOK"
    pv_list = [pv_ion_mass, pv_ion_charge, pv_ion_number, pv_ion_name]
    return get_dataset_at_time_with_pvs(pv_list, t, client=FRIBArchiverDataClient)


def export_as_settings_manager_datafile(df, filepath, **kws):
    """Export dataframe as the datafile for Settings Manager.

    Parameters
    ----------
    df : dataframe
        Data of device settings.
    filepath : str
        Full path of exported data file.

    Keyword Arguments
    -----------------
    note : str
        Note string.
    tags : str
        Tags string.
    machine : str
        Name of machine, default is 'FRIB'.
    segment : str
        Name of segment, default is 'LINAC'.
    ion_name : str
        Name of ion, default is 'NAN'.
    ion_number: int
        Ion number, default is 0.
    ion_mass : int
        Ion mass, default is 0.
    ion_charge : int
        Ion charge, default is 0.

    See Also
    --------
    get_dataset_at_time_with_devices, get_dataset_at_time

    """
    from getpass import getuser
    from phantasy_apps.settings_manager import __version__
    nrow = df.shape[0]
    for k in ('Readback', 'Last Setpoint'):
        df[k] = ['nan'] * nrow
    df['Tolerance'] = [0.1] * nrow
    df['Writable'] = ['True'] * nrow
    _user = getuser()
    _timestamp = df['time'].astype('int64').mean() / 1e9
    _datetime = datetime.fromtimestamp(_timestamp).isoformat() # df['time'].mean().isoformat()
    _note = kws.get('note', 'Retrieved from Archiver')
    _tags = kws.get('tags', '')
    _machine = kws.get('machine', 'FRIB')
    _segment = kws.get('segment', 'LINAC')
    _ion_name = kws.get('ion_name', 'NAN')
    _ion_num = kws.get('ion_number', 0)
    _ion_mass = kws.get('ion_mass', 0)
    _ion_charge = kws.get('ion_charge', 0)

    ks = ('timestamp', 'datetime', 'note', 'filepath', 'user',
          'ion_name', 'ion_number', 'ion_mass', 'ion_charge',
          'machine', 'segment', 'tags', 'app', 'version')
    vs = (_timestamp, _datetime, _note, filepath, _user,
          _ion_name, _ion_num, _ion_mass, _ion_charge,
          _machine, _segment, _tags, 'Settings Manager', __version__)
    df1 = df.drop(columns=['time'])
    with open(filepath, 'w') as fp:
        for k, v in zip(ks, vs):
            fp.write(f"# {k}: {v}\n")
        df1.to_csv(fp, index=False)


def _to_df_sm(dat, tz='UTC'):
    # dataframrize a list of data with ts for Settings Manager
    df = pd.DataFrame(columns=['Name', 'Field', 'Type', 'Pos', 'Setpoint'])
    ms_list = []
    for i, (ename, fname, etype, pos, val, ms) in enumerate(dat):
        ms_list.append(ms)
        df.loc[i] = [ename, fname, etype, pos, val]
    ts_utc = pd.to_datetime(ms_list, unit='ms').tz_localize('UTC')
    if tz != 'UTC':
        df['time'] = ts_utc.tz_convert(tz)
    else:
        df['time'] = ts_utc
    return df


def _to_df(dat, tz='UTC'):
    # dataframrize dat (dict of {pv:{payload}}) from get_data_at_time().
    df = pd.DataFrame(columns=['PV', 'val', 'status', 'severity'])
    ms_list = []
    for i, (k, v) in enumerate(dat.items()):
        ms_list.append(int((v['secs'] + v['nanos'] / 1e9) * 1e3))
        df.loc[i] = [k, v['val'], v['status'], v['severity']]
    idx_utc = pd.to_datetime(ms_list, unit='ms').tz_localize('UTC')
    if tz != 'UTC':
        df['time'] = idx_utc.tz_convert(tz)
    else:
        df['time'] = idx_utc
    return df


def read_csv(filepath, parse_dates=['time'], index_col='time', **kws):
    return pd.read_csv(filepath, parse_dates=parse_dates, index_col=index_col, **kws)
