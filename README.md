# pyarchappl

Python interface for [Archiver Appliance](https://slacmshankar.github.io/epicsarchiver_docs/index.html).

# Installation

See [INSTALL.md](INSTALL.md)

# How to test & develop

## [Optional] Set up Archiver Appliance testing environment

## Data Retrieval Client
```Python
from archappl.client import ArchiverDataClient
import matplotlib.pyplot as plt


plt.style.use('ggplot')

client = ArchiverDataClient()
client.url = 'http://127.0.0.1:17665'  # default url, optional.

pv = 'TST:gaussianNoise'
data = client.get_data(pv)

data.plot()
plt.show()
```
![](tests/data_plot1.png?raw=true)

### Data (PV) Management Client
```Python
from archappl.client import ArchiverMgmtClient


client = ArchiverMgmtClient()
client.url = 'http://127.0.0.1:17665'

all_pvs = client.get_all_pvs()
print(all_pvs)
# [u'TST:fakeGaussianNoise', u'TST:gaussianNoise', u'TST:uniformNoise']
```
