#!/usr/bin/env python
"""parse/generate data for a relatively simple skill format. A skill
is comprised of its name, its difficulty (one character), the stat
it's based on, and the number of points spent into its proficiency.
Different columns are separated by at least 2 spaces. Example:
Acting               A  IQ    13
Driving: Motorcycle  A  DX-1  11
Will parse into:
[{"name":"Acting","difficulty":"A","base stat":"IQ","points":"13"},
 {"name":"Driving: MOtorcycle","difficulty":"A","base stat":"DX-1","points":"11"}]"""


def parse(lines):
    skills = []
    for line in lines:
        # split along longer amounts of whitespace
        items = [str.strip() for str in line.split('  ') if str]
        if len(items) < 4:
            items.extend((4 - len(items)) * '')
        skills.append({"name": items[0], "difficulty": items[1], "base": items[2], "points": items[3]})
    return skills


def generate(json):
    namemax = 0
    #diffmax = 0  # we can assume that difficulty is always encoded in the same length
    statmax = 0
    for item in json:
        namemax = max(namemax, len(item["name"]))
        statmax = max(statmax, len(item["base stat"]))
        #diffmax = max(diffmax, len(item["difficulty"]))
    return '\n'.join([item["name"]
                     + (namemax - len(item["name"]) + 2)*' '
                     + item["difficulty"]
                     #+ ()*' '
                     + "  "
                     + item["base stat"]
                     + (statmax - len(item["base stat"]) + 2)*' '
                     + item["points"] for item in json]) + '\n'
