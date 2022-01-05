# -*- coding: utf-8 -*-

import logging
import time
import pandas as pd
from datetime import datetime
from functools import partial
from archappl.client import FRIBArchiverDataClient
from archappl.data.utils import LOCAL_ZONE_NAME
from archappl import TQDM_INSTALLED

_LOGGER = logging.getLogger(__name__)


class HitSingleDataEntry(Exception):
    def __init__(self, *args, **kws):
        super(self.__class__, self).__init__(*args, **kws)


def _get_data(pv, from_time, to_time, client=None, use_json=False):
    if client is None:
        client = FRIBArchiverDataClient
    if use_json:
        client.format = 'JSON'
    data = client.get_data(pv,
                           from_time=from_time,
                           to_time=to_time)
    try:
        assert data is not None
        if len(data.iloc[:,0]) == 1:
            raise HitSingleDataEntry
    except AssertionError:
        # got nothing
        r, reason = None, "NotExist"
        _LOGGER.error(f"Get nothing, probably {pv} is not archived")
    except HitSingleDataEntry:
        reason = "SingleEntry"
        data.drop(columns=['severity', 'status'], inplace=True)
        data.rename(columns={'val': pv}, inplace=True)
        r = data
        _LOGGER.warning(f"Only get single sample for {pv}")
    else:
        data.drop(columns=['severity', 'status'], inplace=True)
        data.rename(columns={'val': pv}, inplace=True)
        r, reason = data, "OK"
    finally:
        return r, reason


def _get_data_at_time(pv_list, at_time, client=None):
    if client is None:
        client = FRIBArchiverDataClient
    data = client.get_data_at_time(pv_list, at_time)
    if data == {} or data is None:
        _LOGGER.warning("Retrieved nothing")
        return None
    return data


def get_dataset_with_pvs(pv_list, from_time=None, to_time=None, **kws):
    """Pull data from Archiver Appliance, with a given list of PVs, within defined time slot.
    Return None if no data is retrieved.

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
    use_json : bool
        If set True, fetch data in the form of JSON instead of RAW, default is False.

    Returns
    -------
    r : dataframe
        Pandas dataframe with datetime as the index, and device PV names as columns.

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
    t0_ = time.time()
    client = kws.pop('client', None)
    resample = kws.pop('resample', None)
    verbose = kws.pop('verbose', 0)
    use_json = kws.pop('use_json', False)
    df_list = []
    _LOGGER.info("Start pulling data")
    if verbose != 0 and TQDM_INSTALLED:
        from archappl import tqdm
        pbar = tqdm(pv_list)
    else:
        pbar = pv_list
    for pv in pbar:
        data_, reason_ = _get_data(pv, from_time, to_time, client=client,
                                   use_json=use_json)
        if reason_ == 'NotExist':
            _LOGGER.info(f"Skip not being archived PV: {pv}")
            if verbose > 1:
                pbar.set_description(f"Skip {pv}")
            continue
        df_list.append(data_)
        if verbose > 1:
            pbar.set_description(f"Fetched data for {pv}")
            _LOGGER.debug(f"Fetched data for {pv}")
    if not df_list:
        _LOGGER.warning("Get nothing, return None")
        return None
    data = df_list[0].join(df_list[1:], how='outer')
    data.fillna(method='ffill', inplace=True)
    if resample is not None:
        _LOGGER.info(f"Apply resampling with '{resample}'")
        _df1 = data[from_time:to_time]
        _df2 = _df1[~_df1.index.duplicated(keep='first')]
        data = _df2.resample(resample).ffill()
        data.dropna(inplace=True)
    if verbose > 0:
        _LOGGER.info(f"Fetched all data in {time.time() - t0_:.1f} seconds")
    return data


def get_dataset_with_devices(element_list, field_list, from_time=None, to_time=None, **kws):
    """Pull data from Archiver Appliance, with a given list of devices and dynamic fields,
    within defined time slot. Return None if no data is retrieved.

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
        Pandas dataframe with datetime as the index, and device names as 1st level columns, and
        field names as 2nd level columns.

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
    _df = get_dataset_with_pvs(pv_list, from_time, to_time, **kws)
    return _fieldize_df(_df, element_list, field_list, handle)


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
    setpoint_alt_field_list : list
        A list of field names, for each retrieve readset PVs if given handle is 'setpoint'.

    Returns
    -------
    r : dataframe
        Pandas dataframe.

    Examples
    --------
    >>> # Pull the setpoint values from a list of element for each field defined in field_list,
    >>> # use readset PVs for field defined in setpoint_alt_field_list argument.
    >>> get_dataset_at_time_with_devices(element_list, field_list, t0, handle='setpoint',
    >>>                                  setpoint_alt_field_list=['PHA', 'PHA1', 'PHA2', 'PHA3'])
    """
    handle = kws.pop('handle', 'readback')
    all_pv_list = []
    pv_list_per_element = []
    field_list_per_element = []
    elem_list = []

    cset_alt_flist = kws.pop('setpoint_alt_field_list', [])
    # ['PHA', 'PHA1', 'PHA2', 'PHA3']:

    for i in element_list:
        _pv_list = []
        _field_list = []
        for f in field_list:
            if f not in i.fields:
                continue
            _field_list.append(f)

            # for CAV, retrieve RSET if asking for CSET
            if handle == 'setpoint' and f in cset_alt_flist:
                handle_ = 'readset'
            else:
                handle_ = handle
            #
            field_pv_list_ = i.pv(field=f, handle=handle_)
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

    # map all CAV PHA? PVs from RSET to CSET, create new CSET keys
    if cset_alt_flist:
        for i in element_list:
            # if i.family != 'CAV':
            #     continue
            for f in field_list:
                if f not in i.fields:
                    continue
                if f in cset_alt_flist:
                    data_[i.pv(field=f, handle='setpoint')[0]] = data_[i.pv(field=f, handle='readset')[0]]

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


def _fieldize_df(df, elems, fnames, handle='setpoint'):
    # transform dataframe of retrieved values with PV names as columns,
    # to element/fname multilevel columns
    #
    def _f(elems, fnames, irow):
        _d = irow.to_dict()
        return [elem.get_settings(fname, _d, handle=handle) for elem in elems for fname in fnames]
    data = df.apply(partial(_f, elems, fnames), axis=1).tolist()
    df1 = pd.DataFrame(data=data, index=df.index)
    cols = pd.MultiIndex.from_tuples([(elem.name, fname) for elem in elems for fname in fnames])
    df1.columns = cols
    return df1


def _to_df(dat, tz='UTC'):
    # dataframrize dat (dict of {pv:{payload}}) from get_data_at_time().
    if dat is None:
        return None
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
    df.set_index('PV', inplace=True)
    return df


def read_csv(filepath, parse_dates=['time'], index_col='time', **kws):
    return pd.read_csv(filepath, parse_dates=parse_dates, index_col=index_col, **kws)
