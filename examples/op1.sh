#!/bin/bash

# post
curl -H "Content-Type: application/json" -XGET -s \
    "http://epicsarchiver0.ftc:17668/retrieval/data/getData.json?pv=FE_MEBT:BPM_D1056:XPOS_RD&from=2020-10-09T12:00:00.000000-04:00&to=2020-10-09T12:15:00.000000-04:00"
