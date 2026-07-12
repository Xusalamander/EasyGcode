"""Dependency-light web frontend for EasyGcode."""

from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .bambu import PrintService, list_profiles
from .core import DesignSpec, generate_gcode, list_templates
from .jobs import PrintJob

_FRONTEND_DIR = Path(__file__).with_name("frontend")


class EasyGcodeRequestHandler(SimpleHTTPRequestHandler):
    """Serve static UI assets and a tiny JSON API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(_FRONTEND_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/api/templates":
            self._send_json([_dump_model(template) for template in list_templates()])
            return
        if self.path == "/api/printers":
            self._send_json([_dump_model(profile) for profile in list_profiles()])
            return
        if self.path == "/health":
            self._send_json({"status": "ok"})
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        try:
            payload = json.loads(
                self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}"
            )
            if self.path == "/api/gcode":
                result = generate_gcode(DesignSpec(**payload))
            elif self.path == "/api/print-jobs/prepare":
                result = PrintService().prepare(PrintJob(**payload))
            else:
                self.send_error(404, "Not found")
                return
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json(_dump_model(result))

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _dump_model(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def run(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Run the local EasyGcode web app."""

    server = ThreadingHTTPServer((host, port), EasyGcodeRequestHandler)
    print(f"EasyGcode frontend running at http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EasyGcode web frontend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
