"""Experimental placeholders for future Bambu transport integrations."""

from __future__ import annotations


class DirectPrintTransport:
    """Boundary for future FTPS upload support."""

    def upload(self, package_path: str, remote_path: str) -> None:
        raise NotImplementedError("FTPS upload is intentionally not enabled in this stage.")
