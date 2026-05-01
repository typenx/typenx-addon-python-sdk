from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .addon import TypenxAddon


def serve_typenx_addon(addon: TypenxAddon, *, host: str = "127.0.0.1", port: int | None = None) -> ThreadingHTTPServer:
    port = port if port is not None else int(os.environ.get("PORT", "8787"))

    class AddonRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self._handle()

        def do_POST(self) -> None:
            self._handle()

        def log_message(self, format: str, *args: object) -> None:
            return

        def _handle(self) -> None:
            body_length = int(self.headers.get("content-length", "0") or "0")
            body = self.rfile.read(body_length) if body_length else b""
            response = addon.handle(self.command, self.path, body)

            self.send_response(response.status)
            for key, value in (response.headers or {}).items():
                self.send_header(key, value)
            self.send_header("content-length", str(len(response.body)))
            self.end_headers()
            self.wfile.write(response.body)

    server = ThreadingHTTPServer((host, port), AddonRequestHandler)
    print(f"Typenx addon listening on http://{host}:{port}")
    server.serve_forever()
    return server
