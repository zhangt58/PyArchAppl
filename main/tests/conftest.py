# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
from archappl.client import ArchiverDataClient

@pytest.fixture
def get_local_mgmt_client():
    from archappl.client import ArchiverMgmtClient
    return ArchiverMgmtClient(url="http://127.0.0.1:17666")


@pytest.fixture
def get_local_data_client() -> ArchiverDataClient:
    return ArchiverDataClient(url="http://127.0.0.1:17666")


@pytest.fixture
def get_local_appliance_info() -> dict:
    return {
        'engineURL': 'http://localhost:17665/engine/bpl',
        'identity': 'appliance0',
        'retrievalURL': 'http://localhost:17665/retrieval/bpl',
        'clusterInetPort': 'localhost:17670',
        'etlURL': 'http://localhost:17665/etl/bpl',
        'version': 'Archiver Appliance Version 1.1.0',
        'mgmtURL': 'http://localhost:17665/mgmt/bpl',
        'dataRetrievalURL': 'http://localhost:17665/retrieval'
    }

@pytest.fixture
def get_local_pvs() -> dict:
    pv1 = "TST:uniformNoise"
    pv2 = "TST:fakeGaussianNoise"
    pv3 = "TST:gaussianNoise"
    pv4 = "AN_INVALID_PV"
    return {
        'TST_archived': [pv1, pv2],
        'TST_not_archived': pv3,
        'Invalid': pv4,
    }

@pytest.fixture
def config_dir() -> Path:
    return Path(__file__).parent.joinpath("config")