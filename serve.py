#!/usr/bin/env python3
"""Local dev server with SPA routing for clean article URLs."""
import http.server
import os

PORT = 8000
DIR = os.path.dirname(os.path.abspath(__file__))

KNOWN_FILES = set()
for f in os.listdir(DIR):
    if os.path.isfile(os.path.join(DIR, f)):
        KNOWN_FILES.add(f)


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_GET(self):
        path = self.path.split("?")[0].strip("/")
        # If path has no dot and isn't a known file → serve artikel.html
        if path and "." not in path and path not in KNOWN_FILES:
            self.path = "/artikel.html"
        return super().do_GET()


print(f"Serving at http://localhost:{PORT}")
http.server.HTTPServer(("", PORT), SPAHandler).serve_forever()
