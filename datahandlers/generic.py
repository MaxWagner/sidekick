#!/usr/bin/env python


def parse(lines):
    return '\n'.join(lines)


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
