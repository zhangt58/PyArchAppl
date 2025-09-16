# -*- coding: utf-8 -*-

import pytest
try:
    from archappl.client import ArchiverMgmtClient
except ImportError:
    print("Admin client is not available, exit.")
    ADMIN_DISABLED = True
else:
    ADMIN_DISABLED = False

@pytest.mark.skipif(ADMIN_DISABLED, reason="Admin client is not available")
def test_getApplianceInfo(get_local_mgmt_client,
                          get_local_appliance_info: dict):
    r = get_local_mgmt_client.get_appliance_info()
    assert r == get_local_appliance_info


@pytest.mark.skipif(ADMIN_DISABLED, reason="Admin client is not available")
def test_getAllPVs(get_local_mgmt_client,
                   get_local_pvs: dict):
    pv = get_local_pvs['TST_archived'][0]
    r = get_local_mgmt_client.get_all_pvs(pv=pv)
    assert r == [pv]

    pv = get_local_pvs['Invalid']
    r = get_local_mgmt_client.get_all_pvs(pv=pv)
    assert len(r) == 0

    r = get_local_mgmt_client.get_all_pvs(pv="TST*")
    # only two three pvs are being archived
    assert len(r) == 3

    r = get_local_mgmt_client.get_all_pvs(pv="TST*", limit=2)
    assert len(r) == 2
    assert r[0] == 'TST:constant'  # alphabetically
    assert r[1] == 'TST:fakeGaussianNoise'  # alphabetically, it is showing before TST:uniformNoise


@pytest.mark.skipif(ADMIN_DISABLED, reason="Admin client is not available")
def test_getPVStatus(get_local_mgmt_client,
                     get_local_pvs: dict):
    pv1 = get_local_pvs['TST_archived'][0]
    r1 = get_local_mgmt_client.get_pv_status(pv=pv1)
    assert len(r1) == 1
    assert r1[pv1].pvName == pv1
    assert r1[pv1].status == "Being archived"

    r2 = get_local_mgmt_client.get_pv_status(pv="TST*")
    assert len(r2) == 3

    pv2 = get_local_pvs['Invalid']
    r3 = get_local_mgmt_client.get_pv_status(pv=pv2)
    assert len(r3) == 1
    assert r3[pv2].pvName == pv2
    assert r3[pv2].status == "Not being archived"

    r1 = get_local_mgmt_client.get_pv_status(pv=pv1)
    r3 = get_local_mgmt_client.get_pv_status(pv=pv2)
    r4 = get_local_mgmt_client.get_pv_status(pv=[pv1, pv2])
    assert r4[pv1] == r1[pv1]
    assert r4[pv2] == r3[pv2]


@pytest.mark.skipif(ADMIN_DISABLED, reason="Admin client is not available")
def test_get_pv_type_info(get_local_mgmt_client,
                          get_local_pvs: dict):
    pv1 = get_local_pvs['TST_archived'][0]
    r1 = get_local_mgmt_client.get_pv_type_info(pv=pv1)
    assert r1.pvName == pv1

    pv2 = get_local_pvs['Invalid']
    r2 = get_local_mgmt_client.get_pv_type_info(pv=pv2)
    assert r2 is None


@pytest.mark.skipif(ADMIN_DISABLED, reason="Admin client is not available")
def test_get_pv_details(get_local_mgmt_client,
                        get_local_pvs: dict):
    pv1 = get_local_pvs['TST_archived'][0]
    r1 = get_local_mgmt_client.get_pv_details(pv=pv1)
    assert r1.loc[("pv", "Channel Name"), "value"] == pv1
    assert r1.loc[("mgmt", "PV Name"), "value"] == pv1

    pv2 = get_local_pvs['Invalid']
    r2 = get_local_mgmt_client.get_pv_details(pv=pv2)
    assert r2 is None