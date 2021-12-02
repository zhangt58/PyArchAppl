# -*- coding: utf-8 -*-

import logging
import re
from datetime import datetime

from . import EPICSEvent_pb2 as pb


_LOGGER = logging.getLogger(__name__)

SAMPLE_PARSER_MAP = {
    'SCALAR_STRING': pb.ScalarString,
    'SCALAR_SHORT': pb.ScalarShort,
    'SCALAR_FLOAT': pb.ScalarFloat,
    'SCALAR_ENUM': pb.ScalarEnum,
    'SCALAR_BYTE': pb.ScalarByte,
    'SCALAR_INT': pb.ScalarInt,
    'SCALAR_DOUBLE': pb.ScalarDouble,
    'WAVEFORM_STRING': pb.VectorString,
    'WAVEFORM_SHORT': pb.VectorShort,
    'WAVEFORM_FLOAT': pb.VectorFloat,
    'WAVEFORM_ENUM': pb.VectorEnum,
    'WAVEFORM_BYTE': pb.VectorChar,
    'WAVEFORM_INT': pb.VectorInt,
    'WAVEFORM_DOUBLE': pb.VectorDouble,
    'V4_GENERIC_BYTES': pb.V4GenericBytes,
}


def unescape(line):
    # unescape the line to ESC, \n and \r
    # http://127.0.0.1:17665/mgmt/ui/help/pb_pbraw.html
    t = {
        b'\x1b\x01': b'\x1b', # ESC
        b'\x1b\x02': b'\x0a', # \n
        b'\x1b\x03': b'\x0d', # \r
    }
    r = re.compile(b'(%s)' % b'|'.join(map(re.escape, t)))
    return r.sub(lambda m: t[m.group()], line)


def get_sample_parser(i_type):
    # print("Use Parser: ", pb.PayloadType.Name(i_type))
    return SAMPLE_PARSER_MAP[pb.PayloadType.Name(i_type)]


def unpack_raw_data(data: bytes):
    unpacked_data = []
    i = 0
    hit_header = True
    for line in data.split(b'\n'):
        line = line.strip()
        if not line:
            hit_header = True
            continue

        unescaped_line = unescape(line)

        if hit_header:
            I = pb.PayloadInfo()
            I.ParseFromString(unescaped_line)
            year = I.year
            f = get_sample_parser(I.type)()
            hit_header = False
            header_dict = {f.name: f.val for f in I.headers}
            header_dict['name'] = I.pvname
            year_in_sec = (datetime(year, 1, 1) - datetime(1970, 1, 1)).total_seconds()
        else:
            i += 1
            f.ParseFromString(unescaped_line)
            unpacked_data.append({
                'secs': year_in_sec + f.secondsintoyear,
                'val': f.val,
                'nanos': f.nano,
                'status': f.status,
                'severity': f.severity})
    _LOGGER.debug(f"Processed {i} samples for {header_dict['name']}.")
    return [{'meta': header_dict, 'data': unpacked_data}]
