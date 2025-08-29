# PyArchAppl

[![PyPI - Version](https://img.shields.io/pypi/v/PyArchAppl)](https://pypi.org/project/PyArchAppl/)
[![PyPI - License](https://img.shields.io/pypi/l/PyArchAppl)](./LICENSE)
![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue)

**PyArchAppl** is a Python client library for the [EPICS Archiver Appliance](https://github.com/archiver-appliance/epicsarchiverap), providing easy data access, management, and automation for control system data.

---

## Features

- Retrieve and plot time-series data from Archiver Appliance
- Management interface for PVs (Process Variables)
- Command-line tools for data access and inspection
- Flexible site configuration
- Python 3.9, 3.10, 3.11 support

---

## Installation

```bash
pip install pyarchappl
```

To upgrade:
```bash
pip install --upgrade pyarchappl
```

---

## Quick Start

### Data Retrieval Example

```python
from archappl.client import ArchiverDataClient
import matplotlib.pyplot as plt

client = ArchiverDataClient()
client.url = 'http://127.0.0.1:17665'  # Optional, default provided

pv = 'TST:gaussianNoise'
data = client.get_data(pv)

data.plot()
plt.show()
```
![Example Plot](tests/data_plot1.png?raw=true)

### Management Example

```python
from archappl.client import ArchiverMgmtClient

client = ArchiverMgmtClient()
client.url = 'http://127.0.0.1:17665'

all_pvs = client.get_all_pvs(pv="TST*")
print(all_pvs)
# [u'TST:fakeGaussianNoise', u'TST:gaussianNoise', u'TST:uniformNoise']
```

---

## Command Line Tools

PyArchAppl provides convenient CLI tools:

- `pyarchappl-get` &mdash; Retrieve data (use `-h` for help)
- `pyarchappl-inspect` &mdash; Inspect archiver information (use `-h` for help)

---

## Configuration

PyArchAppl uses an INI-style configuration file to define service connection and behavior.

**Config file search order:**
1. `~/.pyarchappl/config.ini`
2. `/etc/pyarchappl/config.ini`
3. Package default: `main/config/default.ini`

Override with the environment variable: `PYARCHAPPL_CONFIG_FILE`.

See the [default.ini](./main/config/default.ini) for all options.

---

## Development

- Clone the repo and install dependencies from `requirements.txt` and `requirements-dev.txt`.
- [Optional] Set up a local Archiver Appliance for testing.

---

## License

This project is licensed under the GPLv3+ License. See the [LICENSE](./LICENSE) file for details.

---

## Links

- [Documentation](https://zhangt58.github.io/PyArchAppl/)
- [Archiver Appliance Docs](https://epicsarchiver.readthedocs.io/en/latest/)
- [PyPI Project](https://pypi.org/project/PyArchAppl/)