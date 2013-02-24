#!/usr/bin/env python

def parse(lines):
    data = {}
    for line in lines:
        line = line.split(':')
        data[line[0].strip()] = int(line[1].strip())
    return data
