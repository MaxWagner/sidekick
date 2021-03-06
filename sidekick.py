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
character_sheets = {}
# format of character_sheets {<system>:{<id>:<name>}}
log_level = 2


@route('/sheets', method='GET')
def get_listing():
    """Return a listing of available character sheets in JSON format"""
    if log_level > 1:
        print("::Received request: GET /sheets")
    update_character_sheets()
    res = []
    for system in character_sheets:
        for id in character_sheets[system]:
            res.append({"id": id, "name": character_sheets[system][id], "system": system})
    return {"sheets": res}


@route('/sheets/<system>/<id>', method='GET')
def get_sheet(system, id):
    """Return a specific sheet in JSON format"""
    if log_level > 1:
        print("::Received request: GET /sheets/" + system + '/' + id)
    if character_sheets[system]:
        # fetch the character sheet
        if id not in character_sheets[system]:
            if log_level > 2:
                print(":::character sheet not found. Updating...")
            update_character_sheets()
            if log_level > 2:
                print(":::found {0} directories.".format(len(character_sheets)))
        if id in character_sheets[system]:
            return parse_sheet(system, id)
    else:
        abort(404, "Character sheet not found")


def _get_raw_data():
    """Get raw request data from bottle"""
    clen = request.content_length
    if clen > request.MEMFILE_MAX:
        abort(413, 'Request too large')
    if clen < 0:
        clen = request.MEMFILE_MAX + 1
    data = request.body.read(clen)
    if len(data) > request.MEMFILE_MAX:
        abort(413, 'Request too large')
    return data


@route('/sheets/<system>/<id>', method='PUT')
def put_sheet(system, id):
    """Parse and save a JSON object under the given id"""
    if not os.path.exists('data/' + system):
        os.path.makedirs('data/' + system)
    if log_level > 1:
        print("::Received request: PUT /sheets/" + system + '/' + id)
    data = json.loads(_get_raw_data())
    if log_level > 2:
        print(":::received proper json data")
    if not data or data["id"] != id or data["system"] != system:
        abort(400, "Bad Request")
    dump_sheet(data)


@route('/sheets/<system>/<id>', method='DELETE')
def delete_sheet(system, id):
    """Delete a character sheet"""
    if log_level > 1:
        print("::Received request: DELETE /sheets/" + system + '/' + id)
    os.remove('data/' + system + '/' + id)
    del character_sheets[system][id[id.index('/'):]]
    if log_level > 0:
        print(":sheet deleted:", id)


@route('/', method='GET')
def get_root():
    """Serve the index.html"""
    if log_level > 1:
        print("::Received request: GET /")
    return get_asset("index.html")


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
    for system in dirlist:
        if os.path.isdir('data/' + system):
            character_sheets[system] = {}
            for cs in os.listdir('data/' + system):
                with open('data/' + system + '/' + cs, 'r') as fd:
                    character_sheets[system][cs] = getline(fd).strip('# \n')


def parse_sheet(system, sheetname):
    char = { "id": sheetname, "system": system, "categories": [] }
    try:
        with open("data/" + system + "/" + sheetname, 'r') as fd:
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
                parse_fn = get_func(system + '.' + header.lower(), "parse")
                char["categories"].append({ "id": header.lower(), "name": header, "data": parse_fn(lines) })
        return char
    except IOError:
        if log_level > 0:
            print(":failed while trying to serve {0}. File not found.".format(sheetname))
        abort(404, "File not found")


def get_func(module, func):
    """gets a named function from one of the extension modules.
    It always returns the most specific one, but supports at most
    2 indirections in the module name (e.g. datahandlers.gurps.skills)"""
    if log_level > 2:
        print(":::trying to find module datahandlers." + module)
    prefs = ["datahandlers"] + module.split('.')
    try:
        mod = __import__(prefs[0] + '.' + prefs[1] + '.' + prefs[2])
        mod = getattr(mod, prefs[1])
        mod = getattr(mod, prefs[2])
        func = getattr(mod, func)
        if log_level > 2:
            print(":::found applicable system-specific implementation")
        return func
    except (ImportError, AttributeError):
        try:
            # try a general implementation
            mod = __import__(prefs[0] + '.' + prefs[2])
            mod = getattr(mod, prefs[2])
            func = getattr(mod, func)
            if log_level > 2:
                print(":::found applicable general implementation")
            return func
        except (ImportError, AttributeError):
            if log_level > 2:
                print(":::could not find specific implementation; using fallback",
                      file=sys.stderr)
            return getattr(datahandlers.generic, func)


def generate_sheet(sheet):
    sheet_text = ["# " + sheet["name"] + '\n\n']
    for cat in sheet["categories"]:
        sheet_text.append('## ' + cat["name"] + '\n\n')
        gen_fn = get_func(sheet["system"] + '.' + cat["id"], "generate")
        sheet_text.append(gen_fn(cat["data"]) + '\n')
    return ''.join(sheet_text)


def dump_sheet(data):
    sheet_text = generate_sheet(data)
    if log_level > 2:
        print(":::sheet generated")
    if not os.path.isdir("data/" + data["system"]):
        os.path.makedirs("data/" + data["system"])
    with open("data/" + data["system"] + '/' + data["id"], 'w') as fd:
        fd.write(sheet_text)
        if log_level > 0:
            print(":file", data["id"], "successfully written")


if __name__ == "__main__":
    update_character_sheets()
    # since the default WSGI reference server is too slow when reading request data,
    # we're using the faster cherrypy server
    if len(sys.argv) > 1 and len(sys.argv[1]) > 9 and sys.argv[1].startswith("--server="):
        run(host='0.0.0.0', port=port, server=sys.argv[1][9:])
    else:
        run(host='0.0.0.0', port=port)
