# coding: utf-8
import numpy as np
from phantasy import MachinePortal
from archappl.client import ArchiverDataClient

mp = MachinePortal("FRIB", "MEBT2FS1A")
bpms = mp.get_elements(type="BPM")
client = ArchiverDataClient()
client.url = 'http://epicsarchiver0.ftc:17668'

pvs_x = [i.pv('X', handle='readback')[0] for i in bpms]
pvs_y = [i.pv('Y', handle='readback')[0] for i in bpms]

# client.get_data(pv=pvs[0], ifrom="2019-03-05T12:05:00.000-04:00",
#                 to="2019-03-05T12:06:00.000-04:00")

ts = '2019-03-05T13:04:08.000000-05:00'

traj_x = client.get_data_at_time(pvs_x, ts=ts)
traj_y = client.get_data_at_time(pvs_y, ts=ts)
valid_pv_elem_list = [elem for elem in bpms
                      if elem.pv('X', handle='readback')[0] in traj_x]
pos = np.asarray([i.sb for i in valid_pv_elem_list])
valid_x = np.asarray([traj_x[p]['val'] for p in pvs_x if p in traj_x])
valid_y = np.asarray([traj_y[p]['val'] for p in pvs_y if p in traj_y])

data = np.vstack([pos, valid_x, valid_y]).T
np.savetxt('data_from_archiver.txt', data, delimiter=',')
