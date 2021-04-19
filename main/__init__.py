try:
    from IPython import get_ipython
    if get_ipython().__class__.__name__ == 'ZMQInteractiveShell':
        NB_SHELL = True
    else:
        NB_SHELL = False
except ImportError:
    NB_SHELL = False
finally:
    import pkg_resources
    try:
        pkg_resources.get_distribution('tqdm')
    except pkg_resources.DistributionNotFound:
        TQDM_INSTALLED = False
    else:
        TQDM_INSTALLED = True
        if NB_SHELL:
            from tqdm.notebook import tqdm
        else:
            from tqdm import tqdm

from archappl.client import *
from archappl.data import *


__version__ = '0.9.3'
__author__ = 'Tong Zhang <zhangt@frib.msu.edu>'

__doc__ ="""archappl: Python interface of Archiver Appliance."""

