# coding: utf-8

from archappl.client import ArchiverDataClient
import matplotlib.pyplot as plt


plt.style.use('ggplot')


client = ArchiverDataClient()

pv = 'TST:gaussianNoise'
d = client.get_data(pv)

d.plot()
plt.show()
