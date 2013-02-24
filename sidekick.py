#!/usr/bin/env python

from urllib.parse import urlparse
import http.server
import json
import sys
import os
import datahandlers.generic

port = 8080
character_sheets = []

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/").split("/")[1:]
        # path is the requested file path, as list
        data = {}
        if path and path[0] == "sheets":
            # we're trying to find a character sheet
            if len(path) <= 1:
                data = character_sheets
                # we serve the sheet selection page
            else:
                if path[1] not in character_sheets:
                    update_character_sheets()
                    print("found {0} character sheets".format(len(character_sheets)))
                if path[1] in character_sheets:
                    data = parse_sheet(path[1])
                else:
                    # 404, I hope super() knows what to do
                    return super().do_GET()
        else:
            self.path = "/assets" + self.path
            # obviously looking for something else entirely
            return super().do_GET()
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
        return


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
    try:
        server = http.server.HTTPServer(('',port),Handler)
        print("Server started on port", port)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down")
        server.socket.close()
