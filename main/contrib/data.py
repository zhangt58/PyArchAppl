# -*- coding: utf-8 -*-


from archappl.client import FRIBArchiverDataClient
import time


def get_data(pv, ts_from, ts_to, client=None):
    if client is None:
        client = FRIBArchiverDataClient
    data = client.get_data(pv,
                           ifrom=ts_from,  #'2020-10-09T12:00:00.000000-05:00'
                           to=ts_to)       #'2020-10-09T12:20:00.000000-05:00'
    if len(data.iloc[:, 0]) == 1:
        return None
    data.drop(columns=['severity', 'status'], inplace=True)
    data.rename(columns={'val': pv}, inplace=True)
    return data


def get_dataset1(pv_list, ts_from, ts_to, **kws):
    client = kws.pop('client', None)
    resample = kws.pop('resample', None)
    echo = kws.pop('echo', False)
    t0 = time.time()
    data = None
    for pv in pv_list:
        _con, data = _update_ds(data, pv, ts_from, ts_to, client=client)
        if not _con:
            if echo:
                print(f"Skip {pv}, no data to fetch.")
            continue
        if echo:
            print(f"Fetched data of {pv}.")
    data.fillna(method='ffill', inplace=True)
    if resample is not None:
        data = data.resample(resample).ffill()
        data.dropna(inplace=True)
    if echo:
        print(f"Data fetching is done, cost {time.time() - t0} seconds.")
    return data


def get_dataset(element_list, field_list, ts_from, ts_to, **kws):
    client = kws.pop('client', None)
    resample = kws.pop('resample', None)
    echo = kws.pop('echo', False)
    t0 = time.time()
    data = None
    for i in element_list:
        for field in field_list:
            pv = i.pv(field=field)[0]
            _con, data = _update_ds(data, pv, ts_from, ts_to, client=client)
            if not _con:
                if echo:
                    print(f"Skip {i.name}[{field}], no data to fetch.")
                continue
            if echo:
                print(f"Fetched data of {i.name}[{field}].")
    data.fillna(method='ffill', inplace=True)
    if resample is not None:
        data = data.resample(resample).ffill()
        data.dropna(inplace=True)
    if echo:
        print(f"Data fetching is done, cost {time.time() - t0} seconds.")
    return data


def _update_ds(data, pv, ts_from, ts_to, client=None):
    data_ = get_data(pv, ts_from, ts_to, client)
    if data_ is None:
        return False, data
    if data is None:
        data = data_
    else:
        data = data.join(data_, how='outer')
    return True, data

