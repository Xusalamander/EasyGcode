"""Experimental placeholders for future Bambu MQTT integrations."""

from __future__ import annotations


class BambuMqttClient:
    """Boundary for future remote start/status support."""

    def start_print(self, remote_path: str) -> None:
        raise NotImplementedError("MQTT remote start is intentionally not enabled in this stage.")
