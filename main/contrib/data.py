# -*- coding: utf-8 -*-


from archappl.client import FRIBArchiverDataClient
import time
from archappl import tqdm
from archappl import printlog


def get_data(pv, ts_from, ts_to, client=None):
    if client is None:
        client = FRIBArchiverDataClient
    data = client.get_data(pv,
                           ts_from=ts_from,   #'2020-10-09T12:00:00.000000-05:00'
                           ts_to=ts_to)       #'2020-10-09T12:20:00.000000-05:00'
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
    df_list = []
    for pv in pv_list:
        data_ = get_data(pv, ts_from, ts_to, client=client)
        if data_ is None:
            if echo:
                print(f"Skip {pv}, no data to fetch.")
            continue
        df_list.append(data_)
        if echo:
            print(f"Fetched data of {pv}.")
    data = df_list[0].join(df_list[1:], how='outer')
    data.fillna(method='ffill', inplace=True)
    if resample is not None:
        data = data.resample(resample).ffill()
        data.dropna(inplace=True)
    if echo:
        print(f"Data fetching is done, cost {time.time() - t0} seconds.")
    return data


def get_dataset(element_list, field_list, ts_from, ts_to, **kws):
    """
    """
    client = kws.pop('client', None)
    resample = kws.pop('resample', None)
    verbose = kws.pop('verbose', 0)
    t0 = time.time()
    df_list = []
    if verbose != 0:
        pbar = tqdm(element_list)
    else:
        pbar = element_list
    for i in pbar:
        for field in field_list:
            pv = i.pv(field=field)[0]
            data_ = get_data(pv, ts_from, ts_to, client=client)
            if data_ is None:
                if verbose > 1:
                    pbar.set_description(f"Skip {i.name}[{field}]")
                continue
            df_list.append(data_)
            if verbose > 1:
                pbar.set_description(f"Fetched {i.name}[{field}]")
    data = df_list[0].join(df_list[1:], how='outer')
    data.fillna(method='ffill', inplace=True)
    if resample is not None:
        data = data.resample(resample).ffill()
        data.dropna(inplace=True)
    if verbose > 0:
        printlog(f"Fetch all data, time cost: {time.time() - t0:.1f} seconds.")
    return data
