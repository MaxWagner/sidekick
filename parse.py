#!/usr/bin/env python

from urllib.parse import urlparse
import http.server
import json
import os
import generic

PORT = 8080
character_sheets = []

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path.split("/")[1:]
        # path is the requested file path, as list
        data = {}
        if path[0] == "sheets":
            # we're trying to find a character sheet
            if len(path) <= 1:
                # we serve the sheet selection page
                pass
            else:
                if path[1] not in character_sheets:
                    update_character_sheets()
                    print("found {0} character sheets".format(len(character_sheets)))
                if path[1] in character_sheets:
                    data = parse_sheet(path[1])
                else:
                    # 404
                    self.send_response(404)
                    self.end_headers()
                    return

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        d = data
        self.wfile.write(json.dumps(d).encode())
        return

def update_character_sheets():
    global character_sheets
    character_sheets = os.listdir('data')

def parse_sheet(sheetname):
    def getline(fd):
        line = fd.readline()
        while line == '\n' and line != '':
            line = fd.readline()
        return line
    char = {}
    with open(''.join(["data/",sheetname]),'r') as fd:
        line = getline(fd)
        char["Name"] = line.strip("# ")
        line = getline(fd)
        while line != '':
            header = line.strip("# ")
            line = getline(fd)
            lines = []
            while not line.startswith('## ') and line != '':
                lines.append(line)
                line = getline(fd)
            if len(lines) == 0:
                break
            try:
                module = __import__(header.lower())
                cl = getattr(module, header.lower())
            except Exception:
                print("could not find specific parser -- using generic one")
                cl = generic.parser
            char[header.lower()] = cl.parse(lines)
    return char

        
if __name__ == "__main__":
    update_character_sheets()
    try:
        server = http.server.HTTPServer(('',PORT),Handler)
        print("Server started on port", PORT)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down")
        server.socket.close()
