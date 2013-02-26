#!/usr/bin/env python

from urllib.parse import urlparse
from bottle import route, run, request, static_file
import sys
import os
import datahandlers.generic

port = 8080
character_sheets = []
@route('/sheets', method='GET')
def get_listing():
    """Return a listing of available character sheets in JSON format"""
    return {"sheets": [{"id": id, "name": character_sheets[id]} for id in character_sheets]}

@route('/sheets/<id>', method='GET')
def get_sheet(id=""):
    """Return a specific sheet in JSON format"""
    if id:
        # fetch the character sheet
        if id not in character_sheets:
            print("Character sheet not found. Updating...")
            update_character_sheets()
            print("Found {0} character sheets.".format(len(character_sheets)))
        if id in character_sheets:
            # We need to wrap this into another object to prevent certain vulnerabilities
            return {"sheet": parse_sheet(id), "id": id}
    else:
        return get_listing()

@route('/', method='GET')
def get_root():
    """Serve the index.html"""
    return get_asset("/index.html")

@route('/<asset:path>', method='GET')
def get_asset(asset=""):
    """Serve assets located in the "assets" folder by redirecting all requests there"""
    try:
        return static_file(asset, "assets")
    except:
        abort(404, "Sorry, file not found")

def getline(fd):
    """Fetch a non-empty line from an (open) file"""
    line = fd.readline()
    while line == '\n' and line != '':
        line = fd.readline()
    return line

def update_character_sheets():
    """Look for character sheets in the 'data' folder"""
    global character_sheets
    dirlist = os.listdir('data')
    character_sheets = {}
    for cs in dirlist:
        with open('data/' + cs,'r') as fd:
            character_sheets[cs] = getline(fd).strip('# \n')

def parse_sheet(sheetname):
    char = {}
    with open("data/" + sheetname,'r') as fd:
        line = getline(fd)
        char["name"] = line.strip("# ")
        line = getline(fd)
        while line != '':
            header = line.strip("# \n")
            line = getline(fd)
            lines = []
            while not line.startswith('## ') and line != '':
                lines.append(line.strip('\n'))
                line = getline(fd)
            if len(lines) == 0:
                break
            parse_fn = get_func(header.lower(), "parse")
            char[header.lower()] = parse_fn(lines)
    return char

def get_func(module_name, func_name):
    try:
        print("::trying to find module", module_name)
        namespace = __import__("datahandlers." + module_name)
        module = getattr(namespace, module_name)
        print("::module found!")
        return getattr(module, func_name)
    except Exception:
        print("::could not find specific implementation -- using generic one", file=sys.stderr)
        return getattr(datahandlers.generic, func_name)

def capitalize_words(string):
    return ' '.join([s.capitalize() for s in string.split()])

if __name__ == "__main__":
    update_character_sheets()
    run(host='0.0.0.0', port=port)
