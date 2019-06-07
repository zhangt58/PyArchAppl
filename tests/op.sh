#!/bin/bash

# post
curl -H "Content-Type: application/json" -XPOST -s \
    "http://epicsarchiver0.ftc:17668/retrieval/data/getDataAtTime?at=2019-03-05T13:04:08.120000-05:00" -d '["LS1_CB09:BPM_D1761:XPOS_RD"]'

# "LS1_CB09:BPM_D1761:XPOS_RD"
# "FE_MEBT:BPM_D1056:XPOS_RD"

