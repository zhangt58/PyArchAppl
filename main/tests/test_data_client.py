# -*- coding: utf-8 -*-

from unittest.mock import Mock

import pandas as pd

from archappl.client import ArchiverDataClient
from archappl.contrib import data as contrib_data


def test_get_data_url_includes_full_request():
    client = ArchiverDataClient(
        url="http://archiver.example:17665", format="raw")

    url = client.get_data_url(
        "TST:PV",
        from_time="2026-07-24T10:00:00.000Z",
        to_time="2026-07-24T11:00:00.000Z",
    )

    assert url == (
        "http://archiver.example:17665/retrieval/data/getData.raw"
        "?pv=TST:PV"
        "&from=2026-07-24T10:00:00.000Z"
        "&to=2026-07-24T11:00:00.000Z"
    )


def test_get_data_uses_reported_url(monkeypatch):
    client = ArchiverDataClient(
        url="http://archiver.example:17665", format="json")
    response = Mock(ok=True)
    response.json.return_value = [{
        "meta": {},
        "data": [{
            "secs": 1,
            "nanos": 0,
            "val": 2.0,
            "status": 0,
            "severity": 0,
        }],
    }]
    get = Mock(return_value=response)
    monkeypatch.setattr("archappl.data.client.requests.get", get)

    url = client.get_data_url(
        "TST:PV",
        from_time="2026-07-24T10:00:00.000Z",
        to_time="2026-07-24T11:00:00.000Z",
    )
    client.get_data(
        "TST:PV",
        from_time="2026-07-24T10:00:00.000Z",
        to_time="2026-07-24T11:00:00.000Z",
    )

    get.assert_called_once_with(url)


def test_only_verbose_three_outputs_full_requested_url(monkeypatch, capsys):
    client = ArchiverDataClient(
        url="http://archiver.example:17665", format="raw")
    index = pd.DatetimeIndex([
        "2026-07-24T10:00:00Z",
        "2026-07-24T10:00:01Z",
    ])
    frame = pd.DataFrame(
        {
            "val": [2.0, 3.0],
            "status": [0, 0],
            "severity": [0, 0],
        },
        index=index,
    )
    monkeypatch.setattr(
        client, "get_data", Mock(side_effect=[frame.copy(), frame.copy()]))
    monkeypatch.setattr(contrib_data, "TQDM_INSTALLED", False)

    contrib_data.get_dataset_with_pvs(
        ["TST:PV"],
        "2026-07-24T10:00:00.000Z",
        "2026-07-24T11:00:00.000Z",
        client=client,
        verbose=2,
    )
    assert capsys.readouterr().err == ""

    contrib_data.get_dataset_with_pvs(
        ["TST:PV"],
        "2026-07-24T10:00:00.000Z",
        "2026-07-24T11:00:00.000Z",
        client=client,
        verbose=3,
    )
    assert capsys.readouterr().err == (
        "Requested URL: "
        "http://archiver.example:17665/retrieval/data/getData.raw"
        "?pv=TST:PV"
        "&from=2026-07-24T10:00:00.000Z"
        "&to=2026-07-24T11:00:00.000Z\n"
    )
