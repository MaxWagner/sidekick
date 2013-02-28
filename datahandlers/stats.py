#!/usr/bin/env python


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
