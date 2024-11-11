# PyArchAppl

![PyPI - Version](https://img.shields.io/pypi/v/PyArchAppl)
![PyPI - License](https://img.shields.io/pypi/l/PyArchAppl)
![Static Badge](https://img.shields.io/badge/Python-3.9-blue)
![Static Badge](https://img.shields.io/badge/Python-3.10-blue)
![Static Badge](https://img.shields.io/badge/Python-3.11-blue)

The Python client library for [Archiver Appliance](https://slacmshankar.github.io/epicsarchiver_docs/index.html).

# Installation

`pip install pyarchappl [--upgrade]`

# User Guide

## Site Configuration

A site configuration file is an INI file which defines how the package work with the service.
The full version of the configuration file could be found at [default.init](./main/config/default.ini)

The search priority follows:
1. `~/.pyarchappl/config.ini`
2. `/etc/pyarchappl/config.ini`
3. `<package-default>: default.ini`

However, it could be overridden via an env `PYARCHAPPL_CONFIG_FILE`.

## CLI Tools

`PyArchAppl` provides convenient command line interface tools as console apps:

* ``pyarchappl-get``: the tool for data retrieval, read the usage help message by `-h` option
* ``pyarchappl-inspect``: the tool for inspect the information, `-h` for help

# Development

## [Optional] Set up Archiver Appliance testing environment

## Data Retrieval Interface
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

### Management Interface
```Python
from archappl.client import ArchiverMgmtClient

client = ArchiverMgmtClient()
client.url = 'http://127.0.0.1:17665'

all_pvs = client.get_all_pvs(pv="TST*")
print(all_pvs)
# [u'TST:fakeGaussianNoise', u'TST:gaussianNoise', u'TST:uniformNoise']
```