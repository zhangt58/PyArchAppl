# -*- coding: utf-8 -*-

import logging
import os


__LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

# env: ARCHAPPL_LOG_LEVEL: debug, info (default), warning, error, critical
DEFAULT_LOGGING_LEVEL = __LOG_LEVEL_MAP.get(
        os.environ.get('ARCHAPPL_LOG_LEVEL', 'INFO').upper())

logging.basicConfig(
        level=DEFAULT_LOGGING_LEVEL,
        format="[%(asctime)s.%(msecs)03d] %(levelname)s: %(name)s: %(message)s",
        datefmt="%H:%M:%S"
)

_LOGGER = logging.getLogger(__name__)

# set global logging level, default is INFO.
def set_logging_level(level='info'):
    logging.root.setLevel(__LOG_LEVEL_MAP.get(level.upper(), DEFAULT_LOGGING_LEVEL))


try:
    from IPython import get_ipython
    if get_ipython().__class__.__name__ == 'ZMQInteractiveShell':
        NB_SHELL = True
        _LOGGER.debug("Running in Jupyter Notebook")
    else:
        NB_SHELL = False
        _LOGGER.warning("Not running in Jupyter Notebook")
except ImportError:
    NB_SHELL = False
    _LOGGER.warning("'IPython' is not installed")
finally:
    import pkg_resources
    try:
        pkg_resources.get_distribution('tqdm')
    except pkg_resources.DistributionNotFound:
        TQDM_INSTALLED = False
        _LOGGER.warning("'tqdm' is not installed")
    else:
        TQDM_INSTALLED = True
        _LOGGER.debug("Progressbar display is supported")
        if NB_SHELL:
            from tqdm.notebook import tqdm
        else:
            from tqdm import tqdm

from archappl.client import *
from archappl.data import *


__version__ = '0.10.2'
__author__ = 'Tong Zhang <zhangt@frib.msu.edu>'

__doc__ ="""archappl: Python interface of Archiver Appliance."""

_LOGGER.info(f"Running archappl version: {__version__}")
