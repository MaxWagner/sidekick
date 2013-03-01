#!/usr/bin/env python

from urllib.parse import urlparse
from bottle import route, run, request, static_file, abort
import sys
import os
import datahandlers.generic
try:
    import ujson as json
except ImportError:
    import json

port = 8080
character_sheets = []
log_level = 2


@route('/sheets', method='GET')
def get_listing():
    """Return a listing of available character sheets in JSON format"""
    if log_level > 1:
        print("::Received request: GET /sheets")
    update_character_sheets()
    return {"sheets": [{"id": id, "name": character_sheets[id]} for id in character_sheets]}


@route('/sheets/<id>', method='GET')
def get_sheet(id=""):
    """Return a specific sheet in JSON format"""
    if log_level > 1:
        print("::Received request: GET /sheets/" + id)
    if id:
        # fetch the character sheet
        if id not in character_sheets:
            if log_level > 2:
                print(":::character sheet not found. Updating...")
            update_character_sheets()
            if log_level > 2:
                print(":::found {0} character sheets.".format(len(character_sheets)))
        if id in character_sheets:
            # We need to wrap this into another object to prevent certain vulnerabilities
            return {"sheet": parse_sheet(id), "id": id}
    else:
        return get_listing()


def _get_raw_data():
    """Get raw request data from bottle"""
    clen = request.content_length
    if clen > request.MEMFILE_MAX:
        abort(413, 'Request too large')
    if clen < 0:
        clen = request.MEMFILE_MAX + 1
    data = request.body.read(clen)
    if len(data) > request.MEMFILE_MAX: # Fail fast
        abort(413, 'Request too large')
    return data


@route('/sheets/<id>', method='PUT')
def put_sheet(id):
    """Parse and save a JSON object under the given id"""
    if id:
        if log_level > 1:
            print("::Received request: PUT /sheets/" + id)
        data = json.loads(_get_raw_data())
        if log_level > 2:
            print(":::received proper json data")
        if not data or data["id"] != id:
            abort(400, "Bad Request")
    dump_sheet(data)


@route('/sheets/<id>', method='DELETE')
def delete_sheet(id):
    """Delete a character sheet"""
    if log_level > 1:
        print("::Received request: DELETE /sheets/" + id)
    os.remove('data/' + id)
    del character_sheets[id]
    if log_level > 0:
        print(":sheet deleted:", id)


@route('/', method='GET')
def get_root():
    """Serve the index.html"""
    if log_level > 1:
        print("::Received request: GET /")
    return get_asset("/index.html")


@route('/<asset:path>', method='GET')
def get_asset(asset=""):
    """Serve assets located in the "assets" folder by redirecting all requests there"""
    if log_level > 1:
        print("::Received request: GET /" + asset)
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
        with open('data/' + cs, 'r') as fd:
            character_sheets[cs] = getline(fd).strip('# \n')


def parse_sheet(sheetname):
    char = {}
    try:
        with open("data/" + sheetname, 'r') as fd:
            line = getline(fd)
            char["name"] = line.strip("# \n")
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
    except IOError:
        if log_level > 0:
            print(":failed while trying to serve {0}. File not found.".format(sheetname))
        abort(404, "File not found")


def get_func(module_name, func_name):
    try:
        if log_level > 2:
            print(":::trying to find module", module_name)
        namespace = __import__("datahandlers." + module_name)
        module = getattr(namespace, module_name)
        if log_level > 2:
            print(":::module found!")
        return getattr(module, func_name)
    except ImportError or AttributeError:
        if log_level > 2:
            print(":::could not find specific implementation -- using generic one", file=sys.stderr)
        return getattr(datahandlers.generic, func_name)


def capitalize_words(string):
    """Capitalize a string word by word"""
    return ' '.join([s.capitalize() for s in string.split()])


def generate_sheet(data):
    sheet = data["sheet"]  # unwrap sheet
    sheet_text = ["# " + capitalize_words(sheet["name"]) + '\n\n']
    for key in sheet:
        if key != "name":
            sheet_text.append('## ' + capitalize_words(key) + '\n\n')
            gen_fn = get_func(key, "generate")
            sheet_text.append(gen_fn(sheet[key]) + '\n')
    return ''.join(sheet_text)


def dump_sheet(data):
    sheet_text = generate_sheet(data)
    if log_level > 2:
        print(":::sheet generated")
    with open("data/" + data["id"], 'w') as fd:
        fd.write(sheet_text)
        if log_level > 0:
            print(":file", data["id"], "successfully written")


if __name__ == "__main__":
    update_character_sheets()
    # since the default WSGI reference server is too slow when reading request data,
    # we're using the faster cherrypy server
    run(host='0.0.0.0', port=port, server='cherrypy')
