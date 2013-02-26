#!/usr/bin/env python

def parse(lines):
    data = {}
    for line in lines:
        line = line.split(':')
        data[line[0].strip()] = line[1].strip()
    return data

def generate(json):
    # TODO implement this properly
    return "DIE: 10\n"
