# -*- coding: utf-8 -*-

from archappl.client import ArchiverDataClient
from archappl.contrib import get_dataset
from phantasy import MachinePortal
from voyager import voyager


mp = MachinePortal("FRIB_VA", "LS1FS1")
bpms = mp.get_elements(type="BPM")
client = ArchiverDataClient()
client.url = "http://127.0.0.1:17665"

ts_from = "2020-11-16T14:18:00.000000-05:00"
ts_to = "2020-11-16T14:24:20.000000-05:00"
field_list = ['X', 'Y']

df = get_dataset(bpms, field_list,
                 ts_from, ts_to, resample="1S",
                 echo=True,
                 client=client)

voyager(df)
