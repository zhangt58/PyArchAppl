#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Inspect the PV archived information.
"""

import logging
import sys
import pandas as pd
from pathlib import Path
from typing import Union

from .utils import SimpleNamespaceEncoder

_LOGGER = logging.getLogger(__name__)

try:
    from archappl.client import ArchiverMgmtClient
except ImportError:
    _LOGGER.warning("This command is disabled.")
    sys.exit(1)

import argparse
import json
import os

VALID_INFO_KEYS = ('status', 'type', 'details', 'stores')


class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


parser = argparse.ArgumentParser(
        description="Inspect Archiver Appliance w/ or w/o PVs.",
        formatter_class=Formatter)
parser.add_argument('--url', dest='url', default=None,
        help="URL of Archiver Appliance, defaults to the one defined in site configuration file.")
parser.add_argument('--pv', action='append', dest='pv_list',
        help="List of PVs for inspection, each define with --pv")
parser.add_argument('--pv-file', dest='pv_file', default=None,
        help="A file for PVs, one PV per line (skip lines start with #), append each to pv_list")
parser.add_argument('--key', dest='key', default='status',
        help="Define the kind of information to inspect: 'status' (default), 'type', 'details', 'stores'")
parser.add_argument('--sub-keys', dest='sub_keys', default=None,
                    help="Define the sub-level keys separated with ',' to inspect if applicable.")
parser.add_argument('--version', action='store_true',
                    help="Print out version info")
parser.add_argument('--info', action='store_true',
                    help="Print out the info of archiver appliance")
parser.add_argument('--log-file', dest='logfile', default=None,
                    help="File path for log messages, print to stdout if not defined.")
parser.add_argument('-o', '--output', dest='output', default=None,
                    help="File path for output data, print to stdout if not defined")
parser.add_argument('--show-config', action='store_true',
                    help = "Print the site configuration with essential dependencies and their versions.")

parser.epilog = \
"""
Examples:
# Check if a PV is being archived or not
$ {n} --pv TST:constant # --key status
$ {n} --pv TST:constant --pv TST:NONEXIST --sub-keys pvName,status
# Replace --key with "type", "details", "stores" to have different results
# Output the results to a file
$ {n} --pv TST:constant --pv TST:uniformNoise --key details --output details.xlsx
$ {n} --pv TST:constant --pv TST:uniformNoise --key type --output type.json
""".format(n=os.path.basename(sys.argv[0]))


def main():
    _LOGGER.info(f"Executing {os.path.basename(sys.argv[0])} ...")
    args = parser.parse_args(sys.argv[1:])

    if args.version:
        from archappl import __version__
        from .utils import print_deps
        print(f"PyArchAppl: {__version__}")
        print_deps()
        sys.exit(0)

    if args.show_config:
        from .utils import print_site_config
        print_site_config()
        sys.exit(0)

    # log file
    if args.logfile is not None:
        _handler = logging.FileHandler(args.logfile)
        _fmt = logging.Formatter(
            fmt="[%(asctime)s.%(msecs)03d] "
                "%(levelname)s: %(name)s: %(message)s",
            datefmt="%Y%m%dT%H:%M:%S")
        _handler.setFormatter(_fmt)
        _LOGGER.parent.addHandler(_handler)
        #
        _LOGGER.info(f"Writing log messages to {args.logfile}")

    # client
    if args.url is None:
        client = ArchiverMgmtClient()
    else:
        client = ArchiverMgmtClient(url=args.url)

    # Archiver Appliance info
    if args.info:
        _LOGGER.info("Getting Archiver Appliance info...")
        print(json.dumps(client.get_appliance_info(), indent=2))
        sys.exit(0)

    # pv list
    if args.pv_list is None:
        pv_list = []
    else:
        pv_list = args.pv_list
        _LOGGER.info(f"Defined {len(pv_list)} PVs via '--pv'")
    try:
        with open(args.pv_file, "r") as fp:
            i = 0
            for line in fp:
                if line.startswith("#"):
                    continue
                if line.strip() not in pv_list:
                    pv_list.append(line.strip())
                    i += 1
    except:
        pass
    else:
        _LOGGER.info(f"Read {i} PVs from '{args.pv_file}'")
    if not pv_list:
        parser.print_help()
        sys.exit(1)

    #
    if args.key not in VALID_INFO_KEYS:
        print(f"Invalid key, supported ones: {VALID_INFO_KEYS}")
        sys.exit(1)

    if args.sub_keys is not None:
        sub_keys = args.sub_keys.split(',')
    else:
        sub_keys = []

    if args.key == "status":
        r = client.get_pv_status(pv_list)
        s = _get_json_with_subkeys(r, sub_keys)
        _print_json(s, args.output)
    elif args.key == "type":
        r_ = {pv: client.get_pv_type_info(pv) for pv in pv_list}
        r = {k: v for k, v in r_.items() if v is not None}
        s = _get_json_with_subkeys(r, sub_keys)
        _print_json(s, args.output)
    elif args.key == "details":
        if args.output is not None:
            if Path(args.output).suffix != ".xlsx":
                _LOGGER.error("Only support writing details to an xlsx file.")
                sys.exit(1)
            else:
                xlsx_file = args.output
        else:
            xlsx_file = None
        r = [(pv, client.get_pv_details(pv)) for pv in pv_list]
        if xlsx_file is not None:
            _LOGGER.info(f"Writing details to '{xlsx_file}' ...")
            _write_details_to_excel(xlsx_file, r)
        else:
            print(r)
    elif args.key == "stores":
        r_ = {pv: client.get_stores_for_pv(pv) for pv in pv_list}
        r = {k: v for k, v in r_.items() if v is not None}
        s = _get_json_with_subkeys(r, sub_keys)
        _print_json(s, args.output)


def _write_details_to_excel(output_path: str, r: list):
    def get_sheet_name(pv_name: str):
        return pv_name.replace(":", "-")

    with pd.ExcelWriter(output_path) as writer:
        for pv_name, df in r:
            if df is None:
                continue
            df.to_excel(writer, sheet_name=get_sheet_name(pv_name))


def _get_json_with_subkeys(d: dict, sub_keys: list[str], indent: int = 2) -> str:
    s = json.dumps(d, indent=indent, cls=SimpleNamespaceEncoder)
    if sub_keys:
        d = json.loads(s)
        d1 = {k: {ik: v.get(ik, "N/A") for ik in sub_keys}
              for k, v in d.items()}
        return json.dumps(d1, indent=indent)
    else:
        return s


def _print_json(s: str, outfile: Union[str, None] = None):
    if outfile is not None:
        _LOGGER.info(f"Writing output to '{outfile}' ...")
        with open(outfile, "w") as fp:
            fp.write(s)
    else:
        _LOGGER.info("Printing output ...")
        print(s, end="", file=sys.stdout)
