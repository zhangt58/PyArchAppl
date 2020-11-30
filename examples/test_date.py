#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from archappl.data import parse_dt
from datetime import datetime


def test():
    # datetime 1 hour ago
    dt0 = datetime.now()
    dt1 = parse_dt("1 month and 1 hour before", align_tz=True)
    print(dt1)


if __name__ == '__main__':
    test()
