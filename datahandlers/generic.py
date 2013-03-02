#!/usr/bin/env python
"""generic data parser/generator for everything that doesn't
get caught by another file. It doesn't do any fancy stuff, it only
returns strings. It does unpack lists and dicts when given json
data, though."""

def parse(lines):
    for i in range(len(lines)-1):
        lines[i] = lines[i].strip()
    return lines


def generate(json):
    # We really only want to have to deal with strings here
    strings = []
    # we do a best effort on dicts and list, that should be generic enough
    if type(json) is dict:
        text = [generate(val) for val in json.values()]
        text.append('')
        return '\n'.join(text)
    if type(json) is list:
        text = [generate(val) for val in json]
        text.append('')
        return '\n'.join(text)
    return str(json)
