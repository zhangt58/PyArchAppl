# -*- coding: utf-8 -*-
from typing import Union
from archappl.client import ArchiverMgmtClient


def get_pv_status(pv: Union[list[str], str], client: ArchiverMgmtClient = None) -> Union[list[str], str]:
    """ Return the same shape of the input PVs for the defined status information.

    Parameters
    ----------
    pv : str or list[str]
        A PV name or a list of PV names.
    client : ArchiverDataClient, optional
        The ArchiverDataClient or the default one.

    Returns
    -------
    r : str or list[str]
        A list or a single string containing the PV status.

    See Also
    --------
    `~ArchiverDataClient.get_pv_status`
    """
    if client is None:
        client = ArchiverMgmtClient()
    if isinstance(pv, str):
        pv = pv,
    sts = [client.get_pv_status(i)[i].status for i in pv]
    if len(pv) == 1:
        return sts[0]
    else:
        return sts



