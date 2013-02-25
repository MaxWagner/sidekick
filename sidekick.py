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
    return {"sheets": [{"id": id, "name": character_sheets[id]} for id in character_sheets]}

@route('/sheets/<id>', method='GET')
def get_sheet(id=""):
    """Return a listing of available character sheets or, if requested, a specific sheet in JSON format"""
    if id:
        # fetch the character sheet
        if id not in character_sheets:
            print("Character sheet not found. Updating...")
            update_character_sheets()
            print("Found {0} character sheets.".format(len(character_sheets)))
        if id in character_sheets:
            return {id: parse_sheet(id)}
    else:
        return get_listing()

@route('/', method='GET')
def get_root():
    return get_asset("/index.html")

@route('/<asset>', method='GET')
def get_asset(asset=""):
    try:
        return static_file(asset, "assets")
    except:
        print("WDKHDLK")
        abort(404, "Sorry, file not found")

def getline(fd):
    line = fd.readline()
    while line == '\n' and line != '':
        line = fd.readline()
    return line

def update_character_sheets():
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
            try:
                print("::trying to find module",header.lower())
                namespace = __import__("datahandlers." + header.lower())
                module = getattr(namespace,header.lower())
                print("::module found!")
                parse_fn = module.parse
            except Exception:
                print("could not find specific parser -- using generic one", file=sys.stderr)
                parse_fn = datahandlers.generic.parse
            char[header.lower()] = parse_fn(lines)
    return char

        
if __name__ == "__main__":
    update_character_sheets()
    run(host='localhost', port=port)
