#!/usr/bin/env python
"""parser/generator for a basic stat format along the following lines:
IQ: 13
It allows for arbitrary strings left and right of the colon and strips
both sides of whitespace. The parser outputs a json dict with lowercase
keys, e.g. {"iq":"13"}. The generated text is somewhat prettified by
aligning the values"""


def parse(lines):
    data = {}
    for line in lines:
        line = line.split(':')
        data[line[0].strip().lower()] = line[1].strip()
    return data


def generate(json):
    maxlen = 0
    for key in json:
        if len(key) > maxlen:
            maxlen = len(key)
    return '\n'.join([key.upper() + ':' + (1+maxlen-len(key))*' ' + json[key] for key in json]) + '\n'
