#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Get data from archiver appliance by PV names and time range.

Example:
$ pyarchappl-get --verbose 1 --pv VA:LS1_CA01:BPM_D1129:X_RD --pv VA:LS1_CA01:BPM_D1129:Y_RD \
                 --from-time 2021-04-15T20:10:00.000Z --to-time 2021-04-15T21:25:00.000Z
                 --resample 1min --url http://127.0.0.1:17665
"""

from archappl.client import ArchiverDataClient
from archappl.client import FRIBArchiverDataClient

import argparse
import sys
import os
import json

class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(
        description="Retrieve data from Archiver Appliance and export as a file.",
        formatter_class=Formatter)
parser.add_argument('--url', dest='url', default=None,
        help="URL of Archiver Appliance, default is FRIB FTC archiver")
parser.add_argument('--pv', action='append', dest='pv_list',
        help="List of PVs for retrieval, each define with --pv")
parser.add_argument('--pv-file', dest='pv_file', default=None,
        help="A file for PVs, one PV per line (skip line starts with #), append each to pv_list")
parser.add_argument('--from', dest='from_time',
        help="A string of begin time in ISO8601 format")
parser.add_argument('--to', dest='to_time',
        help="A string of end time in ISO8601 format")
parser.add_argument('--resample', dest='resample', default=None,
        help="The offset string/object representing target conversion, e.g. '1S' for resample with 1 second")
parser.add_argument('--verbose', '-v', action='count', default=0,
        help="Verbosity level of the log output, 0: no output, 1(-v): output progress, 2(-vv): output progress with description")
parser.add_argument('-o', '--output', dest='output', default=None,
        help="File path for output data, print to stdout if not defined")
parser.add_argument('-f', '--output-format', dest='fmt', default='csv',
        help="File format for output data, supported: csv, hdf, html, ...")
parser.add_argument('--format-args', dest='fmt_args', type=json.loads, default='{}',
        help='''Additional arguments passed to data export function in the form of dict, e.g. '{"key":"data"}' (for hdf format)''')

parser.epilog = \
"""
Examples:
# Retrieve raw PV data in the defined time frame
$ {n} -o data.csv -v \\
  --pv LS1_CA01:BPM_D1129:X_RD --pv LS1_CA01:BPM_D1129:Y_RD  \\
  --from 2021-04-15T20:10:00.000Z --to 2021-04-15T21:25:00.000Z \\

# Align the timestamps, resample at 1 second
$ {n} -o data.csv -v \\
  --pv LS1_CA01:BPM_D1129:X_RD --pv LS1_CA01:BPM_D1129:Y_RD  \\
  --from 2021-04-15T20:10:00.000Z --to 2021-04-15T21:25:00.000Z \\
  --resample 1S

# Load PV names from a file
$ {n} --output data.csv -vv \\
  --pv-file pvlist.txt \\
  --from 2021-04-15T20:10:00.000Z --to 2021-04-15T21:25:00.000Z \\

> Time format:
  The following time strings with different timezones define the same time:
  2021-04-15T21:25:00.000Z (GMT)
  2021-04-15T17:25:00.00-04:00 (America/New_York)
""".format(n=os.path.basename(sys.argv[0]))


def main():
    args = parser.parse_args(sys.argv[1:])

    # time range
    if args.from_time is None or args.to_time is None:
        parser.print_help()
        sys.exit(1)

    # pv list
    if args.pv_list is None:
        pv_list = []
    else:
        pv_list = args.pv_list
    try:
        with open(args.pv_file, "r") as fp:
            for line in fp:
                if line.startswith("#"):
                    continue
                if line.strip() not in pv_list:
                    pv_list.append(line.strip())
    except:
        pass
    if pv_list == []:
        parser.print_help()
        sys.exit(1)

    # client
    if args.url is None:
        client = FRIBArchiverDataClient
    else:
        client = ArchiverDataClient(url=args.url)

    from archappl.contrib import get_dataset_with_pvs

    dset = get_dataset_with_pvs(pv_list, args.from_time, args.to_time, client=client,
                                resample=args.resample, verbose=args.verbose)
    output = args.output
    if output is None:
        print(dset.to_string())
    else:
        attr_fmt = f"to_{args.fmt}"
        if hasattr(dset, attr_fmt):
            getattr(dset, attr_fmt)(output, **args.fmt_args)
        else:
            print(f"{args.fmt}: no supported export function.")
            sys.exit(1)
